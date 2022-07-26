from __future__ import annotations

import copy
from collections import deque

import numpy as np

from rubiks_cube.utils import Color, TupleSlice
from rubiks_cube.utils import Direction as Direc

# Directions that indicates whether a "piece" should be inverted.
_LIST_DIRECTIONS_TO_INV = [
    {Direc.U, Direc.R}, {Direc.U},
    {Direc.D, Direc.L}, {Direc.D}
]


def _color_to_str(list_of_colors: list[Color]) -> list[str]:
    """Function that maps the list of colors into a list of strings."""
    return [repr(c) for c in list_of_colors]


def _invert_piece(piece, direction=-1) -> list[Color]:
    """Function that invert a piece if the 'direction' is negative. Otherwise, it returns the same list."""
    if direction < 0:
        return list(reversed(piece))
    return piece


def _rotate_pieces(list_of_pieces, times) -> list[list[Color]]:
    """Function that rotates the given list of pieces depending on the parameter 'times'."""
    even, odd = [1, 1, -1, -1], [1, -1, -1, 1]
    list_of_directions = [even, odd, even, odd]
    new_list_of_pieces = deque()
    for piece, directions in zip(list_of_pieces, list_of_directions):
        new_list_of_pieces.append(_invert_piece(piece, directions[times]))
    new_list_of_pieces.rotate(times)
    return list(new_list_of_pieces)


def _as_tuple(arr: np.ndarray) -> tuple[tuple, ...]:
    return tuple([tuple(row) for row in arr])


class Face:
    """Class that represents a face of the Rubik's Cube."""

    def __init__(self, central_face: np.ndarray[Color] | list[list[Color]]):
        # Central Face
        self.central_face: np.ndarray[Color] = np.asarray(central_face)

        # Shape
        self.shape: tuple[int, int] = self.central_face.shape

        # Faces
        self.up: Face | None = None
        self.right: Face | None = None
        self.down: Face | None = None
        self.left: Face | None = None

        self._direc_list: list[Direc] | None = None
        self._slice_list: list[TupleSlice] | None = None

    @classmethod
    def from_color(cls, color: Color | str, shape: tuple[int, int]) -> Face:
        """Factory method that creates a Face given a color and a shape."""
        return cls(np.tile(Color(color), shape))

    def __getitem__(self, index) -> np.ndarray[Color]:
        return self.central_face.__getitem__(index)

    def __setitem__(self, index, item):
        self.central_face.__setitem__(index, item)

    def __eq__(self, other):
        # Self check
        if other is self:
            return True
        # Null check
        if other is None:
            return False
        if not isinstance(other, Face):
            return False
        other: Face
        return (self.central_face == other.central_face).all()

    def __hash__(self):
        return hash(_as_tuple(self.central_face))

    def __copy__(self) -> Face:
        central_face = copy.copy(self.central_face)

        new = self.__class__(central_face)

        new.__dict__.update(self.__dict__)

        return new

    def __deepcopy__(self, memo=None) -> Face:
        if memo is None:
            memo = {}

        central_face = copy.deepcopy(self.central_face, memo)

        new = self.__class__(central_face)

        new.__dict__ = copy.deepcopy(self.__dict__, memo)

        return new

    @property
    def faces(self) -> tuple[Face]:
        """Iterates over the other faces adjacent tp the current face."""
        return self.up, self.right, self.down, self.left

    def _invert_pieces(self, list_of_pieces) -> list[list[Color]]:
        """Invert some pieces if it is necessary."""
        to_return: list[list[Color]] = [list(elem) for elem in list_of_pieces]
        for i, dir_set in enumerate(_LIST_DIRECTIONS_TO_INV):
            if self._direc_list[i] in dir_set:
                to_return[i] = _invert_piece(to_return[i])
        return to_return

    @property
    def pieces(self) -> list[list[Color]]:
        """Returns the pieces adjacent of the current face."""
        u_s, r_s, d_s, l_s = self._slice_list
        return self._invert_pieces([self.up[u_s], self.right[r_s], self.down[d_s], self.left[l_s]])

    @pieces.setter
    def pieces(self, value_to_set):
        """Sets the pieces to the current face."""
        u_s, r_s, d_s, l_s = self._slice_list
        self.up[u_s], self.right[r_s], self.down[d_s], self.left[l_s] = self._invert_pieces(value_to_set)

    def repr_central_face(self, space: int = 0) -> str:
        """Returns a representation of the central face."""
        str_to_return = ""
        for row in self.central_face:
            str_to_return += " " * space + " ".join([repr(e) for e in row]) + "\n"
        return str_to_return[:-1]

    def __repr__(self):
        # In the case that the other faces are not set.
        for f in self.faces:
            if f is None:
                return self.repr_central_face()
        # Pieces as string
        p_up, p_right, p_down, p_left = [_color_to_str(loc) for loc in self.pieces]
        # Up
        str_to_return = "   "
        str_to_return += " ".join(p_up) + "\n\n"
        # Left, central and right
        central_face_list = self.repr_central_face().split("\n")
        for left, central, right in zip(p_left, central_face_list, p_right):
            str_to_return += f"{left}  {central}  {right}\n"
        # Down
        str_to_return += "\n   " + " ".join(p_down)
        return str_to_return

    def add_faces(self, up_tuple, right_tuple, down_tuple, left_tuple):
        """Attach the faces to the current face."""
        # TODO: Agregar algo para que valide que las caras realmente se ajusten? onda que
        #  si la cara central es de (2, 2) que el de la izquierda sea de (2, 100) y no de (100, 100).
        (up, up_d), (right, right_d), (down, down_d), (left, left_d) = up_tuple, right_tuple, down_tuple, left_tuple
        self.up, self.right, self.down, self.left = up, right, down, left
        self._direc_list: list[Direc] = [Direc(s) for s in [up_d, right_d, down_d, left_d]]
        self._slice_list: list[TupleSlice] = [d.generate_slice() for d in self._direc_list]

    def rotate(self, times: int):
        """Rotate the face at the desired times."""
        times = times % 4
        # TODO: Agregar validadores para chequear que el movimiento se puede hacer (?)
        self.pieces = _rotate_pieces(self.pieces, times)
        self.central_face = np.rot90(self.central_face, 4 - times)
