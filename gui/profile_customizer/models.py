from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class IntervalMapping:
    """
    Pure configuration for piecewise interval mapping.

    If using raw ADC values, normalize
    before calling the mapper.

    breakpoints: strictly decreasing list, e.g. [0.75, 0.50]
    outputs: length = len(breakpoints) + 1, e.g. ["A", "B", "C"]

    Intervals, top-down:
      (breakpoints[0], 1]              -> outputs[0]
      (breakpoints[1], breakpoints[0]] -> outputs[1]
      ...
      [0, breakpoints[-1]]             -> outputs[-1]
    """

    breakpoints: List[float]
    outputs: List[str]


@dataclass
class Profile:
    """A full layout/config set containing mappings for physical buttons."""

    buttons: Dict[int, IntervalMapping]
