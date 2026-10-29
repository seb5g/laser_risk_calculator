"""Génération du JSON Schema publié à partir des modèles pydantic."""
import json

from laser_risk_calculator.calculator.park import LaserPark


def park_json_schema() -> dict:
    schema = LaserPark.model_json_schema()
    schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    schema['title'] = 'Parc laser d\'une unité'
    return schema


def dumps_schema() -> str:
    return json.dumps(park_json_schema(), indent=2, ensure_ascii=False) + '\n'
