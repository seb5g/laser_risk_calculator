from pathlib import Path

import pytest

from laser_risk_calculator.calculator.exposure import evaluate, mpe_irradiance
from laser_risk_calculator.storage import load_park
from laser_risk_calculator.units import Q_

EXAMPLE = Path(__file__).parent.parent / 'examples' / 'parc_exemple.json'


def test_visible_cw_mpe_for_blink_reflex():
    beam = load_park(EXAMPLE).laser('hene-01').beam('main')
    assert mpe_irradiance(beam).to('W/m**2').magnitude == pytest.approx(25.46, abs=0.01)


def test_nohd_of_a_five_milliwatt_helium_neon():
    beam = load_park(EXAMPLE).laser('hene-01').beam('main')
    assert evaluate(beam).nohd.to('m').magnitude == pytest.approx(12.6, abs=0.1)


def test_out_of_scope_is_explicit():
    beam = load_park(EXAMPLE).laser('ti-sa-01').beam('fondamental')
    with pytest.raises(NotImplementedError):
        evaluate(beam)
    cw_ir = load_park(EXAMPLE).laser('hene-01').beam('main').model_copy(update={'wavelength': Q_(1064, 'nm')})
    with pytest.raises(NotImplementedError):
        evaluate(cw_ir)
