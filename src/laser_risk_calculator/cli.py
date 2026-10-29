"""Interface en ligne de commande : ``python -m laser_risk_calculator``."""
import argparse
import sys

from laser_risk_calculator.calculator.exposure import evaluate
from laser_risk_calculator.schema import dumps_schema
from laser_risk_calculator.storage import load_park


def _show(args) -> int:
    park = load_park(args.file)
    print(f'{park.unit_name} : {len(park.lasers)} laser(s), {len(park.locations)} lieu(x)')
    for laser in park.lasers:
        print(f'- {laser.name} [{laser.id}]')
        for beam in laser.beams:
            print(f'    {beam.name} : {beam.laser_type.value}, {beam.wavelength:~}')
    return 0


def _exposure(args) -> int:
    laser = load_park(args.file).laser(args.laser_id)
    for beam in laser.beams:
        try:
            result = evaluate(beam)
        except (NotImplementedError, ValueError) as e:
            print(f'{laser.name} / {beam.name} : non calculé ({e})')
            continue
        print(f'{laser.name} / {beam.name} : EMP {result.mpe:.3~P}, DNRO {result.nohd:.3~P} '
              f'pour {result.exposure_time:~}')
        print(f'    source : {result.source}')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='laser_risk_calculator',
                                     description='Vitrine du paquet laser_risk_calculator')
    sub = parser.add_subparsers(dest='command', required=True)
    show = sub.add_parser('show', help='résume un fichier de parc')
    show.add_argument('file')
    show.set_defaults(func=_show)
    exposure = sub.add_parser('exposure', help='calcule l\'exposition des faisceaux d\'un laser')
    exposure.add_argument('file')
    exposure.add_argument('laser_id')
    exposure.set_defaults(func=_exposure)
    schema = sub.add_parser('schema', help='écrit le JSON Schema du parc')
    schema.set_defaults(func=lambda args: sys.stdout.write(dumps_schema()) and 0)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
