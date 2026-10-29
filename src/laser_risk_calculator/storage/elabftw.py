"""Correspondance entre un laser et une ressource eLabFTW.

Un laser = une ressource. Le JSON complet du laser est rangé dans les métadonnées de la
ressource, sous la clé ``laser_risk_calculator``, et un résumé lisible est mis dans
``extra_fields`` pour apparaître dans l'interface d'eLabFTW.

ESQUISSE À VALIDER avec les développeurs d'eLabFTW : ces fonctions ne font aucun appel
réseau et leur forme n'a pas été confrontée à une instance réelle.
"""
import json
from typing import Any, Dict, Optional

from laser_risk_calculator.calculator.laser import Laser
from laser_risk_calculator.calculator.park import SCHEMA_VERSION

METADATA_KEY = 'laser_risk_calculator'


def _extra_fields(laser: Laser) -> Dict[str, Dict[str, Any]]:
    wavelengths = ', '.join(str(beam.wavelength.to('nm')) for beam in laser.beams)
    fields = {
        'Longueurs d\'onde': wavelengths,
        'Régimes': ', '.join(sorted({beam.laser_type.value for beam in laser.beams})),
        'Fabricant': laser.manufacturer or '',
        'Modèle': laser.model or '',
    }
    return {title: {'type': 'text', 'value': value} for title, value in fields.items()}


def laser_to_resource(laser: Laser, category_id: Optional[int] = None) -> Dict[str, Any]:
    """Corps d'une ressource eLabFTW pour ce laser."""
    metadata = {
        'extra_fields': _extra_fields(laser),
        METADATA_KEY: {'schema_version': SCHEMA_VERSION, 'laser': json.loads(laser.model_dump_json())},
    }
    resource: Dict[str, Any] = {'title': laser.name, 'metadata': json.dumps(metadata, ensure_ascii=False)}
    if category_id is not None:
        resource['category'] = category_id
    return resource


def laser_from_resource(resource: Dict[str, Any]) -> Laser:
    """Reconstruit le laser depuis une ressource ; lève ``ValueError`` si elle n'en décrit pas."""
    metadata = resource.get('metadata') or '{}'
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    try:
        content = metadata[METADATA_KEY]['laser']
    except KeyError as e:
        raise ValueError(f'Ressource « {resource.get("title")} » sans métadonnées {METADATA_KEY}') from e
    return Laser.model_validate(content)
