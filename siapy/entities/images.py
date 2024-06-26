# mypy: ignore-errors
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import spectral as sp
from PIL import Image, ImageOps

from .shapes import Shape
from .signatures import Signatures

if TYPE_CHECKING:
    from ..core.types import SpectralType
    from .pixels import Pixels


@dataclass
class SpectralImage:
    def __init__(
        self,
        sp_file: "SpectralType",
    ):
        self._sp_file = sp_file
        self._geometric_shapes: list[Shape] = []

    def __repr__(self) -> str:
        return repr(self._sp_file)

    def __str__(self) -> str:
        return str(self._sp_file)

    @classmethod
    def envi_open(
        cls, *, hdr_path: str | Path, img_path: str | Path | None = None
    ) -> "SpectralImage":
        sp_file = sp.envi.open(file=hdr_path, image=img_path)
        if isinstance(sp_file, sp.io.envi.SpectralLibrary):
            raise ValueError("Opened file of type SpectralLibrary")
        return cls(sp_file)

    @property
    def file(self) -> "SpectralType":
        return self._sp_file

    @property
    def metadata(self) -> dict[str, Any]:
        return self._sp_file.metadata

    @property
    def shape(self) -> tuple[int, int, int]:
        rows = self._sp_file.nrows
        samples = self._sp_file.ncols
        bands = self._sp_file.nbands
        return (rows, samples, bands)

    @property
    def rows(self) -> int:
        return self._sp_file.nrows

    @property
    def cols(self) -> int:
        return self._sp_file.ncols

    @property
    def bands(self) -> int:
        return self._sp_file.nbands

    @property
    def default_bands(self) -> list[int]:
        db = self.metadata["default bands"]
        return list(map(int, db))

    @property
    def filepath(self) -> Path:
        return Path(self._sp_file.filename)

    @property
    def wavelengths(self) -> list[float]:
        wavelength_data = self._sp_file.metadata["wavelength"]
        return list(map(float, wavelength_data))

    @property
    def geometric_shapes(self) -> list["Shape"]:
        return self._geometric_shapes

    @geometric_shapes.setter
    def geometric_shapes(self, shapes: list["Shape"]):
        if not all(isinstance(shape, Shape) for shape in shapes):
            raise ValueError("All items in the list must be instances of Shape")
        self._geometric_shapes = shapes

    def to_display(self, equalize: bool = True) -> Image.Image:
        image_3ch = self._sp_file.read_bands(self.default_bands)
        image_3ch = self._remove_nan(image_3ch, nan_value=0)
        image_3ch[:, :, 0] = image_3ch[:, :, 0] / (image_3ch[:, :, 0].max() / 255.0)
        image_3ch[:, :, 1] = image_3ch[:, :, 1] / (image_3ch[:, :, 1].max() / 255.0)
        image_3ch[:, :, 2] = image_3ch[:, :, 2] / (image_3ch[:, :, 2].max() / 255.0)
        image = Image.fromarray(image_3ch.astype("uint8"))
        if equalize:
            image = ImageOps.equalize(image)
        return image

    def to_numpy(self, nan_value: float | None = None) -> np.ndarray:
        image = self._sp_file[:, :, :]
        if nan_value is not None:
            image = self._remove_nan(image, nan_value)
        return image

    def to_signatures(self, pixels: "Pixels") -> Signatures:
        image_arr = self.to_numpy()
        signatures = Signatures.from_array_and_pixels(image_arr, pixels)
        return signatures

    def mean(self, axis: int | tuple[int] | None = None) -> float | np.ndarray:
        image_arr = self.to_numpy()
        return np.nanmean(image_arr, axis=axis)

    def _remove_nan(self, image: np.ndarray, nan_value: float = 0.0) -> np.ndarray:
        image_mask = np.bitwise_not(np.bool_(np.isnan(image).sum(axis=2)))
        image[~image_mask] = nan_value
        return image
