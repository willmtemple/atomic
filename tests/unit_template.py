#
# Project Atomic Unit Test Example Template
#

import unittest


class TestAtomicUnit(unittest.TestCase):
    def test_unit_desired_behavior(self):
        self.assertTrue(True)


# Not necessary, but allows the test to be run outside of test
# discovery.
if __name__ == '__main__':
    unittest.main()
