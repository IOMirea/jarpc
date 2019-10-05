from yarpc import Client


def test_creation():
    assert Client("example")
