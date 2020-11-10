import unittest
from pthat.pthat import AUX


class TestAux(unittest.TestCase):

    def setUp(self):
        self.aux = AUX(1, test_mode=True)
        self.aux.command_type = "I"
        self.aux.command_id = 00
        self.aux.wait_delay = 0
        self.aux.debug = True

    def test_output_on(self):
        self.assertEqual("I00A11*", self.aux.output_on())

    def test_output_off(self):
        self.assertEqual("I00A10*", self.aux.output_off())


if __name__ == '__main__':
    unittest.main()
