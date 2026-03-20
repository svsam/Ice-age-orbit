"""Climate proxy calculations."""

from __future__ import annotations

import math

from constants import (
    EARTH_ALBEDO,
    GLACIAL_REFERENCE_C,
    GLACIAL_THRESHOLD_C,
    HEATMAP_MAX_C,
    HEATMAP_MIN_C,
    INTERGLACIAL_THRESHOLD_C,
    PRECESSION_PERIOD_YEARS,
    SOLAR_LUMINOSITY_W,
    STEFAN_BOLTZMANN,
)
from mathutils import clamp


def precession_proxy(year: float) -> float:
    return math.sin(2.0 * math.pi * year / PRECESSION_PERIOD_YEARS + math.pi / 6.0)


def equilibrium_temperature_c(distance_m: float) -> float:
    flux = SOLAR_LUMINOSITY_W / (4.0 * math.pi * distance_m ** 2)
    kelvin = ((flux * (1.0 - EARTH_ALBEDO)) / (4.0 * STEFAN_BOLTZMANN)) ** 0.25
    return kelvin - 273.15


def climate_temperature_c(year: float, eccentricity: float, e_min: float, e_max: float) -> float:
    e_norm = 0.0 if e_max == e_min else (eccentricity - e_min) / (e_max - e_min)
    dominant_cycle = 11.4 + 3.5 * math.cos(2.0 * math.pi * year / 40_000.0 - math.pi / 10.0)
    secondary_forcing = 0.20 * precession_proxy(year) + 0.18 * (e_norm - 0.5)
    temperature = dominant_cycle + secondary_forcing
    if temperature < GLACIAL_REFERENCE_C:
        temperature = GLACIAL_REFERENCE_C + 0.30 * (temperature - GLACIAL_REFERENCE_C)
    return clamp(temperature, HEATMAP_MIN_C, HEATMAP_MAX_C)


def classify_phase(temperature_c: float) -> str:
    if temperature_c <= GLACIAL_THRESHOLD_C:
        return 'Glacial'
    if temperature_c >= INTERGLACIAL_THRESHOLD_C:
        return 'Interglacial'
    return 'Transitional'
