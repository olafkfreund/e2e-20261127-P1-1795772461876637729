# AC#4: pytest -q passes across tests/test_wordfreq.py.
# Subtask: an end-to-end tie-breaking and JSON round-trip scenario through
# wordfreq.cli.main must hold (sort by (-count, word); --json output ends with "\n").
import io
import json
import sys

import pytest

from wordfreq.cli import main


@pytest.fixture
def tie_input_file(tmp_path):
    path = tmp_path / "ties.txt"
    # a:2, b:2, c:1 -> ties on count resolved by word ascending.
    path.write_text("b a c b a\n", encoding="utf-8")
    return path


def test_main_tie_breaking_tsv_orders_by_count_then_word(tie_input_file, capsys):
    exit_code = main([str(tie_input_file)])
    out = capsys.readouterr().out
    assert out == "a\t2\nb\t2\nc\t1\n"
    assert exit_code == 0


def test_main_tie_breaking_tsv_returns_zero(tie_input_file, capsys):
    exit_code = main([str(tie_input_file)])
    assert exit_code == 0


def test_main_json_output_ends_with_newline(tie_input_file, capsys):
    main([str(tie_input_file), "--json"])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_json_output_parses_as_json(tie_input_file, capsys):
    main([str(tie_input_file), "--json"])
    out = capsys.readouterr().out
    assert json.loads(out) is not None


def test_main_json_round_trip_preserves_tie_order(tie_input_file, capsys):
    main([str(tie_input_file), "--json"])
    out = capsys.readouterr().out
    reloaded = json.loads(json.dumps(json.loads(out)))
    redumped = json.dumps(reloaded)
    assert redumped.index('"a"') < redumped.index('"b"') < redumped.index('"c"')


def test_main_json_round_trip_is_stable_across_runs(tie_input_file, capsys):
    main([str(tie_input_file), "--json"])
    first = capsys.readouterr().out
    main([str(tie_input_file), "--json"])
    second = capsys.readouterr().out
    assert json.loads(first) == json.loads(second)


def test_main_stdin_tie_breaking_matches_path_input(tie_input_file, capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("b a c b a\n"))
    exit_code = main([])
    out = capsys.readouterr().out
    assert out == "a\t2\nb\t2\nc\t1\n"
    assert exit_code == 0


def test_main_case_sensitive_keeps_distinct_tokens_sorted(tmp_path, capsys):
    path = tmp_path / "case.txt"
    path.write_text("A a\n", encoding="utf-8")
    exit_code = main([str(path), "--case-sensitive"])
    out = capsys.readouterr().out
    assert out == "A\t1\na\t1\n"
    assert exit_code == 0


def test_main_empty_tsv_output_prints_nothing(tmp_path, capsys):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    exit_code = main([str(path)])
    out = capsys.readouterr().out
    assert out == ""
    assert exit_code == 0


def test_main_missing_file_returns_exit_code_2(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    exit_code = main([str(missing)])
    assert exit_code == 2


def test_main_missing_file_writes_stderr(tmp_path, capsys):
    missing = tmp_path / "does_not_exist.txt"
    main([str(missing)])
    err = capsys.readouterr().err
    assert err != ""
