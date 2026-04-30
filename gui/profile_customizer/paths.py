from __future__ import annotations

from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = APP_ROOT / "configs"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

PROFILES_PATH = CONFIG_DIR / "profiles.json"
