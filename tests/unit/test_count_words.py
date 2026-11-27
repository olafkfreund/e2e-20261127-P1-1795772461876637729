# AC#1: count_words extracts tokens, lowercases by default, ignore_case=False,
# min_len filter, sorts by (-count, word).
#
# Tokens are runs of [A-Za-z0-9]+. Lowercasing is the default. With
# ignore_case=False the case is preserved. min_len drops shorter tokens.
# Output is sorted by (-count, word).

import pytest

from wordfreq.cli import count_words


def test_count_words_extracts_alnum_tokens_only_returns_expected_counts():
    text = "hello, world! 42 foo_bar"
    result = count_words(text)
    assert dict(result) == {"hello": 1, "world": 1, "42": 1, "foo": 1, "bar": 1}


def test_count_words_default_lowercases_tokens_returns_single_lowercase_entry():
    result = count_words("Hello HELLO hello")
    assert result == [("hello", 3)]


def test_count_words_ignore_case_false_preserves_case_returns_distinct_entries():
    result = count_words("Hello HELLO hello", ignore_case=False)
    assert dict(result) == {"Hello": 1, "HELLO": 1, "hello": 1}


@pytest.mark.parametrize(
    "min_len,expected",
    [
        (1, {"a": 1, "bb": 1, "ccc": 1, "dddd": 1}),
        (2, {"bb": 1, "ccc": 1, "dddd": 1}),
        (3, {"ccc": 1, "dddd": 1}),
        (5, {}),
    ],
    ids=["min_len_1_keeps_all", "min_len_2_drops_single_char", "min_len_3_drops_short", "min_len_5_drops_all"],
)
def test_count_words_min_len_filter_drops_short_tokens(min_len, expected):
    result = count_words("a bb ccc dddd", min_len=min_len)
    assert dict(result) == expected


def test_count_words_sorts_by_descending_count_returns_most_frequent_first():
    result = count_words("b a b c c c a")
    assert result == [("c", 3), ("a", 2), ("b", 2)]


def test_count_words_breaks_count_ties_alphabetically_returns_word_ascending():
    result = count_words("zeta alpha")
    assert result == [("alpha", 1), ("zeta", 1)]
