"""Grandeurs physiques avec unités, lisibles et écrites sous forme de texte (« 515 nm »).

Le cœur n'utilise que pint : le registre d'unités ``ureg`` est partagé par tout le paquet.
"""
from typing import Annotated, Any

from pint import UnitRegistry, Quantity as PintQuantity
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema

ureg = UnitRegistry()
Q_ = ureg.Quantity


def _make_type(dimension: str, default_unit: str, example: str, label: str):
    """Construit un type pydantic pour une grandeur de dimension donnée.

    Accepte une chaîne (« 100 fs »), un nombre (interprété dans ``default_unit``) ou une
    grandeur pint. Écrit toujours une chaîne, donc un JSON lisible par un humain.
    """

    def validate(value: Any) -> PintQuantity:
        if isinstance(value, PintQuantity):
            quantity = value
        elif isinstance(value, bool):
            raise ValueError(f'{label} : valeur invalide {value!r}')
        elif isinstance(value, (int, float)):
            quantity = Q_(value, default_unit)
        elif isinstance(value, str):
            try:
                quantity = Q_(value)
            except Exception as e:
                raise ValueError(f'{label} : impossible de lire {value!r} ({e})') from e
        else:
            raise ValueError(f'{label} : type non pris en charge {type(value).__name__}')
        if isinstance(quantity, (int, float)) or not quantity.check(dimension):
            raise ValueError(f'{label} : {value!r} n\'a pas la dimension attendue {dimension}')
        return quantity

    def serialize(quantity: PintQuantity) -> str:
        return f'{quantity.magnitude:.10g} {quantity.units:~}'

    return Annotated[
        Any,
        BeforeValidator(validate),
        PlainSerializer(serialize, return_type=str),
        WithJsonSchema({'type': 'string', 'title': label, 'examples': [example],
                        'description': f'{label}, avec son unité, par exemple « {example} »'}),
    ]


Wavelength = _make_type('[length]', 'nm', '515 nm', 'Longueur d\'onde')
Length = _make_type('[length]', 'mm', '0.7 mm', 'Longueur')
Duration = _make_type('[time]', 's', '100 fs', 'Durée')
Power = _make_type('[power]', 'W', '5 mW', 'Puissance')
Energy = _make_type('[energy]', 'J', '10 uJ', 'Énergie')
Frequency = _make_type('[frequency]', 'Hz', '80 MHz', 'Fréquence')
Angle = _make_type('[]', 'mrad', '1.2 mrad', 'Angle')
