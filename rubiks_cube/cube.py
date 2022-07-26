from __future__ import annotations

import copy

from rubiks_cube.faces import Face
from rubiks_cube.movements import CubeMove
from rubiks_cube.utils import Color, Direction

# Directions
_U, _R, _D, _L = Direction.U, Direction.R, Direction.D, Direction.L


class NotPermittedMovementError(Exception):
    """
    Custom error in the cases of a user make a wrong movement.
    """
    pass


class RubikCube:
    """Class that represents a Rubik's Cube."""

    def __init__(self, up: Face, left: Face, front: Face, right: Face, back: Face, down: Face,
                 permitted_movements: set[CubeMove] = None):
        # TODO: Podría ser util tener un validador para determinar si las caras coinciden 
        #  en las dimensiones.

        # Different Faces
        self.front: Face = front
        self.back: Face = back
        self.left: Face = left
        self.right: Face = right
        self.up: Face = up
        self.down: Face = down

        # Attach every face with its correspondent faces
        front.add_faces(
            up_tuple=(up, _D), right_tuple=(right, _L), down_tuple=(down, _U), left_tuple=(left, _R))
        back.add_faces(
            up_tuple=(up, _U), right_tuple=(left, _L), down_tuple=(down, _D), left_tuple=(right, _R))
        left.add_faces(
            up_tuple=(up, _L), right_tuple=(front, _L), down_tuple=(down, _L), left_tuple=(back, _R))
        right.add_faces(
            up_tuple=(up, _R), right_tuple=(back, _L), down_tuple=(down, _R), left_tuple=(front, _R))
        up.add_faces(
            up_tuple=(back, _U), right_tuple=(right, _U), down_tuple=(front, _U), left_tuple=(left, _U))
        down.add_faces(
            up_tuple=(front, _D), right_tuple=(right, _D), down_tuple=(back, _D), left_tuple=(left, _D))

        # Set of permitted movements
        self.permitted_movements: set[CubeMove] = permitted_movements or {m for m in CubeMove}
        
        # Dimensions
        self.dims = self.front.shape[0], self.front.shape[1], self.right.shape[1]

    @classmethod
    def from_dims(cls, dims: tuple[int, int, int], permitted_movements: set[CubeMove] = None) -> RubikCube:
        """
        Factory method that generates a RubikCube instance given the dimensions and permitted movements.

        :param dims: The dimensions in the standard (height, width, length).
        :param permitted_movements: A set of permitted movements.
        :return: An instance of the Rubik's Cube with the desired dimension.
        """
        height, width, length = dims
        cls_to_return = cls(
            front=Face.from_color(Color.RED, (height, width)), back=Face.from_color(Color.ORANGE, (height, width)),
            left=Face.from_color(Color.GREEN, (height, length)), right=Face.from_color(Color.BLUE, (height, length)),
            up=Face.from_color(Color.WHITE, (length, width)), down=Face.from_color(Color.YELLOW, (length, width)),
            permitted_movements=permitted_movements,
        )
        return cls_to_return

    @property
    def faces(self):
        """Iterates over every face in the current cube."""
        return self.up, self.left, self.front, self.right, self.back, self.down

    def __eq__(self, other):
        if other is self:
            return True
        if other is None:
            return False
        if not isinstance(other, RubikCube):
            return False
        other: RubikCube
        for f_self, f_other in zip(self.faces, other.faces):
            if f_self != f_other:
                return False
        return True

    def __hash__(self):
        return hash(self.faces)

    def __copy__(self) -> RubikCube:
        up = copy.copy(self.up)
        left = copy.copy(self.left)
        front = copy.copy(self.front)
        right = copy.copy(self.right)
        back = copy.copy(self.back)
        down = copy.copy(self.down)
        permitted_movements = copy.copy(self.permitted_movements)

        new = self.__class__(up, left, front, right, back, down, permitted_movements)
        new.__dict__.update(self.__dict__)

        return new

    def __deepcopy__(self, memo=None) -> RubikCube:
        """
        To use prototype pattern. It makes a deep copy of the current instance
        :return: A deepcopy of the Rubik's cube.
        """
        memo = memo or {}

        up = copy.deepcopy(self.up, memo)
        left = copy.deepcopy(self.left, memo)
        front = copy.deepcopy(self.front, memo)
        right = copy.deepcopy(self.right, memo)
        back = copy.deepcopy(self.back, memo)
        down = copy.deepcopy(self.down, memo)
        permitted_movements = copy.deepcopy(self.permitted_movements, memo)

        new = self.__class__(up, left, front, right, back, down, permitted_movements)
        new.__dict__ = copy.deepcopy(self.__dict__, memo)

        return new

    def __repr__(self):
        _, _, length = self.dims

        # Up face
        str_to_return = "\n"
        str_to_return += self.up.repr_central_face(2 * length + 1) + "\n\n"

        # Left, front, right and back face
        left_list = self.left.repr_central_face().split("\n")
        front_list = self.front.repr_central_face().split("\n")
        right_list = self.right.repr_central_face().split("\n")
        back_list = self.back.repr_central_face().split("\n")
        for le, fr, ri, ba in zip(left_list, front_list, right_list, back_list):
            str_to_return += f"{le}  {fr}  {ri}  {ba}\n"
        str_to_return += "\n"

        # Down face
        str_to_return += self.down.repr_central_face(2 * length + 1)

        return str_to_return

    def _make_a_move_from_cube_move(self, movement: CubeMove) -> RubikCube:
        """Make a copy with the selected move."""
        # Check if the movement is permitted (or if it is even a movement).
        if movement not in self.permitted_movements:
            raise NotPermittedMovementError(
                f"Movement not allowed. Please choose one of the list: {self.permitted_movements}.")
        self_copy: RubikCube = copy.deepcopy(self)
        movement.move_the_cube(self_copy)
        return self_copy

    def _make_movements_from_list(self, list_of_moves: list[CubeMove]) -> RubikCube:
        """Make movements from a list of CubeMoves."""
        rc = self
        for move in list_of_moves:
            rc = rc._make_a_move_from_cube_move(move)
        return rc

    def _make_movements_from_str(self, str_of_moves: str) -> RubikCube:
        """Make movements from a string, separated by spaces."""
        list_of_str: list[str] = str_of_moves.split()
        list_of_moves: list[CubeMove] = [CubeMove.parse_move(m_str) for m_str in list_of_str]
        return self._make_movements_from_list(list_of_moves)

    def make_movements(self, movement: CubeMove | list[CubeMove] | str) -> RubikCube:
        """
        Make a move on the Rubik's Cube given a movement. It can be whether a CubeMove, a list of CubeMoves or a
        string with representations of movements.

        :param movement: The movement to apply on the Rubik's cube.
        :return: The Rubik's cube with the movement applied.
        """
        if isinstance(movement, CubeMove):
            return self._make_a_move_from_cube_move(movement)
        if isinstance(movement, list):
            return self._make_movements_from_list(movement)
        if isinstance(movement, str):
            return self._make_movements_from_str(movement)
        raise NotPermittedMovementError("Please give a list of CubeMove or give a valid string format.")
