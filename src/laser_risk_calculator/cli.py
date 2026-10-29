"""Command line interface: ``python -m laser_risk_calculator``."""
import argparse
import sys

from laser_risk_calculator.calculator.exposure import evaluate
from laser_risk_calculator.schema import dumps_schema
from laser_risk_calculator.storage import load_park


def _show(args) -> int:
    park = load_park(args.file)
    print(f'{park.unit_name}: {len(park.lasers)} laser(s), {len(park.locations)} place(s)')
    for laser in park.lasers:
        print(f'- {laser.name} [{laser.id}]')
        for beam in laser.beams:
            print(f'    {beam.name}: {beam.laser_type.value}, {beam.wavelength:~}')
    return 0


def _exposure(args) -> int:
    laser = load_park(args.file).laser(args.laser_id)
    for beam in laser.beams:
        try:
            result = evaluate(beam)
        except (NotImplementedError, ValueError) as e:
            print(f'{laser.name} / {beam.name}: not computed ({e})')
            continue
        print(f'{laser.name} / {beam.name}: MPE {result.mpe:.3~P}, NOHD {result.nohd:.3~P} '
              f'for {result.exposure_time:~}')
        print(f'    source: {result.source}')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='laser_risk_calculator',
                                     description='Showcase of the laser_risk_calculator package')
    sub = parser.add_subparsers(dest='command', required=True)
    show = sub.add_parser('show', help='summarise a park file')
    show.add_argument('file')
    show.set_defaults(func=_show)
    exposure = sub.add_parser('exposure', help='compute the exposure of the beams of a laser')
    exposure.add_argument('file')
    exposure.add_argument('laser_id')
    exposure.set_defaults(func=_exposure)
    schema = sub.add_parser('schema', help='write the JSON Schema of the park')
    schema.set_defaults(func=lambda args: sys.stdout.write(dumps_schema()) and 0)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
