"""Example exposure calculation engine.

SCOPE OF THE SHOWCASE: a single case is implemented, to show the shape of the engine (one beam
in, a sourced result out). The values are illustrative and must be validated by laser safety
officers against the standard before any real use. The scope of the first version is to be
defined with Marc Le Parquier and the ROP network.
"""
from dataclasses import dataclass, field
from typing import List

from laser_risk_calculator.calculator.laser import Beam, LaserType
from laser_risk_calculator.units import Q_


@dataclass
class ExposureResult:
    mpe: object                 # maximum permissible irradiance, W/m²
    nohd: object                # nominal ocular hazard distance
    exposure_time: object
    source: str
    assumptions: List[str] = field(default_factory=list)


def mpe_irradiance(beam: Beam, exposure_time=Q_(0.25, 's')):
    """MPE as an irradiance for a continuous visible beam, direct intrabeam viewing.

    Covered case: 400 to 700 nm, exposure time from 18 µs to 10 s, where the MPE as a radiant
    exposure is 18 t^0.75 J/m² (t in seconds), i.e. 25.5 W/m² for 0.25 s (aversion
    response). Any other case raises ``NotImplementedError``.
    """
    wavelength = beam.wavelength.to('nm').magnitude
    t = exposure_time.to('s').magnitude
    if beam.laser_type is not LaserType.Continuous:
        raise NotImplementedError('showcase: only continuous beams are handled')
    if not 400 <= wavelength <= 700:
        raise NotImplementedError('showcase: only the visible range 400 to 700 nm is handled')
    if not 18e-6 <= t <= 10:
        raise NotImplementedError('showcase: only exposure times from 18 µs to 10 s are handled')
    return Q_(18 * t ** 0.75 / t, 'W/m**2')


def nohd(beam: Beam, mpe):
    """Nominal ocular hazard distance, Gaussian beam of full divergence ``phi``.

    NOHD = (sqrt(4 P / (pi E_MPE)) - a) / phi, with P the power and a the output diameter.
    """
    for required in ('power', 'divergence', 'diameter'):
        if getattr(beam, required) is None:
            raise ValueError(f'Beam "{beam.name}": "{required}" is required for the NOHD')
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
        source='18 t^0.75 J/m² (visible range, 18 µs to 10 s), illustrative value to be validated',
        assumptions=['Gaussian beam', 'direct intrabeam viewing', 'point source'])
