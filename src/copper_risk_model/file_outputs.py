"""Helpers for deterministic text-based analytical outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_text_output(path: str | Path, contents: str) -> Path:
    """Write a UTF-8 text file with LF newlines across platforms."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(contents)
    return output_path


def write_json_output(path: str | Path, payload: Any, *, indent: int = 2) -> Path:
    """Write a JSON file with deterministic formatting and LF newlines."""

    return write_text_output(path, json.dumps(payload, indent=indent))


def write_csv_output(frame: pd.DataFrame, path: str | Path, *, index: bool = False) -> Path:
    """Write a CSV file with UTF-8 encoding and LF newlines across platforms."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=index, encoding="utf-8", lineterminator="\n")
    return output_path
