import bz2

from .context import etysim

from etysim.article_parsing import (split_index, get_article,
                                    get_language_sections,
                                    get_tags_from_section, INDEX)
import pytest


def read_index() -> str:
    index: str = ""
    with bz2.open(INDEX, 'rt', encoding='utf-8') as f:
        for _ in range(10):
            index = f.readline().strip()
    return index


def test_split_index() -> None:
    with pytest.raises(ValueError):
        split_index('foo:100:baz')
    with pytest.raises(ValueError):
        split_index('100:bar:baz')
    with pytest.raises(ValueError):
        split_index('test')
    assert split_index('5:10:baz') == (5, 10, 'baz')


def test_get_article() -> None:
    with pytest.raises(OSError):
        get_article('5:10:baz')
    with pytest.raises(OSError):
        get_article('-1:-1:baz')
    with pytest.raises(EOFError):
        get_article('0:0:baz')
    index = read_index()
    article = get_article(index)
    assert article.startswith('<page>')
    assert len(article) > 1000


def test_get_language_sections() -> None:
    index = read_index()
    sections = get_language_sections(index)
    assert len(sections) > 0
    assert all(section.startswith('==') for section in sections)


def test_get_tags_from_section() -> None:
    # get_tags_from_section doesn't take an index string, instead a subset of
    # an article
    example_article = """
    ==English==
    This is the English section.

    ===Noun===
    yes

    ====Synonyms====
    no

    =====Translations=====
    maybe
    """
    expect = [('Noun', 'yes'), ('Synonyms', 'no'), ('Translations', 'maybe')]
    assert (get_tags_from_section(example_article) == expect)
    example_article += """
    ===Verb===

    ====Synonyms====
    The above is purposefully empty

    [[Category:English lemmas]]
    """
    expect.append(('Synonyms', 'The above is purposefully empty'))
    assert (get_tags_from_section(example_article) == expect)
    index = read_index()
    sections = get_language_sections(index)
    for section in sections:
        tags = get_tags_from_section(section)
        assert all(tag[0] for tag in tags)
        assert all(tag[1] for tag in tags)
