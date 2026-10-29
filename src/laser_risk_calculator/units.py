"""Physical quantities with units, written and read as text ("515 nm").

The core only uses pint: the unit registry ``ureg`` is shared by the whole package.
"""
from typing import Annotated, Any

from pint import UnitRegistry, Quantity as PintQuantity
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema

ureg = UnitRegistry()
Q_ = ureg.Quantity


def _make_type(dimension: str, default_unit: str, example: str, label: str):
    """Build a pydantic type for a quantity of a given dimension.

    Accepts a string ("100 fs"), a number (read in ``default_unit``) or a pint quantity.
    Always writes a string, so the JSON stays readable by a human.
    """

    def validate(value: Any) -> PintQuantity:
        if isinstance(value, PintQuantity):
            quantity = value
        elif isinstance(value, bool):
            raise ValueError(f'{label}: invalid value {value!r}')
        elif isinstance(value, (int, float)):
            quantity = Q_(value, default_unit)
        elif isinstance(value, str):
            try:
                quantity = Q_(value)
            except Exception as e:
                raise ValueError(f'{label}: cannot read {value!r} ({e})') from e
        else:
            raise ValueError(f'{label}: unsupported type {type(value).__name__}')
        if isinstance(quantity, (int, float)) or not quantity.check(dimension):
            raise ValueError(f'{label}: {value!r} does not have the expected dimension {dimension}')
        return quantity

    def serialize(quantity: PintQuantity) -> str:
        return f'{quantity.magnitude:.10g} {quantity.units:~}'

    return Annotated[
        Any,
        BeforeValidator(validate),
        PlainSerializer(serialize, return_type=str),
        WithJsonSchema({'type': 'string', 'title': label, 'examples': [example],
                        'description': f'{label}, with its unit, for example "{example}"'}),
    ]


Wavelength = _make_type('[length]', 'nm', '515 nm', 'Wavelength')
Length = _make_type('[length]', 'mm', '0.7 mm', 'Length')
Duration = _make_type('[time]', 's', '100 fs', 'Duration')
Power = _make_type('[power]', 'W', '5 mW', 'Power')
Energy = _make_type('[energy]', 'J', '10 uJ', 'Energy')
Frequency = _make_type('[frequency]', 'Hz', '80 MHz', 'Frequency')
Angle = _make_type('[]', 'mrad', '1.2 mrad', 'Angle')
