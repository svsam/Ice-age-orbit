"""Shared math helpers used by multiple modules."""

from __future__ import annotations


def linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + index * step for index in range(count)]


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))
