from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mwm_data.paths import resolve_data_root
from mwm_data.preview import CORE_TABLES, get_table_path, read_preview


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview core MIMIC-IV tables.")
    parser.add_argument(
        "--tables",
        nargs="+",
        default=["patients", "admissions", "icustays", "edstays"],
        help="Table names to preview.",
    )
    parser.add_argument(
        "--nrows",
        type=int,
        default=5,
        help="Number of rows to load from each table.",
    )
    parser.add_argument(
        "--data-root",
        type=str,
        default=None,
        help="Optional explicit dataset root. If omitted, the script will auto-detect it.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Only list the available core tables and exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_root = resolve_data_root(args.data_root)

    print(f"Dataset root: {data_root}")
    print()
    print("Available core tables:")
    for name in sorted(CORE_TABLES):
        print(f"- {name}")

    if args.list:
        return

    for table_name in args.tables:
        path = get_table_path(data_root, table_name)
        df = read_preview(data_root, table_name, nrows=args.nrows)

        print("\n" + "=" * 80)
        print(f"TABLE: {table_name}")
        print(f"FILE:  {path}")
        print(f"COLUMNS ({len(df.columns)}): {df.columns.tolist()}")
        print("PREVIEW:")
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
