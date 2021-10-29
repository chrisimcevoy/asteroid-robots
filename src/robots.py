"""Robot instruction processing."""

import sys
from dataclasses import dataclass
from pathlib import Path

import marshmallow.exceptions

from dto import (
    Coordinates,
    BearingType,
    AsteroidMessage,
    NewRobotMessage,
    MoveMessage,
    RobotMessage,
    MovementType,
)
from serialisation import deserialise_message, serialise_message

TURN_RIGHT_MAP: dict[BearingType, BearingType] = {
    BearingType.North: BearingType.East,
    BearingType.East: BearingType.South,
    BearingType.South: BearingType.West,
    BearingType.West: BearingType.North
}

TURN_LEFT_MAP: dict[BearingType, BearingType] = {
    v: k for k, v in TURN_RIGHT_MAP.items()
}


def validate_instructions_file_path(path: Path) -> Path:
    """Parse and validate the instructions file path."""

    if not path.exists():
        raise FileNotFoundError(path)

    if not path.is_file():
        raise ValueError(f'Path provided is not a file ({path})')

    return path


@dataclass
class Asteroid:
    size: Coordinates

    def contains(self, coordinates: Coordinates) -> bool:
        """Return True if the coordinates fall within the Asteroid map."""
        return (
            coordinates.x in range(self.size.x + 1)
            and coordinates.y in range(self.size.y + 1)
        )


@dataclass
class Robot:
    """A Robot."""
    position: Coordinates
    bearing: BearingType

    def move(self, movement: MovementType) -> None:
        """Move the Robot according to the instruction."""
        match movement:
            case MovementType.Left:
                self.bearing = TURN_LEFT_MAP[self.bearing]
            case MovementType.Right:
                self.bearing = TURN_RIGHT_MAP[self.bearing]
            case MovementType.Forward:
                match self.bearing:
                    case BearingType.North:
                        self.position.y += 1
                    case BearingType.South:
                        self.position.y -= 1
                    case BearingType.East:
                        self.position.x += 1
                    case BearingType.West:
                        self.position.x -= 1
                    case _:
                        raise RuntimeError(f'Unsupported movement: {movement}')

    def generate_message(self) -> RobotMessage:
        """Generate a RobotMessage."""
        return RobotMessage(self.position, self.bearing)


def broadcast_message(robot: Robot | None) -> None:
    """Broadcast the position of a Robot, if it exists."""
    if robot:
        msg = robot.generate_message()
        print(serialise_message(msg))


def process_instructions(instructions_file_path: Path) -> None:
    """Process instructions and pass them to the Robots."""
    asteroid: Asteroid | None = None
    robot: Robot | None = None

    with open(instructions_file_path) as f:
        while line := f.readline(100):
            try:
                message = deserialise_message(line)
            except marshmallow.exceptions.ValidationError:
                raise ValueError(f'Invalid instruction: "{line}"')

            match message:
                case AsteroidMessage():
                    asteroid = Asteroid(message.size)
                case NewRobotMessage():
                    if not asteroid:
                        raise ValueError('Cannot create a Robot before the asteroid is mapped!')
                    broadcast_message(robot)
                    robot = Robot(message.position, message.bearing)
                case MoveMessage():
                    if not asteroid:
                        raise ValueError('Cannot process a movement before the asteroid has been mapped!')
                    if not robot:
                        raise ValueError(f'Cannot process a movement before the robot arrives!')
                    robot.move(message.movement)
                    if not asteroid.contains(robot.position):
                        raise RuntimeError(f"Robot wandered off the grid! :(")
                case _:
                    raise ValueError(f'Invalid instruction type: {message}')

        broadcast_message(robot)


def main():
    """Validate arguments and kick off instruction processing."""
    try:
        path: str = sys.argv[1]
    except IndexError:
        raise ValueError(f'Instructions file path not provided!') from None

    path: Path = validate_instructions_file_path(Path(path))
    process_instructions(path)


if __name__ == '__main__':
    main()
