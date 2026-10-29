import json
from pathlib import Path

from laser_risk_calculator.schema import park_json_schema
from laser_risk_calculator.storage import load_park, save_park
from laser_risk_calculator.storage.elabftw import laser_from_resource, laser_to_resource

EXAMPLE = Path(__file__).parent.parent / 'examples' / 'parc_exemple.json'


def test_example_file_roundtrip(tmp_path):
    park = load_park(EXAMPLE)
    save_park(park, tmp_path / 'copie.json')
    assert load_park(tmp_path / 'copie.json') == park


def test_schema_describes_a_park():
    schema = park_json_schema()
    assert schema['title'] == 'Parc laser d\'une unité'
    assert 'lasers' in schema['properties']
    assert schema['$defs']['Beam']['properties']['wavelength']['type'] == 'string'


def test_published_schema_is_up_to_date():
    published = json.loads((EXAMPLE.parent.parent / 'schema' / 'laser_park.schema.json').read_text('utf-8'))
    assert published == park_json_schema()


def test_elabftw_resource_roundtrip():
    laser = load_park(EXAMPLE).lasers[1]
    resource = laser_to_resource(laser, category_id=7)
    assert resource['title'] == laser.name and resource['category'] == 7
    assert 'extra_fields' in json.loads(resource['metadata'])
    assert laser_from_resource(resource) == laser
