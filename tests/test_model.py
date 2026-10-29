import json

import pytest
from pydantic import ValidationError

from laser_risk_calculator import Beam, Laser, LaserPark, LaserType
from laser_risk_calculator.units import Q_


def test_beam_accepts_text_and_numbers():
    beam = Beam(laser_type='pulsed', wavelength='515nm', pulse_duration='100fs', power=0.005)
    assert beam.wavelength == Q_(515, 'nm')
    assert beam.pulse_duration.to('s').magnitude == pytest.approx(1e-13)
    assert beam.power == Q_(5, 'mW')


def test_wrong_dimension_is_refused():
    with pytest.raises(ValidationError):
        Beam(laser_type='continuous', wavelength='5 mW', power='5 mW')


def test_regime_requirements():
    with pytest.raises(ValidationError):
        Beam(laser_type='pulsed', wavelength='800 nm')
    with pytest.raises(ValidationError):
        Beam(laser_type='continuous', wavelength='633 nm')


def test_laser_needs_distinct_beams():
    beam = dict(laser_type='continuous', wavelength='633 nm', power='1 mW')
    with pytest.raises(ValidationError):
        Laser(name='x', beams=[])
    with pytest.raises(ValidationError):
        Laser(name='x', beams=[beam, beam])


def test_serialisation_is_readable_text():
    laser = Laser(name='x', beams=[Beam(laser_type=LaserType.Pulsed, wavelength='515 nm',
                                        pulse_duration='100 fs', pulse_energy='10 uJ')])
    data = json.loads(laser.model_dump_json())
    assert data['beams'][0]['wavelength'] == '515 nm'
    assert data['beams'][0]['pulse_duration'] == '100 fs'
    assert data['beams'][0]['laser_type'] == 'pulsed'
    assert Laser.model_validate(data) == laser


def test_park_checks_references():
    laser = dict(name='x', location_id='absent',
                 beams=[dict(laser_type='continuous', wavelength='633 nm', power='1 mW')])
    with pytest.raises(ValidationError):
        LaserPark(unit_name='u', lasers=[laser])


def test_collective_protection_references():
    laser = dict(id='l1', name='x', beams=[dict(laser_type='continuous', wavelength='633 nm', power='1 mW')])
    protection = dict(id='p1', kind='interlock', description='Contact de porte', laser_ids=['l1'])
    park = LaserPark(unit_name='u', lasers=[laser], collective_protections=[protection])
    assert park.collective_protections[0].interlocked is False
    with pytest.raises(ValidationError):
        LaserPark(unit_name='u', lasers=[laser],
                  collective_protections=[dict(protection, laser_ids=['absent'])])
    with pytest.raises(ValidationError):
        LaserPark(unit_name='u', lasers=[laser], collective_protections=[protection],
                  assessments=[dict(date='2026-01-01', laser_id='l1', beam_name='main',
                                    collective_protection_ids=['absent'])])
