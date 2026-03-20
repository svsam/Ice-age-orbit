"""Orbit simulation package entry point."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

if __package__ in {None, ''}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from orbit_sim.constants import DEFAULT_OUTPUT_DIR, DEFAULT_SAMPLES, DEFAULT_YEARS
    from orbit_sim.engine import TkOrbitSimulationApp
    from orbit_sim.exporters import write_csv, write_xlsx
    from orbit_sim.simulation import generate_records
else:
    from .constants import DEFAULT_OUTPUT_DIR, DEFAULT_SAMPLES, DEFAULT_YEARS
    from .engine import TkOrbitSimulationApp
    from .exporters import write_csv, write_xlsx
    from .simulation import generate_records

__all__ = ["TkOrbitSimulationApp", "generate_records", "main"]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Run the orbit_sim package directly and launch the visualization by default.')
    parser.add_argument('--years', type=int, default=DEFAULT_YEARS)
    parser.add_argument('--samples', type=int, default=DEFAULT_SAMPLES)
    parser.add_argument('--output-dir', type=Path, default=Path(DEFAULT_OUTPUT_DIR))
    parser.add_argument('--export-only', action='store_true', help='Generate CSV/XLSX outputs without launching the Tkinter visualization.')
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    records = generate_records(args.years, args.samples)
    write_csv(records, args.output_dir / 'orbit_climate_data.csv')
    write_xlsx(records, args.output_dir / 'orbit_climate_data.xlsx')

    glacial_steps = sum(1 for record in records if record.phase == 'Glacial')
    interglacial_steps = sum(1 for record in records if record.phase == 'Interglacial')
    years_per_step = args.years / max(1, args.samples - 1)
    print(textwrap.dedent(f'''
    Generated physical simulation datasets in {args.output_dir}
    Proxy glacial duration: {glacial_steps * years_per_step:,.0f} years
    Proxy interglacial duration: {interglacial_steps * years_per_step:,.0f} years
    ''').strip())

    if not args.export_only:
        app = TkOrbitSimulationApp(records)
        app.run()


if __name__ == '__main__':
    main()
