import numpy as np
from numpy.testing import assert_allclose
import astropy.units as u
from gammapy.maps import MapAxis
from gammapy.irf import RadMax2D, EffectiveAreaTable2D

import pytest


def test_rad_max_roundtrip(tmp_path):
    n_energy = 10
    energy_axis = MapAxis.from_energy_bounds(
        50 * u.GeV, 100 * u.TeV, n_energy, name="energy"
    )

    n_offset = 5
    offset_axis = MapAxis.from_bounds(0, 2, n_offset, unit=u.deg, name="offset")

    shape = (n_energy, n_offset)
    rad_max = np.linspace(0.1, 0.5, n_energy * n_offset).reshape(shape)

    rad_max_2d = RadMax2D(
        axes=[
            energy_axis,
            offset_axis,
        ],
        data=rad_max,
        unit=u.deg,
    )

    rad_max_2d.write(tmp_path / "rad_max.fits")
    rad_max_read = RadMax2D.read(tmp_path / "rad_max.fits")

    assert np.all(rad_max_read.data == rad_max)
    assert np.all(rad_max_read.data == rad_max_read.data)


def test_rad_max_from_irf():
    e_bins = 3
    o_bins = 2
    energy_axis = MapAxis.from_energy_bounds(1 * u.TeV, 10 * u.TeV, nbin=e_bins, name='energy_true')
    offset_axis = MapAxis.from_bounds(0 * u.deg, 3 * u.deg, nbin=o_bins, name='offset')
    aeff = EffectiveAreaTable2D(
        data=u.Quantity(np.ones((e_bins, o_bins)), u.m**2, copy=False),
        axes=[energy_axis, offset_axis],
        is_pointlike=True,
    )

    with pytest.raises(ValueError):
        # not a point-like IRF
        RadMax2D.from_irf(aeff)

    with pytest.raises(ValueError):
        # missing rad_max
        RadMax2D.from_irf(aeff)

    aeff.meta['RAD_MAX'] = '0.2 deg'
    with pytest.raises(ValueError):
        # invalid format
        RadMax2D.from_irf(aeff)

    aeff.meta['RAD_MAX'] = 0.2
    rad_max = RadMax2D.from_irf(aeff)

    assert rad_max.axes['energy'].nbin == 1
    assert rad_max.axes['offset'].nbin ==  1
    assert rad_max.axes['energy'].edges[0] == aeff.axes['energy_true'].edges[0]
    assert rad_max.axes['energy'].edges[1] == aeff.axes['energy_true'].edges[-1]
    assert rad_max.axes['offset'].edges[0] == aeff.axes['offset'].edges[0]
    assert rad_max.axes['offset'].edges[1] == aeff.axes['offset'].edges[-1]
    assert rad_max.quantity.shape == (1, 1)
    assert rad_max.quantity[0, 0] == 0.2 * u.deg


def test_rad_max_single_bin():
    energy_axis = MapAxis.from_energy_bounds(0.01, 100, 1, unit="TeV")
    offset_axis = MapAxis.from_bounds(0., 5, 1, unit="deg", name="offset", )

    rad_max = RadMax2D(
        data=[[0.1]] * u.deg,
        axes=[energy_axis, offset_axis],
        interp_kwargs={"method": "nearest", "fill_value": None}
    )

    value = rad_max.evaluate(energy=1 * u.TeV, offset=1 * u.deg)
    assert_allclose(value, 0.1 * u.deg)

    value = rad_max.evaluate(energy=[1, 2, 3] * u.TeV, offset=[[1]] * u.deg)
    assert value.shape == (1, 3)
    assert_allclose(value, 0.1 * u.deg)

