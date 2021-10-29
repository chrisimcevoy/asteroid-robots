from pathlib import Path
from uuid import uuid4

import pytest

from dto import Coordinates
from robots import Robot, Asteroid


@pytest.fixture
def asteroid():
    return Asteroid(Coordinates(5, 5))


@pytest.fixture
def robot(request):
    return Robot(Coordinates(0, 0), request.param)


@pytest.fixture
def path(request):
    text = '\n'.join(request.param)
    p = Path().parent / f'{uuid4()}.txt'
    p.write_text(text)
    yield p
    p.unlink(missing_ok=True)
