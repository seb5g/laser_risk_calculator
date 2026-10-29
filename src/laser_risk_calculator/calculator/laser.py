"""Description of a laser and its beams (outputs).

A laser can have several outputs (fundamental, harmonics, OPO output): the exposure
calculation is done per beam.
"""
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from laser_risk_calculator.units import (Angle, Duration, Energy, Frequency, Length, Power,
                                         Wavelength)


class LaserType(str, Enum):
    """Emission regime of a beam."""
    Continuous = 'continuous'
    Pulsed = 'pulsed'

    @classmethod
    def names(cls) -> List[str]:
        return [member.name for member in cls]


class Beam(BaseModel):
    """One output of a laser, with the parameters the exposure calculation depends on."""
    model_config = ConfigDict(extra='forbid')

    name: str = Field('main', description='Name of the output, unique within the laser')
    laser_type: LaserType
    wavelength: Wavelength
    power: Optional[Power] = Field(None, description='Continuous or average power')
    pulse_energy: Optional[Energy] = None
    pulse_duration: Optional[Duration] = None
    repetition_rate: Optional[Frequency] = None
    diameter: Optional[Length] = Field(None, description='Beam diameter at the output')
    divergence: Optional[Angle] = Field(None, description='Full divergence angle')

    @model_validator(mode='after')
    def _check_regime(self):
        if self.laser_type is LaserType.Pulsed and self.pulse_duration is None:
            raise ValueError(f'Pulsed beam "{self.name}": the pulse duration is required')
        if self.laser_type is LaserType.Continuous and self.power is None:
            raise ValueError(f'Continuous beam "{self.name}": the power is required')
        return self


class Laser(BaseModel):
    """A laser of a unit's park."""
    model_config = ConfigDict(extra='forbid')

    id: str = Field(default_factory=lambda: uuid4().hex[:8], description='Stable identifier')
    name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    location_id: Optional[str] = Field(None, description='Identifier of the place where it is used')
    beams: List[Beam] = Field(min_length=1)
    notes: Optional[str] = None

    @model_validator(mode='after')
    def _check_beams(self):
        names = [beam.name for beam in self.beams]
        if len(set(names)) != len(names):
            raise ValueError(f'Laser "{self.name}": duplicate beam names {names}')
        return self

    def beam(self, name: str) -> Beam:
        for beam in self.beams:
            if beam.name == name:
                return beam
        raise KeyError(f'Laser "{self.name}": no beam "{name}"')


if __name__ == '__main__':
    laser = Laser(name='my big laser', beams=[Beam(laser_type=LaserType.Pulsed,
                                                   pulse_duration='100fs', wavelength='515nm')])
    print(laser.model_dump_json(indent=2))
