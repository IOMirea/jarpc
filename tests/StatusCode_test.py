import unittest
from unittest import mock

import sys
sys.path.append("..")
from iomirea_rpc.enums import StatusCode

"""
Testing the StatusCode Class
"""

class Test_StatusCode_TestCase(unittest.TestCase):
    """
    Unit Testing if the variables declared are set to their expected values
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


if __name__ == '__main__':
    unittest.main()
