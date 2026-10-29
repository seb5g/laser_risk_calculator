"""The laser park of a unit: lasers, places, protective eyewear, protections and risk assessments."""
from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from laser_risk_calculator.calculator.laser import Laser
from laser_risk_calculator.units import Length, Wavelength

SCHEMA_VERSION = '0.1.0'


class Location(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: str
    building: Optional[str] = None
    room: str
    optical_table: Optional[str] = None


class Eyewear(BaseModel):
    """Protective eyewear: optical density valid between two wavelengths."""
    model_config = ConfigDict(extra='forbid')

    id: str
    name: str
    optical_density: float = Field(gt=0)
    wavelength_min: Wavelength
    wavelength_max: Wavelength

    def protects(self, wavelength: Length) -> bool:
        return self.wavelength_min <= wavelength <= self.wavelength_max


class ProtectionKind(str, Enum):
    """Kind of collective protection (as opposed to eyewear, which is individual)."""
    Enclosure = 'enclosure'              # housing, closed enclosure
    BeamTube = 'beam_tube'               # tube or sleeve protecting the beam
    BeamStop = 'beam_stop'               # beam stop (beam dump)
    Shutter = 'shutter'                  # shutter
    Screen = 'screen'                    # screen, curtain or opaque partition
    Interlock = 'interlock'              # door or access interlock
    EmergencyStop = 'emergency_stop'     # emergency stop
    WarningLight = 'warning_light'       # warning light for the zone
    AccessControl = 'access_control'     # access control to the zone
    Other = 'other'


class CollectiveProtection(BaseModel):
    """A collective protection in place, with what it protects and its follow-up."""
    model_config = ConfigDict(extra='forbid')

    id: str
    kind: ProtectionKind
    description: str = Field(description='What is in place, in one sentence')
    location_id: Optional[str] = Field(None, description='Place where it is installed')
    laser_ids: List[str] = Field(default_factory=list, description='Lasers it protects')
    interlocked: bool = Field(False, description='Connected to an interlock that cuts the laser')
    optical_density: Optional[float] = Field(
        None, gt=0, description='Optical density, for a screen or a window')
    last_check: Optional[date] = Field(None, description='Date of the last check')
    notes: Optional[str] = None


class RiskAssessment(BaseModel):
    """Dated result of an assessment for one beam and one place."""
    model_config = ConfigDict(extra='forbid')

    date: date
    laser_id: str
    beam_name: str
    location_id: Optional[str] = None
    mpe: Optional[str] = Field(None, description='MPE retained, with its unit')
    nohd: Optional[str] = Field(None, description='NOHD retained, with its unit')
    laser_class: Optional[str] = None
    measures: List[str] = Field(default_factory=list)
    eyewear_ids: List[str] = Field(default_factory=list)
    collective_protection_ids: List[str] = Field(default_factory=list)


class LaserPark(BaseModel):
    """Root of the data file: this is the schema published as JSON Schema."""
    model_config = ConfigDict(extra='forbid')

    schema_version: str = SCHEMA_VERSION
    unit_name: str = Field(description='Name of the unit or laboratory')
    lasers: List[Laser] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    eyewear: List[Eyewear] = Field(default_factory=list)
    collective_protections: List[CollectiveProtection] = Field(default_factory=list)
    assessments: List[RiskAssessment] = Field(default_factory=list)

    @model_validator(mode='after')
    def _check_references(self):
        def unique(label, ids):
            if len(set(ids)) != len(ids):
                raise ValueError(f'{label}: duplicate identifiers')

        unique('lasers', [laser.id for laser in self.lasers])
        unique('places', [location.id for location in self.locations])
        unique('eyewear', [eyewear.id for eyewear in self.eyewear])
        unique('collective protections', [item.id for item in self.collective_protections])

        laser_ids = {laser.id for laser in self.lasers}
        location_ids = {location.id for location in self.locations}
        eyewear_ids = {eyewear.id for eyewear in self.eyewear}
        protection_ids = {item.id for item in self.collective_protections}
        for laser in self.lasers:
            if laser.location_id is not None and laser.location_id not in location_ids:
                raise ValueError(f'Laser "{laser.name}": unknown place "{laser.location_id}"')
        for item in self.collective_protections:
            if item.location_id is not None and item.location_id not in location_ids:
                raise ValueError(f'Protection "{item.id}": unknown place "{item.location_id}"')
            unknown = set(item.laser_ids) - laser_ids
            if unknown:
                raise ValueError(f'Protection "{item.id}": unknown lasers {sorted(unknown)}')
        for item in self.assessments:
            if item.laser_id not in laser_ids:
                raise ValueError(f'Assessment of {item.date}: unknown laser "{item.laser_id}"')
            if item.location_id is not None and item.location_id not in location_ids:
                raise ValueError(f'Assessment of {item.date}: unknown place "{item.location_id}"')
            unknown = set(item.eyewear_ids) - eyewear_ids
            if unknown:
                raise ValueError(f'Assessment of {item.date}: unknown eyewear {sorted(unknown)}')
            unknown = set(item.collective_protection_ids) - protection_ids
            if unknown:
                raise ValueError(f'Assessment of {item.date}: unknown protections {sorted(unknown)}')
        return self

    def laser(self, laser_id: str) -> Laser:
        for laser in self.lasers:
            if laser.id == laser_id:
                return laser
        raise KeyError(f'No laser "{laser_id}" in the park')
