import json
from pathlib import Path
from typing import Any, Dict

def export_reactions(payload: Dict[str, Any], output_path: Path) -> None:
    """
    Write the reactions payload to disk in pretty-printed JSON (UTF-8).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)