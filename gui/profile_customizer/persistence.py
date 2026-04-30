from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from profile_customizer.defaults import default_profiles
from profile_customizer.mapping import validate_interval_mapping
from profile_customizer.models import IntervalMapping, Profile
from profile_customizer.paths import PROFILES_PATH

CURRENT_PROFILE_SCHEMA_VERSION = 2


def load_profiles(num_profiles: int = 4, profiles_path: Path = PROFILES_PATH) -> Dict[int, Profile]:
    """
    Load profiles from JSON.

    Supported schema versions:
      v1: profile-level single mapping; migrated to all buttons.
      v2: per-button mappings.
    """

    profiles = default_profiles(num_profiles)
    if not profiles_path.exists():
        return profiles

    try:
        data = json.loads(profiles_path.read_text(encoding="utf-8"))
        version = int(data.get("version", 1))
        raw_profiles = data.get("profiles", {})

        if version == 1:
            return _load_v1_profiles(raw_profiles, profiles, num_profiles)

        if version == 2:
            return _load_v2_profiles(raw_profiles, profiles, num_profiles)

        return profiles
    except Exception:
        return default_profiles(num_profiles)


def save_profiles(profiles: Dict[int, Profile], profiles_path: Path = PROFILES_PATH) -> None:
    data: Dict[str, Any] = {"version": CURRENT_PROFILE_SCHEMA_VERSION, "profiles": {}}

    for profile_id, profile in profiles.items():
        data["profiles"][str(profile_id)] = {
            "buttons": {
                str(button_id): asdict(mapping)
                for button_id, mapping in profile.buttons.items()
            }
        }

    profiles_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_v1_profiles(
    raw_profiles: Dict[str, Any],
    profiles: Dict[int, Profile],
    num_profiles: int,
) -> Dict[int, Profile]:
    for key, value in raw_profiles.items():
        profile_id = int(key)
        if not (1 <= profile_id <= num_profiles):
            continue

        fallback = profiles[profile_id].buttons[1]
        mapping_json = value.get("mapping", {})
        mapping = IntervalMapping(
            breakpoints=list(mapping_json.get("breakpoints", fallback.breakpoints)),
            outputs=list(mapping_json.get("outputs", fallback.outputs)),
            hysteresis=float(mapping_json.get("hysteresis", fallback.hysteresis)),
        )
        validate_interval_mapping(mapping)

        for button_id in profiles[profile_id].buttons:
            profiles[profile_id].buttons[button_id] = _copy_mapping(mapping)

    return profiles


def _load_v2_profiles(
    raw_profiles: Dict[str, Any],
    profiles: Dict[int, Profile],
    num_profiles: int,
) -> Dict[int, Profile]:
    for key, value in raw_profiles.items():
        profile_id = int(key)
        if not (1 <= profile_id <= num_profiles):
            continue

        buttons = value.get("buttons", {})
        for button_id, fallback in profiles[profile_id].buttons.items():
            button_json = buttons.get(str(button_id), {})
            mapping = IntervalMapping(
                breakpoints=list(button_json.get("breakpoints", fallback.breakpoints)),
                outputs=list(button_json.get("outputs", fallback.outputs)),
                hysteresis=float(button_json.get("hysteresis", fallback.hysteresis)),
            )
            validate_interval_mapping(mapping)
            profiles[profile_id].buttons[button_id] = mapping

    return profiles


def _copy_mapping(mapping: IntervalMapping) -> IntervalMapping:
    return IntervalMapping(
        breakpoints=list(mapping.breakpoints),
        outputs=list(mapping.outputs),
        hysteresis=float(mapping.hysteresis),
    )
