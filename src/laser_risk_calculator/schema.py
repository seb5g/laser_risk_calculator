"""Generation of the published JSON Schema from the pydantic models."""
import json

from laser_risk_calculator.calculator.park import LaserPark


def park_json_schema() -> dict:
    schema = LaserPark.model_json_schema()
    schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    schema['title'] = 'Laser park of a unit'
    return schema


def dumps_schema() -> str:
    return json.dumps(park_json_schema(), indent=2, ensure_ascii=False) + '\n'
