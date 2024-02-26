"""This module provides unit tests for 'SolarPySAM'."""
import pytest
import os
from hercules.python_simulators.solar_pysam import SolarPySAM
from numpy.testing import assert_almost_equal

def get_solar_params():

    full_path = os.path.realpath(__file__)
    path = os.path.dirname(full_path)

    solar_dict = {
        "py_sim_type": SolarPySAM,
        "weather_file_name": None,
        "weather_data_input": {
        "Timestamp": ['2018-05-10 12:31:00+00:00'],
        "SRRL BMS Direct Normal Irradiance (W/m²_irr)": [330.8601989746094],
        "SRRL BMS Diffuse Horizontal Irradiance (W/m²_irr)": [68.23037719726561],
        "SRRL BMS Global Horizontal Irradiance (W/m²_irr)": [68.23037719726561],
        "SRRL BMS Wind Speed at 19' (m/s)": [0.4400002620664621],
        "SRRL BMS Dry Bulb Temperature (°C)": [11.990000406901045],
        },

        "system_info_file_name": path+'/../../example_case_folders/07_amr_wind_standin_and_solar_pysam/100MW_1axis_pvsamv1.json',
        "initial_conditions": {
            "power": 25, 
            "irradiance": 1000
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
    solar_dict, dt = get_solar_params()
    SPS = SolarPySAM(solar_dict, dt)

    assert SPS.dt == dt

    assert SPS.power_mw == solar_dict["initial_conditions"]["power"]
    assert SPS.dc_power_mw == solar_dict["initial_conditions"]["power"]
    assert SPS.irradiance == solar_dict["initial_conditions"]["irradiance"]
    assert SPS.aoi == 0

def test_return_outputs(SPS: SolarPySAM):
    # outputs after initialization - all outputs should reflect input dict
    outputs_init = SPS.return_outputs()

    assert outputs_init["power"] == 25
    assert outputs_init["irradiance"] == 1000

    # change simple battery state as if during simulation
    SPS.power_mw = 800
    SPS.dc_power_mw = 1000
    SPS.irradiance = 900

    # check that outputs return the changed battery state
    outputs_sim = SPS.return_outputs()

    assert outputs_sim["power"] == 800
    assert outputs_sim["dc_power"] == 1000
    assert outputs_sim["irradiance"] == 900

def test_step(SPS: SolarPySAM):
    step_inputs = {
        "py_sims": {
            "inputs": {
                "sim_time_s": 0,
            },
        },
    }

    SPS.step(step_inputs)

    assert_almost_equal(SPS.power_mw, 32.17650018440107, decimal=8)
    assert_almost_equal(SPS.dc_power_mw, 33.26240852125279, decimal=8)
    assert_almost_equal(SPS.irradiance, 68.23037719726561, decimal=8)
