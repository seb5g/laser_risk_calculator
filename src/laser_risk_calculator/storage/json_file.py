"""Lecture et écriture d'un parc laser dans un fichier JSON (forme de référence)."""
from pathlib import Path
from typing import Union

from laser_risk_calculator.calculator.park import LaserPark


def load_park(path: Union[str, Path]) -> LaserPark:
    """Lit un fichier et le valide contre le schéma ; lève ``ValidationError`` sinon."""
    return LaserPark.model_validate_json(Path(path).read_text(encoding='utf-8'))


def save_park(park: LaserPark, path: Union[str, Path]) -> None:
    Path(path).write_text(park.model_dump_json(indent=2) + '\n', encoding='utf-8')
