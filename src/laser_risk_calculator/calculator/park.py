"""Le parc laser d'une unité : lasers, lieux, lunettes de protection et évaluations de risque."""
from datetime import date
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
    """Lunettes de protection : densité optique valable entre deux longueurs d'onde."""
    model_config = ConfigDict(extra='forbid')

    id: str
    name: str
    optical_density: float = Field(gt=0)
    wavelength_min: Wavelength
    wavelength_max: Wavelength

    def protects(self, wavelength: Length) -> bool:
        return self.wavelength_min <= wavelength <= self.wavelength_max


class RiskAssessment(BaseModel):
    """Résultat daté d'une évaluation pour un faisceau et un lieu."""
    model_config = ConfigDict(extra='forbid')

    date: date
    laser_id: str
    beam_name: str
    location_id: Optional[str] = None
    mpe: Optional[str] = Field(None, description='EMP retenue, avec son unité')
    nohd: Optional[str] = Field(None, description='DNRO retenue, avec son unité')
    laser_class: Optional[str] = None
    measures: List[str] = Field(default_factory=list)
    eyewear_ids: List[str] = Field(default_factory=list)


class LaserPark(BaseModel):
    """Racine du fichier de données : c'est ce schéma que l'on publie en JSON Schema."""
    model_config = ConfigDict(extra='forbid')

    schema_version: str = SCHEMA_VERSION
    unit_name: str = Field(description='Nom de l\'unité ou du laboratoire')
    lasers: List[Laser] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    eyewear: List[Eyewear] = Field(default_factory=list)
    assessments: List[RiskAssessment] = Field(default_factory=list)

    @model_validator(mode='after')
    def _check_references(self):
        def unique(label, ids):
            if len(set(ids)) != len(ids):
                raise ValueError(f'{label} : identifiants en double')

        unique('lasers', [laser.id for laser in self.lasers])
        unique('lieux', [location.id for location in self.locations])
        unique('lunettes', [eyewear.id for eyewear in self.eyewear])

        laser_ids = {laser.id for laser in self.lasers}
        location_ids = {location.id for location in self.locations}
        eyewear_ids = {eyewear.id for eyewear in self.eyewear}
        for laser in self.lasers:
            if laser.location_id is not None and laser.location_id not in location_ids:
                raise ValueError(f'Laser « {laser.name} » : lieu inconnu « {laser.location_id} »')
        for item in self.assessments:
            if item.laser_id not in laser_ids:
                raise ValueError(f'Évaluation du {item.date} : laser inconnu « {item.laser_id} »')
            if item.location_id is not None and item.location_id not in location_ids:
                raise ValueError(f'Évaluation du {item.date} : lieu inconnu « {item.location_id} »')
            unknown = set(item.eyewear_ids) - eyewear_ids
            if unknown:
                raise ValueError(f'Évaluation du {item.date} : lunettes inconnues {sorted(unknown)}')
        return self

    def laser(self, laser_id: str) -> Laser:
        for laser in self.lasers:
            if laser.id == laser_id:
                return laser
        raise KeyError(f'Pas de laser « {laser_id} » dans le parc')
