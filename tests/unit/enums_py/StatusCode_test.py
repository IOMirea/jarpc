import unittest
from iomirea_rpc.enums import StatusCode

class enums_StatusCode_TestCase(unittest.TestCase):
    """
    Testing the StatusCode Class
    """
    all_enumaration_types = [
        StatusCode.SUCCESS,
        StatusCode.BAD_FORMAT,
        StatusCode.UNKNOWN_COMMAND,
        StatusCode.BAD_PARAMS,
        StatusCode.INTERNAL_ERROR
    ]

    def test_enums_variables_values(self):
        """
        Should ensure that variables are set to their expected values
        """
        
        enum_val = [0, 1, 2, 3, 4]
        for enum in self.all_enumaration_types:
            self.assertEqual(enum.value, enum_val[enum.value])

    def test_enums_type(self):
        """
        Should have the enum variable of type Enum
        """

        for enum in self.all_enumaration_types:
            self.assertEqual(type(enum), StatusCode)


if __name__ == '__main__':
    unittest.main()
