# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from numpy.testing import assert_allclose
import astropy.units as u
from gammapy.irf import EffectiveAreaTable, EDispKernel
from gammapy.spectrum import CountsSpectrum, SensitivityEstimator, SpectrumDataset


@pytest.fixture()
def spectrum_dataset():
    etrue = np.logspace(0, 1, 21) * u.TeV
    ereco = np.logspace(0, 1, 5) * u.TeV
    aeff = EffectiveAreaTable.from_constant(value=1e6 * u.m ** 2, energy=etrue)
    edisp = EDispKernel.from_diagonal_response(etrue, ereco)

    data = np.ones(4)
    data[-1] = 1e-3
    background = CountsSpectrum(
        energy_lo=ereco[:-1], energy_hi=ereco[1:], data=data, unit="s-1"
    )
    return SpectrumDataset(
        aeff=aeff,
        livetime="5h",
        edisp=edisp,
        background=background
    )


def test_cta_sensitivity_estimator(spectrum_dataset):
    sens = SensitivityEstimator()
    table = sens.run(spectrum_dataset)

    assert len(table) == 4
    assert table.colnames == ["energy", "e2dnde", "excess", "background", "criterion"]
    assert table["energy"].unit == "TeV"
    assert table["e2dnde"].unit == "erg / (cm2 s)"

    row = table[0]
    assert_allclose(row["energy"], 1.33352, rtol=1e-3)
    assert_allclose(row["e2dnde"], 3.40101e-11, rtol=1e-3)
    assert_allclose(row["excess"], 334.454, rtol=1e-3)
    assert_allclose(row["background"], 3600, rtol=1e-3)
    assert row["criterion"] == "significance"

    row = table[3]
    assert_allclose(row["energy"], 7.49894, rtol=1e-3)
    assert_allclose(row["e2dnde"], 1.14367e-11, rtol=1e-3)
    assert_allclose(row["excess"], 20, rtol=1e-3)
    assert_allclose(row["background"], 3.6, rtol=1e-3)
    assert row["criterion"] == "gamma"
