"""Orbital mechanics functions."""

from __future__ import annotations

import math

from constants import (
    AU_M,
    ECCENTRICITY_CYCLE_AMPLITUDE,
    ECCENTRICITY_LONG_AMPLITUDE,
    ECCENTRICITY_LONG_PERIOD_YEARS,
    ECCENTRICITY_MEAN,
    SOLAR_MU,
)
from mathutils import clamp


def eccentricity_over_time(year: float, cycle_years: float) -> float:
    base = ECCENTRICITY_MEAN + ECCENTRICITY_CYCLE_AMPLITUDE * math.cos(2.0 * math.pi * year / cycle_years)
    long_mod = ECCENTRICITY_LONG_AMPLITUDE * math.cos(2.0 * math.pi * year / ECCENTRICITY_LONG_PERIOD_YEARS)
    return clamp(base + long_mod, 0.003, 0.067)


def solve_kepler(mean_anomaly_rad: float, eccentricity: float, iterations: int = 8) -> float:
    estimate = mean_anomaly_rad if eccentricity < 0.8 else math.pi
    for _ in range(iterations):
        residual = estimate - eccentricity * math.sin(estimate) - mean_anomaly_rad
        derivative = 1.0 - eccentricity * math.cos(estimate)
        estimate -= residual / derivative
    return estimate


def true_anomaly_from_mean(mean_anomaly_rad: float, eccentricity: float) -> float:
    eccentric_anomaly = solve_kepler(mean_anomaly_rad, eccentricity)
    numerator = math.sqrt(1.0 + eccentricity) * math.sin(eccentric_anomaly / 2.0)
    denominator = math.sqrt(1.0 - eccentricity) * math.cos(eccentric_anomaly / 2.0)
    return 2.0 * math.atan2(numerator, denominator)


def semi_minor_axis_au(eccentricity: float) -> float:
    return math.sqrt(1.0 - eccentricity ** 2)


def orbital_radius_au(true_anomaly_rad: float, eccentricity: float, semi_major_axis_au: float = 1.0) -> float:
    return semi_major_axis_au * (1.0 - eccentricity ** 2) / (1.0 + eccentricity * math.cos(true_anomaly_rad))


def heliocentric_position_au(true_anomaly_rad: float, eccentricity: float, inclination_rad: float) -> tuple[float, float, float]:
    radius = orbital_radius_au(true_anomaly_rad, eccentricity)
    x = radius * math.cos(true_anomaly_rad) - eccentricity
    y = radius * math.sin(true_anomaly_rad) * math.sin(inclination_rad)
    z = radius * math.sin(true_anomaly_rad) * math.cos(inclination_rad)
    return x, y, z


def instantaneous_speed_m_s(radius_au: float, semi_major_axis_au: float = 1.0) -> float:
    radius_m = radius_au * AU_M
    semi_major_m = semi_major_axis_au * AU_M
    return math.sqrt(SOLAR_MU * (2.0 / radius_m - 1.0 / semi_major_m))
