"""This module provides unit tests for 'SolarPySAM'."""
import os

import pytest
from hercules.python_simulators.solar_pysam import SolarPySAM
from numpy.testing import assert_almost_equal


def get_solar_params():

    full_path = os.path.realpath(__file__)
    path = os.path.dirname(full_path)

    # explicitly specifying weather inputs from the first timestep of the example file
    solar_dict = {
        "py_sim_type": SolarPySAM,
        "pysam_model": "pvsam",
        "weather_file_name": None,
        "weather_data_input": {
        "Timestamp": ['2018-05-10 12:31:00+00:00'],
        "SRRL BMS Direct Normal Irradiance (W/m²_irr)": [330.8601989746094],
        "SRRL BMS Diffuse Horizontal Irradiance (W/m²_irr)": [68.23037719726561], # [32.576671600341804],
        "SRRL BMS Global Horizontal Irradiance (W/m²_irr)": [68.23037719726561],
        "SRRL BMS Wind Speed at 19' (m/s)": [0.4400002620664621], # [0.9500006239596464],
        "SRRL BMS Dry Bulb Temperature (°C)": [11.990000406901045],
        },

        "system_info_file_name": path+
            '/../test_inputs/100MW_1axis_pvsamv1.json',
        "lat": 39.7442, 
        "lon": -105.1778, 
        "elev": 1829,
        "target_system_capacity_kW": 100002.58266599999,
        "target_dc_ac_ratio": 1.33,
        "initial_conditions": {
            "power": 25, 
            "dni": 1000
        },
    }
    
    dt = 0.5 # s - input file has a dt of 1 min

    return solar_dict, dt

def create_solar_pysam():
    solar_dict, dt = get_solar_params()
    return SolarPySAM(solar_dict, dt)

@pytest.fixture
def SPS():
    return create_solar_pysam()

def test_init():
    # testing the `init` function: reading the inputs from input dictionary
    solar_dict, dt = get_solar_params()
    SPS = SolarPySAM(solar_dict, dt)

    assert SPS.dt == dt

    assert SPS.power_mw == solar_dict["initial_conditions"]["power"]
    assert SPS.dc_power_mw == solar_dict["initial_conditions"]["power"]
    assert SPS.dni == solar_dict["initial_conditions"]["dni"]
    assert SPS.aoi == 0

def test_return_outputs(SPS: SolarPySAM):
    # testing the function `return_outputs`
    # outputs after initialization - all outputs should reflect input dict
    outputs_init = SPS.return_outputs()

    assert outputs_init["power_mw"] == 25
    assert outputs_init["dni"] == 1000

    # change PV power predictions and irradiance as if during simulation
    SPS.power_mw = 800
    # SPS.dc_power_mw = 1000
    SPS.dni = 900
    SPS.aoi = 0

    # check that outputs return the changed PV outputs
    outputs_sim = SPS.return_outputs()

    assert outputs_sim["power_mw"] == 800
    # assert outputs_sim["dc_power_mw"] == 1000
    assert outputs_sim["dni"] == 900
    assert outputs_sim["aoi"] == 0

def test_step(SPS: SolarPySAM):
    # testing the `step` function: calculating power based on inputs at first timestep
    step_inputs = {"time": 0}

    SPS.step(step_inputs)

    assert_almost_equal(SPS.power_mw, 32.19801938915135, decimal=8)
    # assert_almost_equal(SPS.power_mw, 28.56578613515644, decimal=8)
    assert_almost_equal(SPS.ghi, 68.23037719726561, decimal=8)

def test_control(SPS: SolarPySAM):
    power_setpoint_mw = 30
    step_inputs = {"time": 0, "py_sims": {"inputs": {"solar_setpoint_mw": power_setpoint_mw}}}
    SPS.step(step_inputs)
    assert_almost_equal(SPS.power_mw, power_setpoint_mw, decimal=8)
