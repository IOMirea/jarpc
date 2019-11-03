from jarpc import StatusCode

all_enumaration_types = [
    StatusCode.SUCCESS,
    StatusCode.BAD_FORMAT,
    StatusCode.UNKNOWN_COMMAND,
    StatusCode.BAD_PARAMS,
    StatusCode.INTERNAL_ERROR,
]


def test_properties_values():
    """
    Should ensure that variables are set to their expected values
    """

    vals = [0, 1, 2, 3, 4]
    for enum in all_enumaration_types:
        assert enum.value == vals[enum.value]


def test_properties_types():
    """
    Should have the enum variable of type Enum
    """

    for enum in all_enumaration_types:
        assert type(enum) == StatusCode
