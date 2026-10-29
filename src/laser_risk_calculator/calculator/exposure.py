"""Exemple de moteur de calcul d'exposition.

PÉRIMÈTRE DE LA VITRINE : un seul cas est implémenté, pour montrer la forme du moteur (un
faisceau en entrée, un résultat sourcé en sortie). Les valeurs sont illustratives et doivent
être validées par des référents laser contre la norme avant tout usage réel. Le périmètre
de la première version est à définir avec Marc Le Parquier et le réseau ROP.
"""
from dataclasses import dataclass, field
from typing import List


from laser_risk_calculator.calculator.laser import Beam, LaserType
from laser_risk_calculator.units import Q_


@dataclass
class ExposureResult:
    mpe: object                 # irradiance maximale permise, W/m²
    nohd: object                # distance nominale de risque oculaire
    exposure_time: object
    source: str
    assumptions: List[str] = field(default_factory=list)


def mpe_irradiance(beam: Beam, exposure_time=Q_(0.25, 's')):
    """EMP en irradiance pour un faisceau continu visible, vue directe dans le faisceau.

    Cas couvert : 400 à 700 nm, durée d'exposition de 18 µs à 10 s, où l'EMP en exposition
    énergétique vaut 18 t^0.75 J/m² (t en secondes), soit 25,5 W/m² pour 0,25 s (réflexe
    palpébral). Tout autre cas lève ``NotImplementedError``.
    """
    wavelength = beam.wavelength.to('nm').magnitude
    t = exposure_time.to('s').magnitude
    if beam.laser_type is not LaserType.Continuous:
        raise NotImplementedError('vitrine : seuls les faisceaux continus sont traités')
    if not 400 <= wavelength <= 700:
        raise NotImplementedError('vitrine : seul le domaine visible 400 à 700 nm est traité')
    if not 18e-6 <= t <= 10:
        raise NotImplementedError('vitrine : durée d\'exposition de 18 µs à 10 s uniquement')
    return Q_(18 * t ** 0.75 / t, 'W/m**2')


def nohd(beam: Beam, mpe):
    """Distance nominale de risque oculaire, faisceau gaussien de divergence pleine ``phi``.

    NOHD = (sqrt(4 P / (pi E_MPE)) - a) / phi, avec P la puissance, a le diamètre en sortie.
    """
    for required in ('power', 'divergence', 'diameter'):
        if getattr(beam, required) is None:
            raise ValueError(f'Faisceau « {beam.name} » : « {required} » est requis pour la DNRO')
    power = beam.power.to('W').magnitude
    divergence = beam.divergence.to('rad').magnitude
    diameter = beam.diameter.to('m').magnitude
    irradiance = mpe.to('W/m**2').magnitude
    distance = ((4 * power / (3.141592653589793 * irradiance)) ** 0.5 - diameter) / divergence
    return Q_(max(distance, 0.0), 'm')


def evaluate(beam: Beam, exposure_time=Q_(0.25, 's')) -> ExposureResult:
    mpe = mpe_irradiance(beam, exposure_time)
    return ExposureResult(
        mpe=mpe, nohd=nohd(beam, mpe), exposure_time=exposure_time,
        source='18 t^0.75 J/m² (domaine visible, 18 µs à 10 s), valeur illustrative à valider',
        assumptions=['faisceau gaussien', 'vue directe dans le faisceau', 'source ponctuelle'])
