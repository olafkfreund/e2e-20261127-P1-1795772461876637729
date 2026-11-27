# AC#1: count_words raises ValueError on min_len < 1 or top < 0.
# Concretely: ValueError('min_len must be >= 1') for min_len < 1,
# ValueError('top must be >= 0') for top < 0, and top is honored.

import pytest

from wordfreq.cli import count_words


SAMPLE_TEXT = "alpha beta gamma delta"


@pytest.mark.parametrize(
    "min_len",
    [0, -1, -5],
    ids=["min_len_zero", "min_len_minus_one", "min_len_minus_five"],
)
def test_count_words_min_len_below_one_raises_value_error(min_len):
    with pytest.raises(ValueError, match="min_len must be >= 1"):
        count_words(SAMPLE_TEXT, min_len=min_len)


@pytest.mark.parametrize(
    "top",
    [-1, -10],
    ids=["top_minus_one", "top_minus_ten"],
)
def test_count_words_top_below_zero_raises_value_error(top):
    with pytest.raises(ValueError, match="top must be >= 0"):
        count_words(SAMPLE_TEXT, top=top)


def test_count_words_top_two_returns_two_entries():
    result = count_words(SAMPLE_TEXT, top=2)
    assert len(result) == 2
