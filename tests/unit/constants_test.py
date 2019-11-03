from jarpc import constants


def test_NoValue_object():
    """
    Should ensure the NoValue property is an object
    """
    assert isinstance(constants.NoValue, object)
