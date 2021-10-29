from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest

from dto import Coordinates, MovementType, BearingType
from robots import Asteroid, Robot, validate_instructions_file_path


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize('path,expectation', [
    (Path(__file__).parent / 'worked-example.txt', does_not_raise()),
    (Path().parent, pytest.raises(ValueError)),
    (Path(str(uuid4)), pytest.raises(FileNotFoundError)),
])
def test_validate_instructions_file_path(path: Path, expectation) -> None:
    with expectation:
        path = validate_instructions_file_path(path)
        assert isinstance(path, Path)
        assert path.exists()
        assert path.is_file()


class TestAsteroid:

    @pytest.mark.parametrize('coordinates,expected', [
        (Coordinates(0, 0), True),
        (Coordinates(5, 5), True),
        (Coordinates(-1, 0), False),
        (Coordinates(0, -1), False),
        (Coordinates(6, 0), False),
        (Coordinates(0, 6), False),
    ])
    def test_asteroid_contains(self, asteroid: Asteroid, coordinates: Coordinates, expected: bool) -> None:
        assert expected is asteroid.contains(coordinates)


class TestRobot:

    origin = Coordinates(0, 0)

    def assert_is_origin(self, coordinates: Coordinates) -> None:
        assert coordinates.x == self.origin.x
        assert coordinates.y == self.origin.y

    @pytest.mark.parametrize('initial,movement,expected', [
        (BearingType.North, MovementType.Left, BearingType.West),
        (BearingType.West, MovementType.Left, BearingType.South),
        (BearingType.South, MovementType.Left, BearingType.East),
        (BearingType.East, MovementType.Left, BearingType.North),
        (BearingType.North, MovementType.Right, BearingType.East),
        (BearingType.West, MovementType.Right, BearingType.North),
        (BearingType.South, MovementType.Right, BearingType.West),
        (BearingType.East, MovementType.Right, BearingType.South),
    ])
    def test_move_turn(self,
                       initial: BearingType,
                       movement: MovementType,
                       expected: BearingType) -> None:
        robot = Robot(Coordinates(self.origin.x, self.origin.y), initial)
        robot.move(movement)
        assert robot.bearing is expected
        self.assert_is_origin(robot.position)

    @pytest.mark.parametrize('robot,attr,delta', [
        (BearingType.North, 'y', 1),
        (BearingType.North, 'x', 0),
        (BearingType.West, 'y', 0),
        (BearingType.West, 'x', -1),
        (BearingType.South, 'y', -1),
        (BearingType.South, 'x', 0),
        (BearingType.East, 'y', 0),
        (BearingType.East, 'x', 1),
    ], indirect=['robot'])
    def test_move_forward(self, robot: Robot, attr: str, delta: int) -> None:
        initial_bearing = robot.bearing
        expected: int = getattr(robot.position, attr) + delta
        robot.move(MovementType.Forward)
        assert getattr(robot.position, attr) == expected
        assert robot.bearing == initial_bearing
