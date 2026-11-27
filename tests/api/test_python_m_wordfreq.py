# Criterion (AC#3, from rationale): main and `python -m wordfreq` read from
# sys.stdin by default; exit 0 or 2.
# Subtask description: Verify running `python -m wordfreq` as a subprocess reads
# stdin, outputs TSV/JSON with trailing newline, and exits 2 with stderr on a
# missing file.

import subprocess
import sys

import pytest


TIMEOUT_SECONDS = 30
STDIN_TEXT = "the cat and the dog\n"


def _run_module(args=None, stdin_text=None):
    """Run `python -m wordfreq` as a subprocess and capture its output."""
    cmd = [sys.executable, "-m", "wordfreq"]
    if args:
        cmd.extend(args)
    return subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
    )


@pytest.fixture
def stdin_result():
    """Run the module with text piped to stdin and no file argument."""
    return _run_module(stdin_text=STDIN_TEXT)


@pytest.fixture
def missing_file_result(tmp_path):
    """Run the module with a path to a file that does not exist."""
    missing = tmp_path / "does_not_exist.txt"
    assert not missing.exists()
    return _run_module(args=[str(missing)], stdin_text="")


def test_python_m_wordfreq_stdin_input_exit_code_zero(stdin_result):
    assert stdin_result.returncode == 0


def test_python_m_wordfreq_stdin_input_stdout_nonempty(stdin_result):
    assert stdin_result.stdout.strip() != ""


def test_python_m_wordfreq_stdin_input_stdout_ends_with_newline(stdin_result):
    assert stdin_result.stdout.endswith("\n")


def test_python_m_wordfreq_missing_file_exit_code_two(missing_file_result):
    assert missing_file_result.returncode == 2


def test_python_m_wordfreq_missing_file_stderr_nonempty(missing_file_result):
    assert missing_file_result.stderr.strip() != ""
