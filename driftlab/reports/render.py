"""Report rendering utilities."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict


def save_json_report(data: Dict[str, Any], output_path: str) -> None:
    """Atomically save JSON report (write temp in same dir, then replace)."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=path.parent, prefix=".driftlab_", suffix=".json.tmp", text=True
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

