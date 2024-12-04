"""This module provides unit tests for 'SimpleSolar'."""
import os

import pytest
from hercules.python_simulators.simple_solar import SimpleSolar
from numpy.testing import assert_almost_equal

def get_solar_params():

    full_path = os.path.realpath(__file__)
    path = os.path.dirname(full_path)

    # explicitly specifying weather inputs from the first timestep of the example file
    solar_dict = {
        "py_sim_type": SimpleSolar,
        "capacity": 50000,
        "efficiency": 0.5,

        "initial_conditions":{
            "power": 25000,
            "irradiance": 1000,
        },
    }
    
    dt = 0.5 # s - input file has a dt of 1 min

    return solar_dict, dt

def create_simple_solar():
    solar_dict, dt = get_solar_params()
    return SimpleSolar(solar_dict, dt)

@pytest.fixture
def SS():
    return create_simple_solar()

def test_init():
    # testing the `init` function: reading the inputs from input dictionary
    solar_dict, dt = get_solar_params()
    SS = SimpleSolar(solar_dict, dt)

    assert SS.dt == dt

    assert SS.power_kw == solar_dict["initial_conditions"]["power"]
    assert SS.irradiance == solar_dict["initial_conditions"]["irradiance"]

def test_return_outputs(SS: SimpleSolar):
    # testing the function `return_outputs`
    # outputs after initialization - all outputs should reflect input dict
    outputs_init = SS.return_outputs()

    assert outputs_init["power_kw"] == 25000
    assert outputs_init["dni"] == 1000

    # change PV power predictions and irradiance as if during simulation
    SS.power_kw = 20000
    SS.irradiance = 900

    # check that outputs return the changed PV outputs
    outputs_sim = SS.return_outputs()

    assert outputs_sim["power_kw"] == 20000
    # assert outputs_sim["dc_power_mw"] == 1000
    assert outputs_sim["dni"] == 900
    assert outputs_sim["aoi"] == None

def test_step(SS: SimpleSolar):
    # testing the `step` function: calculating power based on inputs at first timestep
    step_inputs = {"time": 0, "irradiance": 900}

    outputs_sim = SS.step(step_inputs)
    print(outputs_sim["power_kw"])
    print(outputs_sim["dni"])
    print(outputs_sim["aoi"])

    assert_almost_equal(SS.power_kw, 22500.0, decimal=8)

# TODO: decide if SimpleSolar should have control capabilities
# def test_control(SPS: SolarPySAM):
#     power_setpoint_mw = 30
#     step_inputs = {"time": 0, "py_sims": {"inputs": {"solar_setpoint_mw": power_setpoint_mw}}}
#     SPS.step(step_inputs)
#     assert_almost_equal(SPS.power_mw, power_setpoint_mw, decimal=8)
