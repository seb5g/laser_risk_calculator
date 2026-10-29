"""Description d'un laser et de ses faisceaux (sorties).

Un laser peut avoir plusieurs sorties (fondamental, harmoniques, sortie d'un OPO) : le calcul
d'exposition se fait par faisceau.
"""
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from laser_risk_calculator.units import (Angle, Duration, Energy, Frequency, Length, Power,
                                         Wavelength)


class LaserType(str, Enum):
    """Régime d'émission d'un faisceau."""
    Continuous = 'continuous'
    Pulsed = 'pulsed'

    @classmethod
    def names(cls) -> List[str]:
        return [member.name for member in cls]


class Beam(BaseModel):
    """Une sortie d'un laser, avec les paramètres dont dépend le calcul d'exposition."""
    model_config = ConfigDict(extra='forbid')

    name: str = Field('main', description='Nom de la sortie, unique dans le laser')
    laser_type: LaserType
    wavelength: Wavelength
    power: Optional[Power] = Field(None, description='Puissance continue ou moyenne')
    pulse_energy: Optional[Energy] = None
    pulse_duration: Optional[Duration] = None
    repetition_rate: Optional[Frequency] = None
    diameter: Optional[Length] = Field(None, description='Diamètre du faisceau en sortie')
    divergence: Optional[Angle] = Field(None, description='Divergence pleine')

    @model_validator(mode='after')
    def _check_regime(self):
        if self.laser_type is LaserType.Pulsed and self.pulse_duration is None:
            raise ValueError(f'Faisceau « {self.name} » impulsionnel : la durée d\'impulsion est requise')
        if self.laser_type is LaserType.Continuous and self.power is None:
            raise ValueError(f'Faisceau « {self.name} » continu : la puissance est requise')
        return self


class Laser(BaseModel):
    """Un laser du parc d'une unité."""
    model_config = ConfigDict(extra='forbid')

    id: str = Field(default_factory=lambda: uuid4().hex[:8], description='Identifiant stable')
    name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    location_id: Optional[str] = Field(None, description='Identifiant du lieu où il est utilisé')
    beams: List[Beam] = Field(min_length=1)
    notes: Optional[str] = None

    @model_validator(mode='after')
    def _check_beams(self):
        names = [beam.name for beam in self.beams]
        if len(set(names)) != len(names):
            raise ValueError(f'Laser « {self.name} » : noms de faisceaux en double {names}')
        return self

    def beam(self, name: str) -> Beam:
        for beam in self.beams:
            if beam.name == name:
                return beam
        raise KeyError(f'Laser « {self.name} » : pas de faisceau « {name} »')


if __name__ == '__main__':
    laser = Laser(name='my big laser', beams=[Beam(laser_type=LaserType.Pulsed,
                                                   pulse_duration='100fs', wavelength='515nm')])
    print(laser.model_dump_json(indent=2))
