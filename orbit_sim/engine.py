"""Tkinter-based top-down renderer for the orbit simulation."""

from __future__ import annotations

import math
import tkinter as tk
from typing import Iterable

from .constants import AXIAL_TILT_DEG, HEATMAP_MAX_C, HEATMAP_MIN_C, ORBIT_POINT_COUNT, WINDOW_HEIGHT, WINDOW_WIDTH
from .models import ClimateRecord
from .orbital import true_anomaly_from_mean


class TkOrbitSimulationApp:
    def __init__(self, records: list[ClimateRecord]) -> None:
        if not records:
            raise ValueError('TkOrbitSimulationApp requires at least one ClimateRecord.')
        self.records = records
        self.root = tk.Tk()
        self.root.title('Earth Orbit and Ice-Age Physical Simulation')
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.root.configure(bg='#08111f')

        self.canvas = tk.Canvas(self.root, width=920, height=WINDOW_HEIGHT, bg='#050a14', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(self.root, width=360, bg='#0d1424')
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)

        self.metrics: dict[str, tk.Label] = {}
        self.running = True
        self.total_years = records[-1].year
        self.climate_year = 0.0
        self.climate_year_step = max(8.0, self.total_years / max(1, len(records) * 3.5))
        self.orbit_fraction = 0.0
        self.orbit_fraction_step = 1.0 / 24.0
        self.min_eccentricity = min(record.eccentricity for record in records)
        self.max_eccentricity = max(record.eccentricity for record in records)

        self._populate_sidebar()
        self.root.bind('<space>', lambda event: self.toggle_animation())
        self.root.bind('<Escape>', lambda event: self.root.destroy())

    def _add_metric_row(self, key: str) -> None:
        frame = tk.Frame(self.sidebar, bg='#172138')
        frame.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(frame, text=key, fg='white', bg='#172138', font=('Arial', 11, 'bold')).pack(anchor='w', padx=12, pady=(10, 0))
        value = tk.Label(frame, text='-', fg='#9fd3ff', bg='#172138', font=('Consolas', 11))
        value.pack(anchor='w', padx=12, pady=(4, 10))
        self.metrics[key] = value

    def _populate_sidebar(self) -> None:
        title = tk.Label(self.sidebar, text='Earth Orbit / Ice-Age Model', fg='white', bg='#0d1424', font=('Arial', 18, 'bold'))
        title.pack(anchor='w', padx=20, pady=(20, 12))
        description = (
            'This renderer keeps a permanent top-down view so the changing orbit shape remains easy '
            'to compare over the full 100,000-year climate timeline. The Earth heatmap also shifts '
            'seasonally with axial tilt as the planet revolves around the Sun.'
        )
        tk.Label(self.sidebar, text=description, wraplength=300, justify='left', fg='#d9e8ff', bg='#0d1424').pack(anchor='w', padx=20)

        for key in ['Climate year', 'Eccentricity', 'Distance (AU)', 'Speed (km/s)', 'Equilibrium temp (°C)', 'Climate temp (°C)', 'Phase']:
            self._add_metric_row(key)

        legend_text = (
            'Top-down view\n'
            'Dashed grey curves: minimum/maximum eccentricity envelopes\n'
            'Bright dashed curve: current orbit\n'
            'Earth disc: solid seasonal gradient with axial-tilt heating\n'
            'Space: pause/resume   Esc: quit'
        )
        tk.Label(self.sidebar, text=legend_text, wraplength=300, justify='left', fg='#9fb5d1', bg='#0d1424').pack(anchor='w', padx=20, pady=20)

    def toggle_animation(self) -> None:
        self.running = not self.running
        if self.running:
            self._tick()

    def _temperature_to_color(self, temperature_c: float) -> str:
        anchors = [
            (HEATMAP_MIN_C, (255, 255, 255)),
            (7.8, (190, 225, 255)),
            (10.0, (255, 210, 130)),
            (12.5, (255, 140, 70)),
            (HEATMAP_MAX_C, (220, 40, 40)),
        ]
        value = max(HEATMAP_MIN_C, min(HEATMAP_MAX_C, temperature_c))
        for (ta, ca), (tb, cb) in zip(anchors, anchors[1:]):

            if ta <= value <= tb:
                factor = 0.0 if tb == ta else (value - ta) / (tb - ta)
                r = round(ca[0] + factor * (cb[0] - ca[0]))
                g = round(ca[1] + factor * (cb[1] - ca[1]))
                b = round(ca[2] + factor * (cb[2] - ca[2]))
                return f'#{r:02x}{g:02x}{b:02x}'
        return '#dc2828'

    def _record_for_year(self) -> ClimateRecord:
        fraction = 0.0 if self.total_years == 0 else self.climate_year / self.total_years
        index = min(len(self.records) - 1, max(0, round(fraction * (len(self.records) - 1))))
        return self.records[index]

    def current_record(self) -> ClimateRecord:
        return self._record_for_year()

    def _orbit_points(self, eccentricity: float) -> Iterable[tuple[float, float]]:
        for index in range(ORBIT_POINT_COUNT + 1):
            mean_anomaly = 2.0 * math.pi * index / ORBIT_POINT_COUNT
            true_anomaly = true_anomaly_from_mean(mean_anomaly, eccentricity)
            radius = (1.0 - eccentricity ** 2) / (1.0 + eccentricity * math.cos(true_anomaly))
            yield radius * math.cos(true_anomaly) - eccentricity, radius * math.sin(true_anomaly)

    def _earth_center(self, record: ClimateRecord) -> tuple[float, float]:
        mean_anomaly = 2.0 * math.pi * self.orbit_fraction
        true_anomaly = true_anomaly_from_mean(mean_anomaly, record.eccentricity)
        radius = (1.0 - record.eccentricity ** 2) / (1.0 + record.eccentricity * math.cos(true_anomaly))
        return radius * math.cos(true_anomaly) - record.eccentricity, radius * math.sin(true_anomaly)

    def _view_transform(self, x_au: float, z_au: float) -> tuple[float, float]:
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        scale = min(width, height) * 0.32
        return width * 0.5 + x_au * scale, height * 0.5 - z_au * scale

    def _draw_orbit_curve(self, eccentricity: float, color: str, dash: tuple[int, int], width: int) -> None:
        points: list[float] = []
        for x_au, z_au in self._orbit_points(eccentricity):
            px, py = self._view_transform(x_au, z_au)
            points.extend([px, py])
        self.canvas.create_line(*points, fill=color, dash=dash, width=width, smooth=True)

    def _draw_earth_gradient(self, center_x: float, center_y: float, radius: float, climate_temp_c: float) -> None:
        subsolar_lat = AXIAL_TILT_DEG * math.sin(2.0 * math.pi * self.orbit_fraction)
        line_step = max(1, int(radius / 18))
        for pixel_y in range(int(center_y - radius), int(center_y + radius) + 1, line_step):
            dy = pixel_y - center_y
            if abs(dy) > radius:
                continue
            chord = math.sqrt(max(radius ** 2 - dy ** 2, 0.0))
            normalized = dy / radius if radius else 0.0
            latitude = normalized * 90.0
            seasonal_gain = 2.2 * math.cos(math.radians(latitude - subsolar_lat))
            polar_cooling = 1.4 * (abs(latitude) / 90.0) ** 1.15
            local_temp = climate_temp_c + seasonal_gain - polar_cooling
            color = self._temperature_to_color(local_temp)
            self.canvas.create_line(center_x - chord, pixel_y, center_x + chord, pixel_y, fill=color, width=line_step)

        self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline='#d9f4ff', width=2)

        axis_angle = math.radians(90.0 - AXIAL_TILT_DEG * math.cos(2.0 * math.pi * self.orbit_fraction))
        axis_dx = math.cos(axis_angle) * radius * 0.95
        axis_dy = -math.sin(axis_angle) * radius * 0.95
        self.canvas.create_line(center_x - axis_dx, center_y - axis_dy, center_x + axis_dx, center_y + axis_dy, fill='#e8f3ff', width=2)

    def _draw_frame(self) -> None:
        self.canvas.delete('all')
        record = self._record_for_year()

        self._draw_orbit_curve(self.min_eccentricity, '#364152', (5, 8), 2)
        self._draw_orbit_curve(self.max_eccentricity, '#4b5568', (5, 8), 2)
        self._draw_orbit_curve(record.eccentricity, '#d6e7ff', (7, 7), 3)

        sun_x, sun_y = self._view_transform(0.0, 0.0)
        self.canvas.create_oval(sun_x - 18, sun_y - 18, sun_x + 18, sun_y + 18, fill='#ffca45', outline='')
        self.canvas.create_oval(sun_x - 7, sun_y - 7, sun_x + 7, sun_y + 7, fill='#fff2a6', outline='')
        self.canvas.create_text(sun_x, sun_y + 28, text='Sun', fill='#ffe9a8', font=('Arial', 11, 'bold'))

        earth_x_au, earth_z_au = self._earth_center(record)
        earth_x, earth_y = self._view_transform(earth_x_au, earth_z_au)
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        base_radius = min(width, height) * 0.042
        self._draw_earth_gradient(earth_x, earth_y, base_radius, record.climate_temp_c)

        self.canvas.create_text(140, 30, text='Low-opacity dashed envelopes = minimum / maximum eccentricity', fill='#8aa0b8', font=('Arial', 10), anchor='w')
        self.canvas.create_text(140, 48, text='Bright dashed curve = current eccentricity orbit', fill='#d6e7ff', font=('Arial', 10), anchor='w')
        self.canvas.create_text(140, 66, text='Earth colour gradient shifts with seasonal axial tilt', fill='#b8d4ff', font=('Arial', 10), anchor='w')

        self.metrics['Climate year'].config(text=f'{self.climate_year:,.0f}')
        self.metrics['Eccentricity'].config(text=f'{record.eccentricity:.5f}')
        self.metrics['Distance (AU)'].config(text=f'{record.mean_distance_au:.5f}')
        self.metrics['Speed (km/s)'].config(text=f'{record.orbital_speed_m_s / 1000.0:.3f}')
        self.metrics['Equilibrium temp (°C)'].config(text=f'{record.equilibrium_temp_c:.2f}')
        self.metrics['Climate temp (°C)'].config(text=f'{record.climate_temp_c:.2f}')
        self.metrics['Phase'].config(text=record.phase)

    def _advance_time(self) -> None:
        self.orbit_fraction = (self.orbit_fraction + self.orbit_fraction_step) % 1.0
        self.climate_year += self.climate_year_step
        if self.climate_year > self.total_years:
            self.climate_year = 0.0

    def _tick(self) -> None:
        if not self.running:
            return
        self._draw_frame()
        self._advance_time()
        self.root.after(33, self._tick)

    def run(self) -> None:
        self._tick()
        self.root.mainloop()