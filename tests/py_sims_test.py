import pytest

from hercules import py_sims


def test_init_pysim():

    # Test that a pysim can be initated

    input_dict = dict()
    input_dict['dt'] = 0.1
    input_dict['py_sims'] = None

    py_sims.PySims(input_dict)
