from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from scipy.spatial import ConvexHull

from siapy.entities.pixels import Pixels


@dataclass
class Shape(ABC):
    def __init__(self, pixels: Pixels, label: str | None = None):
        self._pixels = pixels
        self._label = label

    @classmethod
    def from_shape_type(
        cls,
        shape_type: Literal["rectangle", "point", "freedraw"],
        pixels: Pixels,
        label: str | None = None,
    ) -> "Shape":
        types_map: dict[str, type[Shape]] = {
            "rectangle": Rectangle,
            "point": Point,
            "freedraw": FreeDraw,
        }
        if shape_type in types_map:
            return types_map[shape_type](pixels=pixels, label=label)
        else:
            raise ValueError(f"Unsupported shape type: {shape_type}")

    @property
    def pixels(self) -> Pixels:
        return self._pixels

    @property
    def label(self) -> str | None:
        return self._label

    @abstractmethod
    def convex_hull(self):
        raise NotImplementedError(
            "convex_hull() method is not implemented for the base Shape class."
        )


class Rectangle(Shape):
    def convex_hull(self) -> Pixels:
        # Rectangle is defined by two opposite corners
        u1, u2 = self.pixels.u()
        v1, v2 = self.pixels.v()

        pixels_inside = []
        for u_coord in range(min(u1, u2), max(u1, u2) + 1):
            for v_coord in range(min(v1, v2), max(v1, v2) + 1):
                pixels_inside.append((u_coord, v_coord))
        return Pixels.from_iterable(pixels_inside)


class Point(Shape):
    def convex_hull(self) -> Pixels:
        return self.pixels


class FreeDraw(Shape):
    def convex_hull(self) -> Pixels:
        if len(self.pixels) < 3:
            return self.pixels
        points = self.pixels.to_numpy()
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]
        return Pixels.from_iterable(hull_points.tolist())
