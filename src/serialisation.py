"""[De]Serialisation of JSON messages. (Can't Robots speak JSON?)"""

from abc import abstractmethod
from collections import OrderedDict

from marshmallow import Schema, fields as f, post_load
from marshmallow_enum import EnumField
from marshmallow_oneofschema import OneOfSchema

from dto import (
    Coordinates,
    BearingType,
    NewRobotMessage,
    MessageType,
    MoveMessage,
    AsteroidMessage,
    MovementType,
    RobotMessage,
)


class BaseSchema(Schema):
    """Common functionality for derived marshmallow schemas."""

    class Meta:
        ordered = True

    @staticmethod
    @abstractmethod
    def declare_type() -> type:
        """Return the type to deserialise to."""
        ...

    @post_load
    def create_instance(self, data: dict, **kwargs):
        """Create an instance of the type this schema deserialises to."""
        return self.declare_type()(**data)


class CoordinatesSchema(BaseSchema):
    """Marshmallow schema for Coordinates."""
    x = f.Int()
    y = f.Int()

    @staticmethod
    def declare_type() -> type:
        return Coordinates


class AsteroidMessageSchema(BaseSchema):
    """Marshmallow schema for Asteroid."""
    size = f.Nested(CoordinatesSchema)

    @staticmethod
    def declare_type() -> type:
        return AsteroidMessage


class MovementMessageSchema(BaseSchema):
    """Marshmallow schema for MovementMessage."""
    movement = EnumField(MovementType, by_value=True)

    @staticmethod
    def declare_type() -> type:
        return MoveMessage


class NewRobotMessageSchema(BaseSchema):
    """Marshmallow schema for NewRobotMessage."""
    position = f.Nested(CoordinatesSchema)
    bearing = EnumField(BearingType, by_value=True)

    @staticmethod
    def declare_type() -> type:
        return NewRobotMessage


class RobotMessageSchema(BaseSchema):
    """Marshmallow schema for RobotMessage."""
    position = f.Nested(CoordinatesSchema)
    bearing = EnumField(BearingType, by_value=True)

    @staticmethod
    def declare_type() -> type:
        return RobotMessage


class MessageSchema(OneOfSchema):
    """A schema which deserialises to the concrete type declared in the JSON."""
    type_schemas = {
        MessageType.Asteroid.value: AsteroidMessageSchema,
        MessageType.NewRobot.value: NewRobotMessageSchema,
        MessageType.Move.value: MovementMessageSchema,
        MessageType.Robot.value: RobotMessageSchema,
    }

    def get_obj_type(self, obj):
        """Return the relevant type_schemas key."""
        match obj:
            case AsteroidMessage():
                return MessageType.Asteroid.value
            case RobotMessage():
                return MessageType.Robot.value
            case NewRobotMessage():
                return MessageType.NewRobot.value
            case MoveMessage():
                return MessageType.Move.value
            case _:
                raise RuntimeError(f'Unknown message type: {obj}')

    def dump(self, *args, **kwargs) -> dict:
        """Override of Schema.dump() which puts JSON properties in the order
        proscribed by the ESA.
        """
        data: OrderedDict = super().dump(*args, **kwargs)
        if 'type' in data.keys():
            keys = [k for k in data.keys() if k != 'type']
            for k in keys:
                v = data.pop(k)
                data[k] = v
        return data


AnyMessage = AsteroidMessage | NewRobotMessage | MoveMessage | RobotMessage


def deserialise_message(instruction: str) -> AnyMessage:
    """Deserialise a JSON string to a concrete message type."""
    return MessageSchema().loads(instruction)


def serialise_message(message: AnyMessage) -> str:
    """Serialise a message instance to JSON string."""
    return MessageSchema().dumps(message)
