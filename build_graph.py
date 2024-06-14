import bz2
import networkx as nx
import numpy as np
import os
import time
import re

from typing import Tuple, List

INDEX = 'dumps/enwiktionary-latest-pages-articles-multistream-index.txt.bz2'
ARTICLES = 'dumps/enwiktionary-latest-pages-articles-multistream.xml.bz2'


def split_index(index_string: str) -> Tuple[int, int, str]:
    """
    Split an index string into its components.

    Parameters
    ----------
    index_string : str
        A string containing the byte offset, article ID, and title of an article.

    Returns
    -------
    Tuple[int, int, str]
        A tuple containing the byte offset, article ID, and title of the article.
    """
    parts = index_string.split(':')
    byte_offset = int(parts[0])
    article_id = int(parts[1])
    title = parts[2].strip()
    return byte_offset, article_id, title


def get_article(index_string: str) -> str:
    """
    Retrieve the content of an article given its index string.

    Parameters
    ----------
    index_string : str
        A string containing the byte offset, article ID, and title of an article.

    Returns
    -------
    str
        The content of the article, unprocessed.
    """
    decompressor = bz2.BZ2Decompressor()
    byte_offset, _, title = split_index(index_string)

    with open(ARTICLES, 'rb') as f:
        f.seek(byte_offset)
        decompressed_data = b''

        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            decompressed_data += decompressor.decompress(chunk)
            if b'</page>' in decompressed_data:
                break

    # Convert bytes to string after decompression
    article = decompressed_data.decode('utf-8')

    # Extract the specific article content from the decompressed data
    end_tag = f'</page>'
    start_index = article.find(f'<title>{title}</title>')
    end_index = article.find(end_tag, start_index) + len(end_tag)

    if start_index != -1 and end_index != -1:
        # back up a bit for start_index to include the stuff before the title,
        # which is 11 characters (len('<page>') + 4 spaces + 1 newline)
        return article[start_index - 11:end_index]
    else:
        return "Article not found or incomplete."


# sections are split up by language, as e.g. ==Chinese== or ==English==
def get_language_sections(article: str) -> List[str]:
    """
    Split an article into its language sections.

    Parameters
    ----------
    article : str
        The content of the article.

    Returns
    -------
    List[str]
        A list of strings, each containing the content of a language section.
    """
    language_sections = re.split(r'(?===[A-Za-z]+==\n)', article)
    return [i for i in language_sections if i.strip().startswith('==')]


TAGS = re.compile(
    r'(={3,}([^\n=]*)=+)(.*?)(?=(={3,}|(\[\[Category.*\]\])|\Z))', re.DOTALL)


def get_tags_from_section(language_section: str) -> List[Tuple[str, str]]:
    """
    Get all sub-sections and their content from a language section. For
    example, might return `[('Etymology', '...'), ('Pronunciation', '...')]`


    Parameters
    ----------
    language_section : str
        The content of a language section.

    Returns
    -------
    List[Tuple[str, str]]
        A list of tuples, each containing the title of a sub-section and 
        its content.
    """
    tag_splits = TAGS.findall(language_section)
    tag_splits = [(i[1], i[2].strip()) for i in tag_splits
                  if i[2].strip() != '']
    for i in tag_splits:
        print(i)
    return tag_splits


start = time.perf_counter()
with bz2.open(INDEX, 'rt', encoding='utf-8') as f:
    indices = f.readlines()
end = time.perf_counter()
print(f'Loaded {len(indices)} indices in {end - start:.2f} seconds.')
