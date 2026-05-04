from __future__ import annotations

from profile_customizer.models import IntervalMapping


def validate_interval_mapping(mapping: IntervalMapping) -> None:
    breakpoints = mapping.breakpoints
    outputs = mapping.outputs

    if any(not isinstance(b, (int, float)) for b in breakpoints):
        raise ValueError("All breakpoints must be numbers.")

    if any(not isinstance(o, str) for o in outputs):
        raise ValueError("All outputs must be strings.")

    if len(outputs) != len(breakpoints) + 1:
        raise ValueError("outputs must have exactly len(breakpoints) + 1 items.")

    previous = None
    for breakpoint in breakpoints:
        breakpoint = float(breakpoint)
        if not (0.0 <= breakpoint <= 1.0):
            raise ValueError("All breakpoints must be within [0, 1].")
        if previous is not None and not (previous > breakpoint):
            raise ValueError("breakpoints must be strictly decreasing, e.g. [0.75, 0.5].")
        previous = breakpoint


def map_voltage_to_output(voltage: float, mapping: IntervalMapping) -> str:
    """
    Stateless normalized-voltage-to-output mapping.
    """

    if not (0.0 <= voltage <= 1.0):
        raise ValueError("v must be in [0, 1].")

    for index, breakpoint in enumerate(mapping.breakpoints):
        if voltage > breakpoint:
            return mapping.outputs[index]

    return mapping.outputs[-1]
