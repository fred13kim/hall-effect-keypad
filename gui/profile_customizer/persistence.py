from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from profile_customizer.defaults import default_profiles
from profile_customizer.mapping import validate_interval_mapping
from profile_customizer.models import IntervalMapping, Profile
from profile_customizer.paths import PROFILES_PATH

CURRENT_PROFILE_SCHEMA_VERSION = 2

def load_profiles(num_profiles: int = 4, profiles_path: Path = PROFILES_PATH) -> Dict[int, Profile]:
    profiles = default_profiles(num_profiles)

    if not profiles_path.exists():
        return profiles

    try:
        data = json.loads(profiles_path.read_text(encoding="utf-8"))
        version = int(data.get("version", CURRENT_PROFILE_SCHEMA_VERSION))
    except Exception:
        return profiles

    if version != CURRENT_PROFILE_SCHEMA_VERSION:
        return profiles

    raw_profiles = data.get("profiles", {})

    print(f"Loading profiles from: {profiles_path.resolve()}")

    return _load_v2_profiles(raw_profiles, profiles, num_profiles)


def save_profiles(profiles: Dict[int, Profile], profiles_path: Path = PROFILES_PATH, active_profile: int = 1) -> None:
    data: Dict[str, Any] = {
        "version": CURRENT_PROFILE_SCHEMA_VERSION,
        "active_profile": str(active_profile),
        "hardware": {
            "adc_channels": {
                "0": "1",
                "1": "2",
                "2": "3",
                "3": "4",
            }
        },
        "profiles": {},
    }

    print(f"Saving profiles to: {profiles_path.resolve()}")

    for profile_id, profile in profiles.items():
        data["profiles"][str(profile_id)] = {
            "buttons": {
                str(button_id): {
                    # Preserve GUI order: high/rest threshold first, lower/harder-press threshold later.
                    "breakpoints": list(mapping.breakpoints),
                    "outputs": list(mapping.outputs),
                }
                for button_id, mapping in profile.buttons.items()
            }
        }

    profiles_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_v2_profiles(raw_profiles: Dict[str, Any], profiles: Dict[int, Profile], num_profiles: int,) -> Dict[int, Profile]:
    for key, value in raw_profiles.items():
        try:
            profile_id = int(key)
        except ValueError:
            continue

        if not (1 <= profile_id <= num_profiles):
            continue

        buttons = value.get("buttons", {})

        for button_id, fallback in profiles[profile_id].buttons.items():
            button_json = buttons.get(str(button_id), {})

            try:
                breakpoints = list(button_json.get("breakpoints", fallback.breakpoints))

                outputs = list(button_json.get("outputs", fallback.outputs))

                mapping = IntervalMapping(breakpoints=breakpoints, outputs=outputs)

                validate_interval_mapping(mapping)

                profiles[profile_id].buttons[button_id] = mapping

            except Exception as error:
                print(
                    f"Invalid mapping in profile {profile_id}, "
                    f"button {button_id}: {error}"
                )

                profiles[profile_id].buttons[button_id] = fallback

    return profiles
