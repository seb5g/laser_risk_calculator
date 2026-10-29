"""Mapping between a laser and an eLabFTW resource.

One laser = one resource. The full JSON of the laser is stored in the resource metadata,
under the ``laser_risk_calculator`` key, and a readable summary is put in ``extra_fields`` so
that it shows up in the eLabFTW interface.

SKETCH TO BE VALIDATED with the eLabFTW developers: these functions make no network call and
their shape has not been checked against a real instance.
"""
import json
from typing import Any, Dict, Optional

from laser_risk_calculator.calculator.laser import Laser
from laser_risk_calculator.calculator.park import SCHEMA_VERSION

METADATA_KEY = 'laser_risk_calculator'


def _extra_fields(laser: Laser) -> Dict[str, Dict[str, Any]]:
    wavelengths = ', '.join(str(beam.wavelength.to('nm')) for beam in laser.beams)
    fields = {
        'Wavelengths': wavelengths,
        'Regimes': ', '.join(sorted({beam.laser_type.value for beam in laser.beams})),
        'Manufacturer': laser.manufacturer or '',
        'Model': laser.model or '',
    }
    return {title: {'type': 'text', 'value': value} for title, value in fields.items()}


def laser_to_resource(laser: Laser, category_id: Optional[int] = None) -> Dict[str, Any]:
    """Body of an eLabFTW resource for this laser."""
    metadata = {
        'extra_fields': _extra_fields(laser),
        METADATA_KEY: {'schema_version': SCHEMA_VERSION, 'laser': json.loads(laser.model_dump_json())},
    }
    resource: Dict[str, Any] = {'title': laser.name, 'metadata': json.dumps(metadata, ensure_ascii=False)}
    if category_id is not None:
        resource['category'] = category_id
    return resource


def laser_from_resource(resource: Dict[str, Any]) -> Laser:
    """Rebuild the laser from a resource; raises ``ValueError`` if it does not describe one."""
    metadata = resource.get('metadata') or '{}'
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    try:
        content = metadata[METADATA_KEY]['laser']
    except KeyError as e:
        raise ValueError(f'Resource "{resource.get("title")}" has no {METADATA_KEY} metadata') from e
    return Laser.model_validate(content)
