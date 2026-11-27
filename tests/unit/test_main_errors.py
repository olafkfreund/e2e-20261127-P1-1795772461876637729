# AC#3: main returns 2 with non-empty stderr on invalid arguments or missing files.

import pytest

from wordfreq.cli import main


@pytest.mark.parametrize(
    "argv",
    [
        ["--min-len", "0"],
        ["--top", "-1"],
        ["--top", "abc"],
        ["--min-len", "xyz"],
    ],
    ids=["min_len_zero", "top_negative", "top_non_int", "min_len_non_int"],
)
def test_main_invalid_argument_returns_2_with_stderr(argv, capsys):
    exit_code = main(argv)
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err.strip() != ""


def test_main_missing_file_returns_2_with_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    exit_code = main([str(missing)])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err.strip() != ""
