"""Regression tests for 'SolarPySAM'."""
import os
import numpy as np

import pytest
from hercules.python_simulators.solar_pysam import SolarPySAM

PRINT_VALUES = True

powers_base_no_control = np.array(
    [
        28.37088745,
        28.39443266,
        28.41798115,
        28.4415289 ,
        28.46507592,
        28.48862221,
        28.51216376,
        28.53570861,
        28.55925274,
        28.58279613,
    ]
)

powers_base_control = np.array(
    [
        28.37088745,
        28.39443266,
        28.4       ,
        28.4       ,
        28.4       ,
        28.4       ,
        28.4       ,
        28.4       ,
        28.4       ,
        28.4       ,
    ]
)

dni_base_no_control = np.array(
    [
        330.86019897,
        331.19604492,
        331.53189087,
        331.86773682,
        332.20358276,
        332.53942871,
        332.87527466,
        333.21112061,
        333.54696655,
        333.8828125 ,
    ]
)

aoi_base_no_control = np.array(
    [   
        41.47901733,
        41.4790173 ,
        41.47901726,
        41.47901722,
        41.47901719,
        41.47901715,
        41.47901711,
        41.47901708,
        41.47901704,
        41.479017  ,
    ]
)

def get_solar_params():

    full_path = os.path.realpath(__file__)
    path = os.path.dirname(full_path)

    # explicitly specifying weather inputs from the first timestep of the example file
    solar_dict = {
        "py_sim_type": SolarPySAM,
        "weather_file_name": path+'/../test_inputs/solar_pysam_data.csv',
        "system_info_file_name": path+'/../test_inputs/100MW_1axis_pvsamv1.json',
        "lat": 39.7442, 
        "lon": -105.1778, 
        "elev": 1829,
        "initial_conditions": {
            "power": 25, 
            "dni": 1000
        },
        "verbose": False
    }
    
    dt = 0.5 # s - input file has a dt of 1 min

    return solar_dict, dt

def create_solar_pysam():
    solar_dict, dt = get_solar_params()
    return SolarPySAM(solar_dict, dt)

@pytest.fixture
def SPS():
    return create_solar_pysam()

def test_SolarPySAM_regression_no_control(SPS: SolarPySAM):

    times_test = np.arange(0, 5, SPS.dt)
    powers_test = np.zeros_like(times_test)
    dni_test = np.zeros_like(times_test)
    aoi_test = np.zeros_like(times_test)

    for i, t in enumerate(times_test):
        out = SPS.step({"time": t})
        powers_test[i] = out["power_mw"]
        dni_test[i] = out["dni"]
        aoi_test[i] = out["aoi"]

    if PRINT_VALUES:
        print("Powers: ", powers_test)
        print("DNI: ", dni_test)
        print("AOI: ", aoi_test)

    assert np.allclose(powers_base_no_control, powers_test)
    assert np.allclose(dni_base_no_control, dni_test)
    assert np.allclose(aoi_base_no_control, aoi_test)

def test_SolarPySAM_regression_control(SPS: SolarPySAM):
    power_setpoint_mw = 28.40 # Slightly below most of the base outputs.

    times_test = np.arange(0, 5, SPS.dt)
    powers_test = np.zeros_like(times_test)
    dni_test = np.zeros_like(times_test)
    aoi_test = np.zeros_like(times_test)

    for i, t in enumerate(times_test):
        out = SPS.step({"time": t, "py_sims": {"inputs": {"solar_setpoint_mw": power_setpoint_mw}}})
        powers_test[i] = out["power_mw"]
        dni_test[i] = out["dni"]
        aoi_test[i] = out["aoi"]

    if PRINT_VALUES:
        print("Powers: ", powers_test)
        print("DNI: ", dni_test)
        print("AOI: ", aoi_test)

    assert np.allclose(powers_base_control, powers_test)
    assert np.allclose(dni_base_no_control, dni_test)
    assert np.allclose(aoi_base_no_control, aoi_test)