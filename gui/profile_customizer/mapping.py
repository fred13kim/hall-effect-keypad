from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QLineEdit, QPushButton
)

from profile_customizer.models import IntervalMapping


def validate_interval_mapping(mapping: IntervalMapping) -> None:
    breakpoints = mapping.breakpoints
    outputs = mapping.outputs

    num_break = len(breakpoints)

    if any(not isinstance(b, (int, float)) for b in breakpoints):
        raise ValueError("All breakpoints must be within in [0, 1].")

    if any(not isinstance(o, str) for o in outputs):
        raise ValueError("All outputs must be strings.")

    if len(outputs) != len(breakpoints) + 1:
        raise ValueError(f"Must have exactly {num_break + 1} outputs.")

    previous = None
    for breakpoint in breakpoints:
        breakpoint = float(breakpoint)
        if not (0.0 <= breakpoint <= 1.0):
            raise ValueError("All breakpoints must be within [0, 1].")
        if previous is not None and not (previous > breakpoint):
            raise ValueError("Breakpoints must be strictly decreasing, e.g. [0.75, 0.5].")
        previous = breakpoint


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
