# Earth Orbit and Ice-Age Physical Simulation

## Overview

This project now uses a **Python-native desktop simulation** instead of a browser-based viewer. The codebase is split into reusable modules so that constants, orbital mechanics, climate calculations, exporters, and the Tkinter rendering engine are isolated and imported where needed.

The application provides:

- a Python desktop simulation engine built with `tkinter`,
- a **permanent top-down view** so the changing orbit shape is always visible,
- low-contrast dashed reference curves for the **minimum and maximum eccentricity envelopes**,
- an Earth disc with a **solid seasonal colour gradient** instead of point/circle markers,
- axial tilt modulation so the warmest band on Earth shifts as the planet revolves around the Sun,
- a dashed current orbital trail,
- eccentricity, distance, speed, and temperature calculations over a **100,000-year** ice-age cycle,
- approximately **one glacial cycle every 40,000 years**, giving about **2.5 ice ages** over the full simulation window,
- spreadsheet exports in both CSV and XLSX formats.

## Module layout

- `orbit_sim/constants.py` — physical constants and default configuration.
- `orbit_sim/mathutils.py` — shared math helpers.
- `orbit_sim/orbital.py` — Kepler solver and orbital mechanics.
- `orbit_sim/climate.py` — equilibrium temperature and climate proxy logic.
- `orbit_sim/models.py` — shared data structures.
- `orbit_sim/exporters.py` — CSV/XLSX output writers.
- `orbit_sim/engine.py` — the Python rendering engine.
- `orbit_sim/simulation.py` — top-level record generation pipeline.
- `orbit_sim/__init__.py` — package entry point that can be run directly and launches the visualization by default.
- `simulation.py` — alternate command-line entry point.

## Physical model

The elliptical orbit follows

$$
\frac{x^2}{a^2} + \frac{y^2}{b^2} = 1, \qquad b = a\sqrt{1-e^2}
$$

-42,97 +43,103 The simulation solves Kepler's equation

$$
M = E - e\sin(E)
$$

and converts the eccentric anomaly $E$ into the true anomaly $\nu$ to place the Earth along the orbit.

The instantaneous orbital speed uses the vis-viva equation

$$
v = \sqrt{\mu_\odot\left(\frac{2}{r} - \frac{1}{a}\right)}
$$

while radiative equilibrium temperature is estimated by

$$
T_{\mathrm{eq}} = \left(\frac{L_\odot (1-\alpha)}{16\pi\sigma r^2}\right)^{1/4}
$$

### Ice-age pacing used here

The long-timescale climate proxy is tuned so that the dominant glacial pacing is approximately **40,000 years**, which is close to the classic obliquity-scale pacing seen in many palaeoclimate records. In this implementation, the mean global proxy temperature oscillates mainly between roughly **7.8 °C** during glacial states and up to **15 °C** during warmer interglacial states, with smaller precession- and eccentricity-based perturbations.

The renderer separately models the Earth's yearly revolution: the planet completes **one full orbit around the Sun per simulated year** while the long-timescale orbital eccentricity and climate state evolve across the 100,000-year run.

### Axial tilt and surface heating in the renderer

The desktop visualization now includes an idealized **23.44° Earth axial tilt**. As the Earth revolves around the Sun, the subsolar latitude shifts north and south through the year, so the hottest band on the Earth disc migrates accordingly. Instead of rendering coloured point markers, the Earth is filled with a **continuous gradient**, making the seasonal heating pattern easier to read.

## Climate phases

Each sampled time step is classified as:

- **Glacial** if $T \le 8.5^\circ\mathrm{C}$,
- **Interglacial** if $T \ge 12.3^\circ\mathrm{C}$,
- **Transitional** otherwise.

## View behaviour

Inside the Tkinter window:

- The view remains fixed in a **top-down orientation**.
- The **bright dashed ellipse** is the current orbit for the current climate year.
- The **fainter dashed ellipses** show the minimum and maximum eccentricity envelopes reached across the full run.
- The Earth still completes one full revolution around the Sun per simulated year.
- The Earth's fill is a **solid gradient** whose warmest latitude shifts seasonally because of axial tilt.
- **Space** pauses or resumes the animation.
- **Esc** closes the program.

This makes it easier to compare how the orbit expands and contracts over time without camera motion obscuring the geometry.

## Comparison with real-world data, errors, and uncertainty

This model is an **educational approximation**, not a full palaeoclimate solver. Compared with real-world Earth system behaviour:

1. **Orbital pacing**: Real glacial cycles are influenced by a mixture of obliquity (~41 kyr), precession (~19–23 kyr), eccentricity (~100 kyr and ~400 kyr), greenhouse gases, albedo feedbacks, ocean circulation, and ice-sheet dynamics. This project intentionally simplifies those effects into a compact proxy formula, so the timing and amplitude of glaciations are only approximate.
2. **Temperature range**: The 7.8–15 °C global proxy range is a visualization choice for this application. Real global mean temperature anomalies between glacial and interglacial states are typically discussed relative to a baseline and depend strongly on the reconstruction method.
3. **Yearly orbit rendering**: The visual engine correctly enforces one orbit per simulated year, but it accelerates the long-term climate year independently so users can see both annual revolution and palaeoclimate evolution within the same animation.
4. **Tilt rendering**: The seasonal gradient is an idealized representation of axial tilt and sunlight distribution. It does not solve full radiative transfer, land/ocean heat capacity differences, clouds, or atmospheric circulation.
5. **No coupled ice physics**: The simulation does not solve ice-sheet flow, ocean circulation, atmospheric chemistry, or carbon-cycle feedbacks, so it cannot reproduce regional ice extent or sea-level changes with research-grade fidelity.
6. **Sampling and interpolation**: The exported timeseries are sampled discretely. Any estimate of exact glacial onset/termination timing depends on sample density and the simplifications in the proxy model.

In practice, the main uncertainties come from the simplified climate response, the absence of feedback-rich Earth system components, and the decision to use a compact visual model rather than a calibrated palaeoclimate inversion framework.

## Generated outputs

The script writes:

- `outputs/orbit_climate_data.csv`
- `outputs/orbit_climate_data.xlsx`

These files can be opened by spreadsheet applications, and the XLSX workbook is created directly from Python without requiring third-party spreadsheet packages.
