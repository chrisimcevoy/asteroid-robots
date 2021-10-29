import pytest

from dto import Coordinates
from robots import Robot, Asteroid


@pytest.fixture
def asteroid():
    return Asteroid(Coordinates(5, 5))


@pytest.fixture
def robot(request):
    return Robot(Coordinates(0, 0), request.param)
