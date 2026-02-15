"""Report rendering utilities."""

from pathlib import Path
from typing import Dict, Any
import json


def save_json_report(data: Dict[str, Any], output_path: str) -> None:
    """Save JSON report to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

