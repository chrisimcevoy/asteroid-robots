import pytest

from serialisation import deserialise_message, serialise_message


@pytest.mark.parametrize('instruction', [
    '{"type": "asteroid", "size": {"x": 5, "y": 5}}',
    '{"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"}',
    '{"type": "move", "movement": "turn-left"}',
    '{"type": "robot", "position": {"x": 1, "y": 3}, "bearing": "north"}',
])
def test_serialisation(instruction: str) -> None:
    message = deserialise_message(instruction)
    instruction_2 = serialise_message(message)
    assert instruction_2 == instruction
