# AC#2: format_table formats rows as word\tcount lines separated by \n and returns '' for empty input.
import pytest

from wordfreq.cli import format_table


def test_format_table_two_rows_joined_by_newline_with_tab_separator():
    rows = [("the", 3), ("cat", 1)]

    assert format_table(rows) == "the\t3\ncat\t1"


def test_format_table_no_trailing_newline_after_last_row():
    rows = [("the", 3), ("cat", 1)]

    assert not format_table(rows).endswith("\n")


def test_format_table_empty_input_returns_empty_string():
    assert format_table([]) == ""


@pytest.mark.parametrize(
    "rows,expected",
    [
        ([("alpha", 10)], "alpha\t10"),
        ([("a", 1), ("b", 2), ("c", 3)], "a\t1\nb\t2\nc\t3"),
    ],
    ids=["single_row", "three_rows_in_order"],
)
def test_format_table_rows_rendered_as_word_tab_count(rows, expected):
    assert format_table(rows) == expected
