# Criterion: Verify main(argv) reads stdin by default, honors --top/--min-len/--case-sensitive/--json,
# returns 0 and ends non-empty output with a newline.

import io
import json
import sys

from wordfreq.cli import main

SAMPLE_TEXT = "apple apple banana\n"


def test_main_default_reads_stdin_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_TEXT))
    result = main([])
    assert result == 0


def test_main_default_output_ends_with_newline(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_TEXT))
    main([])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_default_output_is_non_empty(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_TEXT))
    main([])
    out = capsys.readouterr().out
    assert len(out) > 0


def test_main_top_flag_limits_output_to_one_line(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_TEXT))
    main(["--top", "1"])
    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if line.strip()]
    assert len(lines) == 1


def test_main_top_flag_output_ends_with_newline(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_TEXT))
    main(["--top", "1"])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_min_len_flag_excludes_short_word(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a a bb bb ccc\n"))
    main(["--min-len", "2"])
    out = capsys.readouterr().out
    assert "a" not in out.split()


def test_main_min_len_flag_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a a bb bb ccc\n"))
    result = main(["--min-len", "2"])
    assert result == 0


def test_main_case_sensitive_flag_keeps_case_variants_separate(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple\n"))
    main(["--case-sensitive"])
    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if line.strip()]
    assert len(lines) == 2


def test_main_case_sensitive_flag_output_ends_with_newline(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("Apple apple\n"))
    main(["--case-sensitive"])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_json_flag_output_parses_as_json(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_TEXT))
    main(["--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, (dict, list))


def test_main_json_flag_output_ends_with_newline(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_TEXT))
    main(["--json"])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_json_flag_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_TEXT))
    result = main(["--json"])
    assert result == 0
