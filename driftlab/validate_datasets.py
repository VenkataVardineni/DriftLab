"""Validate reference/current datasets against schema config (no drift run)."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from driftlab.config_loader import load_config
from driftlab.io.load import load_dataframe
from driftlab.io.schema import Schema


def validate_pair(
    ref_path: str,
    cur_path: str,
    config_path: Optional[str] = None,
) -> Dict[str, Any]:
    config = load_config(config_path)
    ref_df = load_dataframe(ref_path)
    cur_df = load_dataframe(cur_path)
    column_types = config.get("column_types", {})
    schema = Schema(
        column_types=column_types,
        required_columns=config.get("required_columns"),
        timestamp_column=config.get("timestamp_column"),
    )
    ref_v = schema.validate(ref_df)
    cur_v = schema.validate(cur_df)
    ok = ref_v["valid"] and cur_v["valid"]
    return {
        "valid": ok,
        "reference": ref_v,
        "current": cur_v,
    }


def main(argv: Optional[list] = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="Validate datasets against DriftLab schema config")
    p.add_argument("--ref", required=True, help="Reference dataset path")
    p.add_argument("--cur", required=True, help="Current dataset path")
    p.add_argument("--config", help="YAML config (column_types, required columns)")
    p.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout")
    args = p.parse_args(argv)

    result = validate_pair(args.ref, args.cur, args.config)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print("reference valid:", result["reference"]["valid"])
        print("current valid:", result["current"]["valid"])
        if not result["valid"]:
            print("errors:", file=sys.stderr)
            for label, block in (("reference", result["reference"]), ("current", result["current"])):
                for err in block.get("errors", []):
                    print(f"  [{label}] {err}", file=sys.stderr)
    return 0 if result["valid"] else 1
