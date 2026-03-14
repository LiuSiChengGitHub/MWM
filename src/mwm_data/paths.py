from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

DATA_ROOT_ENV = "MWM_DATA_ROOT"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _candidate_paths(explicit: str | Path | None = None) -> Iterable[Path]:
    if explicit:
        yield Path(explicit)

    env_value = os.environ.get(DATA_ROOT_ENV)
    if env_value:
        yield Path(env_value)

    repo_root = _repo_root()
    cwd = Path.cwd().resolve()

    yield repo_root.parent / "datasets_MWM"
    yield cwd / "datasets_MWM"
    yield cwd.parent / "datasets_MWM"
    yield Path(r"D:\Base\CodingSpace\datasets_MWM")


def resolve_data_root(explicit: str | Path | None = None) -> Path:
    checked: list[str] = []

    for candidate in _candidate_paths(explicit):
        candidate = candidate.expanduser()
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate

        normalized = str(resolved)
        if normalized in checked:
            continue
        checked.append(normalized)

        if resolved.exists():
            return resolved

    checked_text = "\n- ".join(checked)
    raise FileNotFoundError(
        "Could not find the MIMIC-IV dataset root. Checked:\n- " + checked_text +
        f"\nYou can also set {DATA_ROOT_ENV} to the dataset directory."
    )
