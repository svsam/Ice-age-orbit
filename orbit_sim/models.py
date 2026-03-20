from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClimateRecord:
    year: float
    eccentricity: float
    semi_major_axis_au: float
    semi_minor_axis_au: float
    mean_distance_au: float
    true_anomaly_rad: float
    heliocentric_x_au: float
    heliocentric_y_au: float
    heliocentric_z_au: float
    orbital_speed_m_s: float
    equilibrium_temp_c: float
    climate_temp_c: float
    phase: str
