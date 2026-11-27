"""Command-line entry point and word frequency helpers for wordfreq."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")


def count_words(
    text: str,
    *,
    min_len: int = 1,
    ignore_case: bool = True,
    top: int | None = None,
) -> list[tuple[str, int]]:
    """Count word occurrences in *text* and return `(word, count)` pairs."""
    if min_len < 1:
        msg = "min_len must be >= 1"
        raise ValueError(msg)
    if top is not None and top < 0:
        msg = "top must be >= 0"
        raise ValueError(msg)

    tokens = _TOKEN_PATTERN.findall(text)
    if ignore_case:
        tokens = [token.lower() for token in tokens]
    counts = Counter(token for token in tokens if len(token) >= min_len)
    rows = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    if top is not None:
        rows = rows[:top]
    return rows


def format_table(rows: Sequence[tuple[str, int]]) -> str:
    """Format `(word, count)` pairs as tab-separated lines."""
    return "\n".join(f"{word}\t{count}" for word, count in rows)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wordfreq",
        description="Deterministically count and rank words in text.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="-",
        help="input file (UTF-8); reads stdin when omitted or '-'",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="only show the N most frequent words (default: all)",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=1,
        metavar="M",
        help="ignore words shorter than M characters (default: 1)",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="preserve token case instead of lowercasing",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help='emit a JSON array of {"word", "count"} objects',
    )
    return parser


def _read_input(path: str) -> str:
    if path == "-":
        stream = sys.stdin
        buffer = getattr(stream, "buffer", None)
        if buffer is not None:
            return buffer.read().decode("utf-8")
        return stream.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the wordfreq CLI and return the process exit code."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    try:
        text = _read_input(args.path)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"wordfreq: error: cannot read {args.path!r}: {exc}", file=sys.stderr)
        return 2

    try:
        rows = count_words(
            text,
            min_len=args.min_len,
            ignore_case=not args.case_sensitive,
            top=args.top,
        )
    except ValueError as exc:
        print(f"wordfreq: error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        payload = [{"word": word, "count": count} for word, count in rows]
        print(json.dumps(payload))
    elif rows:
        print(format_table(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
