"""Core simulation pipeline."""

from __future__ import annotations

import math

from climate import classify_phase, climate_temperature_c, equilibrium_temperature_c
from constants import AU_M
from mathutils import linspace
from models import ClimateRecord
from orbital import (
    eccentricity_over_time,
    heliocentric_position_au,
    instantaneous_speed_m_s,
    orbital_radius_au,
    semi_minor_axis_au,
    true_anomaly_from_mean,
)


def generate_records(total_years: int, samples: int) -> list[ClimateRecord]:
    years = linspace(0.0, float(total_years), samples)
    eccentricities = [eccentricity_over_time(year, float(total_years)) for year in years]
    e_min = min(eccentricities)
    e_max = max(eccentricities)

    records: list[ClimateRecord] = []
    for year, eccentricity in zip(years, eccentricities):
        mean_anomaly = 2.0 * math.pi * (year / float(total_years))
        true_anomaly = true_anomaly_from_mean(mean_anomaly, eccentricity)
        inclination = math.radians(7.0 * math.sin(2.0 * math.pi * year / 41_000.0))
        x_au, y_au, z_au = heliocentric_position_au(true_anomaly, eccentricity, inclination)
        radius_au = orbital_radius_au(true_anomaly, eccentricity)
        equilibrium_c = equilibrium_temperature_c(radius_au * AU_M)
        climate_c = climate_temperature_c(year, eccentricity, e_min, e_max)
        records.append(
            ClimateRecord(
                year=year,
                eccentricity=eccentricity,
                semi_major_axis_au=1.0,
                semi_minor_axis_au=semi_minor_axis_au(eccentricity),
                mean_distance_au=radius_au,
                true_anomaly_rad=true_anomaly,
                heliocentric_x_au=x_au,
                heliocentric_y_au=y_au,
                heliocentric_z_au=z_au,
                orbital_speed_m_s=instantaneous_speed_m_s(radius_au),
                equilibrium_temp_c=equilibrium_c,
                climate_temp_c=climate_c,
                phase=classify_phase(climate_c),
            )
        )
    return records
