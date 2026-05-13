from __future__ import annotations

from profile_customizer.models import IntervalMapping


def validate_interval_mapping(mapping):
    breakpoints = mapping.breakpoints
    outputs = mapping.outputs

    if len(outputs) != len(breakpoints) + 1:
        raise ValueError(
            "Number of outputs must be exactly one more than number of breakpoints."
        )

    if any(bp < 0.0 or bp > 1.0 for bp in breakpoints):
        raise ValueError("Breakpoints must be between 0.0 and 1.0.")

    if any(breakpoints[i] <= breakpoints[i + 1] for i in range(len(breakpoints) - 1)):
        raise ValueError("Breakpoints must be strictly decreasing, e.g. [0.85, 0.25].")

    return True


def map_voltage_to_output(voltage: float, mapping: IntervalMapping) -> str:
    """
    Stateless normalized-voltage-to-output mapping.
    """
    if not (0.0 <= voltage <= 1.0):
        raise ValueError("V must be in [0, 1].")

    for index, breakpoint in enumerate(mapping.breakpoints):
        if voltage > breakpoint:
            return mapping.outputs[index]

    return mapping.outputs[-1]
