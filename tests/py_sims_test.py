import unittest

from hercules import py_sims

class TestPySims(unittest.TestCase):

    def test_init_pysim(self):

        input_dict = dict()
        input_dict['dt'] = 0.1
        input_dict['py_sims'] = None

        py_sims.PySims(input_dict)
