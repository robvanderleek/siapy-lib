from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import spectral as sp

from siapy.core.configs import TEST_DATA_DIR
from siapy.entities import Pixels, SpectralImage

image_vnir_hdr_path = TEST_DATA_DIR / "vnir.hdr"
image_vnir_img_path = TEST_DATA_DIR / "vnir.hyspex"
image_swir_hdr_path = TEST_DATA_DIR / "swir.hdr"
image_swir_img_path = TEST_DATA_DIR / "swir.hyspex"


def test_envi_open():
    spectral_image_vnir = SpectralImage.envi_open(
        hdr_path=image_vnir_hdr_path,
        img_path=image_vnir_img_path,
    )
    assert isinstance(spectral_image_vnir, SpectralImage)

    spectral_image_swir = SpectralImage.envi_open(
        hdr_path=image_swir_hdr_path,
        img_path=image_swir_img_path,
    )
    assert isinstance(spectral_image_swir, SpectralImage)


@pytest.fixture
def spectral_images():
    spectral_image_vnir = SpectralImage.envi_open(
        hdr_path=image_vnir_hdr_path,
        img_path=image_vnir_img_path,
    )
    spectral_image_swir = SpectralImage.envi_open(
        hdr_path=image_swir_hdr_path,
        img_path=image_swir_img_path,
    )
    return SimpleNamespace(vnir=spectral_image_vnir, swir=spectral_image_swir)


def test_fixture_spectral_images(spectral_images):
    assert isinstance(spectral_images.vnir, SpectralImage)
    assert isinstance(spectral_images.swir, SpectralImage)


def test_repr(spectral_images):
    assert isinstance(repr(spectral_images.vnir), str)
    assert isinstance(repr(spectral_images.swir), str)


def test_str(spectral_images):
    assert isinstance(str(spectral_images.vnir), str)
    assert isinstance(str(spectral_images.swir), str)


def test_file(spectral_images):
    assert isinstance(
        spectral_images.vnir.file,
        (sp.io.envi.BilFile, sp.io.envi.BipFile, sp.io.envi.BsqFile),
    )
    assert isinstance(
        spectral_images.swir.file,
        (sp.io.envi.BilFile, sp.io.envi.BipFile, sp.io.envi.BsqFile),
    )


def test_metadata(spectral_images):
    vnir_meta = spectral_images.vnir.metadata
    swir_meta = spectral_images.swir.metadata
    assert isinstance(vnir_meta, dict)
    assert isinstance(swir_meta, dict)
    required_keys = ["default bands", "wavelength"]
    assert all(key in vnir_meta.keys() for key in required_keys)
    assert all(key in swir_meta.keys() for key in required_keys)


def test_shape(spectral_images):
    assert isinstance(spectral_images.vnir.shape, tuple)
    assert len(spectral_images.vnir.shape) == 3
    assert isinstance(spectral_images.swir.shape, tuple)
    assert len(spectral_images.swir.shape) == 3


def test_rows(spectral_images):
    assert isinstance(spectral_images.vnir.rows, int)
    assert isinstance(spectral_images.swir.rows, int)


def test_cols(spectral_images):
    assert isinstance(spectral_images.vnir.cols, int)
    assert isinstance(spectral_images.swir.cols, int)


def test_bands(spectral_images):
    assert isinstance(spectral_images.vnir.bands, int)
    assert isinstance(spectral_images.swir.bands, int)


def test_default_bands(spectral_images):
    vnir_db = spectral_images.vnir.default_bands
    swir_db = spectral_images.swir.default_bands
    assert np.array_equal(vnir_db, [55, 41, 12])
    assert np.array_equal(swir_db, [20, 117, 57])


def test_filename(spectral_images):
    assert isinstance(spectral_images.vnir.filepath, Path)
    assert isinstance(spectral_images.swir.filepath, Path)
    assert spectral_images.vnir.filepath.name == image_vnir_img_path.name
    assert spectral_images.swir.filepath.name == image_swir_img_path.name


def test_wavelengths(spectral_images):
    vnir_wave = spectral_images.vnir.wavelengths
    swir_wave = spectral_images.swir.wavelengths
    assert isinstance(vnir_wave, list)
    assert all(isinstance(w, float) for w in vnir_wave)
    assert len(vnir_wave) == 160
    assert isinstance(swir_wave, list)
    assert all(isinstance(w, float) for w in swir_wave)
    assert len(swir_wave) == 288


def test_to_numpy(spectral_images):
    spectral_image_vnir = spectral_images.vnir.to_numpy()
    spectral_image_swir = spectral_images.swir.to_numpy()
    assert isinstance(spectral_image_vnir, np.ndarray)
    assert isinstance(spectral_image_swir, np.ndarray)


def test_remove_nan(spectral_images):
    image = np.array([[[1, 2, np.nan], [4, 2, 6]], [[np.nan, 8, 9], [10, 11, 12]]])
    result = spectral_images.vnir._remove_nan(image.copy())

    assert np.array_equal(result[0, 0], np.array([0, 0, 0]))
    assert np.array_equal(result[0, 1], np.array([4, 2, 6]))
    assert np.array_equal(result[1, 0], np.array([0, 0, 0]))
    assert np.array_equal(result[1, 1], np.array([10, 11, 12]))

    # Call the _remove_nan method with a non-default nan_value
    result = spectral_images.vnir._remove_nan(image.copy(), nan_value=99)

    # Check that all nan values have been replaced with 99
    assert (result == 99).sum() == 6


def test_to_signatures(spectral_images):
    spectral_image_vnir = spectral_images.vnir
    iterable = [(1, 2), (3, 4), (5, 6)]

    pixels = Pixels.from_iterable(iterable)
    signatures = spectral_image_vnir.to_signatures(pixels)

    assert np.array_equal(
        signatures.signals.df.iloc[0].to_numpy(),
        spectral_images.vnir.to_numpy()[2, 1, :],
    )
    assert np.array_equal(
        signatures.signals.df.iloc[1].to_numpy(),
        spectral_images.vnir.to_numpy()[4, 3, :],
    )
    assert np.array_equal(
        signatures.signals.df.iloc[2].to_numpy(),
        spectral_images.vnir.to_numpy()[6, 5, :],
    )

    assert np.array_equal(signatures.pixels.df.iloc[0].to_numpy(), iterable[0])
    assert np.array_equal(signatures.pixels.df.iloc[1].to_numpy(), iterable[1])
    assert np.array_equal(signatures.pixels.df.iloc[2].to_numpy(), iterable[2])


def test_mean(spectral_images):
    spectral_image_vnir = spectral_images.vnir

    mean_all = spectral_image_vnir.mean()
    assert isinstance(mean_all, float)
    assert np.isclose(mean_all, np.nanmean(spectral_image_vnir.to_numpy()))

    mean_axis0 = spectral_image_vnir.mean(axis=0)
    assert isinstance(mean_axis0, np.ndarray)
    assert mean_axis0.shape == spectral_image_vnir.to_numpy().shape[1:]
    assert np.allclose(mean_axis0, np.nanmean(spectral_image_vnir.to_numpy(), axis=0))

    mean_axis1 = spectral_image_vnir.mean(axis=1)
    assert isinstance(mean_axis1, np.ndarray)
    assert mean_axis1.shape == (
        spectral_image_vnir.to_numpy().shape[0],
        spectral_image_vnir.to_numpy().shape[2],
    )
    assert np.allclose(mean_axis1, np.nanmean(spectral_image_vnir.to_numpy(), axis=1))

    mean_axis2 = spectral_image_vnir.mean(axis=2)
    assert isinstance(mean_axis2, np.ndarray)
    assert mean_axis2.shape == spectral_image_vnir.to_numpy().shape[:2]
    assert np.allclose(mean_axis2, np.nanmean(spectral_image_vnir.to_numpy(), axis=2))

    mean_axis_tuple = spectral_image_vnir.mean(axis=(0, 1))
    assert isinstance(mean_axis_tuple, np.ndarray)
    assert mean_axis_tuple.shape == (spectral_image_vnir.to_numpy().shape[2],)
    assert np.allclose(
        mean_axis_tuple, np.nanmean(spectral_image_vnir.to_numpy(), axis=(0, 1))
    )
