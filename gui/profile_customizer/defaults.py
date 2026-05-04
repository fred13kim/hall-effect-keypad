from __future__ import annotations

from typing import Dict

from profile_customizer.models import IntervalMapping, Profile


def default_profiles(num_profiles: int = 4, num_buttons: int = 4) -> Dict[int, Profile]:
    """
    Build default profile presets.

    Each profile receives fresh IntervalMapping objects so profiles/buttons do
    not accidentally share mutable lists.
    """

    button_defaults: Dict[int, IntervalMapping] = {
        1: IntervalMapping([0.75, 0.50], ["A", "B", "C"]),
        2: IntervalMapping([0.75, 0.50], ["D", "E", "F"]),
        3: IntervalMapping([0.75, 0.50], ["G", "H", "I"]),
        4: IntervalMapping([0.75, 0.50], ["J", "K", "L"]),
    }

    profiles: Dict[int, Profile] = {}
    for profile_id in range(1, num_profiles + 1):
        buttons = {}
        for button_id in range(1, num_buttons + 1):
            template = button_defaults.get(button_id, button_defaults[1])
            buttons[button_id] = IntervalMapping(
                breakpoints=list(template.breakpoints),
                outputs=list(template.outputs),
                hysteresis=float(template.hysteresis),
            )
        profiles[profile_id] = Profile(buttons=buttons)

    return profiles
