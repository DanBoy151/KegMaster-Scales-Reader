import json
from pathlib import Path
from typing import List, Dict, Optional


def _candidate_config_paths() -> List[Path]:
    # Project layout: repo root contains `settings/` and `src/`
    # This file is in src/kegmaster-scales-reader/utils/
    settings_dir = Path(__file__).resolve().parents[3] / "settings"
    return [
        settings_dir / "scales.yaml",
        settings_dir / "scales.yml",
        settings_dir / "scales.json",
    ]


def load_scales_config(path: Optional[str] = None) -> List[Dict]:
    """Load scales configuration.

    Expects a JSON file with the shape:
    { "scales": [ {"name": "...", "address": "...", "literSize": 50.0}, ... ] }

    Returns the list of scale dicts.
    """
    if path:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")
    else:
        p = None
        for cand in _candidate_config_paths():
            if cand.exists():
                p = cand
                break
        if p is None:
            raise FileNotFoundError(
                f"No config file found. Tried: {', '.join(str(x) for x in _candidate_config_paths())}"
            )

    # Load depending on file type
    if p.suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except Exception:
            raise ImportError(
                "PyYAML is required to load YAML config files. Install with 'pip install pyyaml'"
            )
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    else:
        # JSON
        data = json.loads(p.read_text(encoding="utf-8"))

    scales = data.get("scales")
    if scales is None:
        raise ValueError("Config file missing top-level 'scales' key")

    # basic validation
    for idx, s in enumerate(scales):
        if not isinstance(s, dict):
            raise ValueError(f"Scale entry at index {idx} is not an object: {s}")
        if "address" not in s:
            raise ValueError(f"Scale entry at index {idx} missing 'address': {s}")
        if "literSize" not in s:
            raise ValueError(f"Scale entry at index {idx} missing 'literSize': {s}")

    return scales


if __name__ == "__main__":
    # Quick CLI to print loaded scales
    try:
        cfg = load_scales_config()
    except Exception as e:
        print(f"Failed to load config: {e}")
    else:
        print("Loaded scales:")
        for s in cfg:
            print(f" - {s.get('name','<unnamed>')}: {s['address']} ({s['literSize']} L)")
