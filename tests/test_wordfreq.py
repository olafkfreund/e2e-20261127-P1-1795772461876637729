"""Unit and CLI tests for the wordfreq package."""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_sample(tmp_path: Path, text: str) -> str:
    sample = tmp_path / "sample.txt"
    sample.write_text(text, encoding="utf-8")
    return str(sample)


def _run_module(*args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        cwd=REPO_ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_count_words_ties_are_sorted_alphabetically() -> None:
    assert count_words("zebra mango apple mango zebra apple") == [
        ("apple", 2),
        ("mango", 2),
        ("zebra", 2),
    ]


def test_count_words_tie_order_ignores_first_appearance() -> None:
    assert count_words("c b a") == [("a", 1), ("b", 1), ("c", 1)]
    assert count_words("b a a b c") == [("a", 2), ("b", 2), ("c", 1)]


def test_count_words_ignore_case_lowercases_by_default() -> None:
    assert count_words("Apple APPLE apple") == [("apple", 3)]


def test_count_words_case_sensitive_keeps_token_case() -> None:
    assert count_words("Apple apple APPLE", ignore_case=False) == [
        ("APPLE", 1),
        ("Apple", 1),
        ("apple", 1),
    ]


def test_count_words_tokens_are_ascii_alphanumeric() -> None:
    assert count_words("well-known don't 42 42 x_y") == [
        ("42", 2),
        ("don", 1),
        ("known", 1),
        ("t", 1),
        ("well", 1),
        ("x", 1),
        ("y", 1),
    ]


def test_count_words_min_len_filters_short_tokens() -> None:
    assert count_words("a an the at a", min_len=2) == [
        ("an", 1),
        ("at", 1),
        ("the", 1),
    ]


def test_count_words_top_zero_returns_empty() -> None:
    assert count_words("apple banana", top=0) == []


def test_count_words_rejects_min_len_below_one() -> None:
    with pytest.raises(ValueError, match="min_len must be >= 1"):
        count_words("apple", min_len=0)


def test_count_words_rejects_negative_top() -> None:
    with pytest.raises(ValueError, match="top must be >= 0"):
        count_words("apple", top=-1)


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_format_table_empty_returns_empty_string() -> None:
    assert format_table([]) == ""


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


def test_cli_case_sensitive_preserves_case(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _write_sample(tmp_path, "Apple apple apple\n")
    rc = main([path, "--case-sensitive"])
    assert rc == 0
    assert capsys.readouterr().out == "apple\t2\nApple\t1\n"


def test_cli_reads_stdin_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple banana\n"))
    rc = main([])
    assert rc == 0
    assert capsys.readouterr().out == "apple\t2\nbanana\t1\n"


def test_cli_reads_stdin_when_path_is_dash(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple banana\n"))
    rc = main(["-"])
    assert rc == 0
    assert capsys.readouterr().out == "apple\t2\nbanana\t1\n"


def test_cli_reads_utf8_stdin_through_buffer(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    raw = io.BytesIO(b"beta alpha beta\n")
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(raw, encoding="utf-8"))
    rc = main([])
    assert rc == 0
    assert capsys.readouterr().out == "beta\t2\nalpha\t1\n"


def test_cli_tsv_output_ends_with_single_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _write_sample(tmp_path, "apple apple banana\n")
    rc = main([path])
    assert rc == 0
    assert capsys.readouterr().out == "apple\t2\nbanana\t1\n"


def test_cli_tsv_empty_output_prints_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _write_sample(tmp_path, "!!! ...\n")
    rc = main([path])
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_cli_json_output_ends_with_single_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _write_sample(tmp_path, "apple apple banana\n")
    rc = main([path, "--json"])
    assert rc == 0
    assert capsys.readouterr().out == (
        '[{"word": "apple", "count": 2}, {"word": "banana", "count": 1}]\n'
    )


def test_cli_json_empty_output_is_empty_array(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _write_sample(tmp_path, "!!!\n")
    rc = main([path, "--json"])
    assert rc == 0
    assert capsys.readouterr().out == "[]\n"


def test_cli_top_zero_prints_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _write_sample(tmp_path, "apple banana\n")
    rc = main([path, "--top", "0"])
    assert rc == 0
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    ("option", "message"),
    [
        (["--min-len", "0"], "min_len must be >= 1"),
        (["--top", "-1"], "top must be >= 0"),
    ],
)
def test_cli_rejects_out_of_range_values(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    option: list[str],
    message: str,
) -> None:
    path = _write_sample(tmp_path, "apple banana\n")
    rc = main([path, *option])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert message in captured.err


@pytest.mark.parametrize(
    "option",
    [
        ["--top", "abc"],
        ["--min-len", "x"],
        ["--no-such-flag"],
    ],
)
def test_cli_rejects_unparseable_arguments(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    option: list[str],
) -> None:
    path = _write_sample(tmp_path, "apple banana\n")
    rc = main([path, *option])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert captured.err != ""


def test_cli_missing_file_exits_with_code_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing.txt"
    rc = main([str(missing)])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert "missing.txt" in captured.err


def test_python_m_wordfreq_reads_stdin() -> None:
    result = _run_module(stdin="apple apple banana\n")
    assert result.returncode == 0
    assert result.stdout == "apple\t2\nbanana\t1\n"
    assert result.stderr == ""


def test_python_m_wordfreq_reads_file_as_json(tmp_path: Path) -> None:
    path = _write_sample(tmp_path, "Apple apple\n")
    result = _run_module(path, "--json")
    assert result.returncode == 0
    assert result.stdout == '[{"word": "apple", "count": 2}]\n'
    assert result.stderr == ""


def test_python_m_wordfreq_missing_file_exits_with_code_2(tmp_path: Path) -> None:
    result = _run_module(str(tmp_path / "missing.txt"))
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr != ""


def test_python_m_wordfreq_invalid_argument_exits_with_code_2() -> None:
    result = _run_module("--min-len", "0", stdin="apple\n")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "min_len must be >= 1" in result.stderr
