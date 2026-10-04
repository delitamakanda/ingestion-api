import unittest

import pytest


@pytest.mark.unit
class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
