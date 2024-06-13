import bz2
import networkx as nx
import numpy as np
import os
import time

from typing import Tuple

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


start = time.perf_counter()
with bz2.open(INDEX, 'rt', encoding='utf-8') as f:
    indices = f.readlines()
end = time.perf_counter()
print(f'Loaded {len(indices)} indices in {end - start:.2f} seconds.')
