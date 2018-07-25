# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
import pytest
import numpy as np
from numpy.testing.utils import assert_allclose
from astropy.convolution import Gaussian2DKernel
from ...utils.testing import requires_dependency, requires_data
from ...utils.scripts import make_path
from ...maps.utils import read_fits_hdus
from ...detect import TSMapEstimator


@requires_dependency('scipy')
@requires_dependency('skimage')
@requires_data('gammapy-extra')
def test_compute_ts_map():
    """Minimal test of compute_ts_image"""
    filename = '$GAMMAPY_EXTRA/test_datasets/unbundled/poisson_stats_image/input_all.fits.gz'
    maps = read_fits_hdus(filename)

    kernel = Gaussian2DKernel(5)

    ts_estimator = TSMapEstimator(method='leastsq iter', n_jobs=4)
    result = ts_estimator.run(maps, kernel=kernel)

    assert_allclose(1714.23, result['ts'].data[99, 99], rtol=1e-2)
    assert_allclose(3, result['niter'].data[99, 99])
    assert_allclose(1.02e-09, result['flux'].data[99, 99], rtol=1e-2)
    assert_allclose(3.84e-11, result['flux_err'].data[99, 99], rtol=1e-2)
    assert_allclose(1.10e-09, result['flux_ul'].data[99, 99], rtol=1e-2)


@requires_dependency('scipy')
@requires_dependency('skimage')
@requires_data('gammapy-extra')
def test_compute_ts_map_downsampled():
    """Minimal test of compute_ts_image"""
    filename = '$GAMMAPY_EXTRA/test_datasets/unbundled/poisson_stats_image/input_all.fits.gz'
    maps = read_fits_hdus(filename)

    kernel = Gaussian2DKernel(2.5)

    ts_estimator = TSMapEstimator(method='root brentq', n_jobs=4)
    result = ts_estimator.run(maps, kernel=kernel, downsampling_factor=2)

    assert_allclose(1675.28, result['ts'].data[99, 99], rtol=1e-2)
    assert_allclose(7, result['niter'].data[99, 99])
    assert_allclose(1.02e-09, result['flux'].data[99, 99], rtol=1e-2)
    assert_allclose(3.84e-11, result['flux_err'].data[99, 99], rtol=1e-2)
    assert_allclose(1.10e-09, result['flux_ul'].data[99, 99], rtol=1e-2)

