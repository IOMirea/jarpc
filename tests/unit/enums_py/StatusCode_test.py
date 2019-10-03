import unittest
from iomirea_rpc.enums import StatusCode

class enums_StatusCode_TestCase(unittest.TestCase):
    """
    Testing the StatusCode Class
    """

    def test_enums_variables_values(self):
        """
        Should ensure that variables are set to their expected values
        """

        all_enumarations_values = [
            StatusCode.SUCCESS.value,
            StatusCode.BAD_FORMAT.value,
            StatusCode.UNKNOWN_COMMAND.value,
            StatusCode.BAD_PARAMS.value,
            StatusCode.INTERNAL_ERROR.value
        ]
        
        enum_val = [0, 1, 2, 3, 4]
        for enum in all_enumarations_values:
            self.assertEqual(enum, enum_val[enum])

    def test_enums_type(self):
        """
        Should have the enum variable of type Enum
        """

        all_enumaration_types = [
            StatusCode.SUCCESS,
            StatusCode.BAD_FORMAT,
            StatusCode.UNKNOWN_COMMAND,
            StatusCode.BAD_PARAMS,
            StatusCode.INTERNAL_ERROR
        ]

        for enum in all_enumaration_types:
            self.assertEqual(type(enum), StatusCode)

if __name__ == '__main__':
    unittest.main()
