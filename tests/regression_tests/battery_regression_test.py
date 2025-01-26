"""Regression tests for 'SolarPySAM'."""

import numpy as np
from hercules.python_simulators.battery import LIB, SimpleBattery

PRINT_VALUES = True

test_input_dict = {
    "size": 20,
    "energy_capacity": 80,
    "charge_rate": 20,
    "discharge_rate": 20,
    "max_SOC": 0.9,
    "min_SOC": 0.1,
    "initial_conditions": {"SOC": 0.5},
}

np.random.seed(0)
powers_requested = np.concatenate(
    (
        np.linspace(0, 100000, 3), # Ramp up
        np.linspace(100000, -5000, 6), # Ramp down
        np.random.normal(-500, 100, 3) # Random fluctuations
    )
)

powers_base_simple = np.array(
    [
        0.,
        20000.,
        20000.,
        20000.,
        20000.,
        20000.,
        20000.,
        16000.,
        -5000.,
        -323.5947654,
        -459.98427916,
    ]
)

reject_base_simple = np.array(
    [
        0.    ,
        30000.,
        80000.,
        80000.,
        59000.,
        38000.,
        17000.,
        0.    ,
        0.    ,
        0.    ,
        0.
    ]
)

soc_base_simple = np.array(
    [
        0.5       ,
        0.50003472,
        0.50006944,
        0.50010417,
        0.50013889,
        0.50017361,
        0.50020833,
        0.50023611,
        0.50022743,
        0.50022687,
        0.50022607,
    ]
)

powers_base_lib = np.array(
    [
        0.            ,
        20047.11229812,
        20047.95046608,
        20048.77886147,
        20049.59760268,
        20050.40680666,
        20051.20658894,
        15990.37116823,
        -4983.52093018,
        -323.83088639 ,
        -459.97259284 ,
    ]
)

reject_base_lib = np.array(
    [
        0.00000000e+00,
        2.99528877e+04,
        7.99520495e+04,
        7.99512211e+04,
        5.89504024e+04,
        3.79495932e+04,
        1.69487934e+04,
        9.62883177e+00,
        -1.64790698e+01,
        2.36120986e-01,
        -1.16863220e-02,
    ]
)

soc_base_lib = np.array(
    [
        0.5       ,
        0.50003472,
        0.50006944,
        0.50010417,
        0.50013889,
        0.50017361,
        0.50020833,
        0.50023604,
        0.50022738,
        0.50022681,
        0.50022601,
    ]
)

def test_SimpleBattery_regression_():

    dt = 0.5

    battery = SimpleBattery(test_input_dict, dt)

    times_test = np.arange(0, 5.5, dt)
    powers_test = np.zeros_like(times_test)
    reject_test = np.zeros_like(times_test)
    soc_test = np.zeros_like(times_test)

    for i, t in enumerate(times_test):
        out = battery.step({
            "time": t,
            "py_sims": {
                "inputs": {
                    "battery_signal": powers_requested[i],
                    "available_power": powers_requested[i]
                }
            }
        })
        powers_test[i] = out["power"]
        reject_test[i] = out["reject"]
        soc_test[i] = out["soc"]

    if PRINT_VALUES:
        print("Powers: ", powers_test)
        print("Rejected: ", reject_test)
        print("SOC: ", soc_test)

    assert np.allclose(powers_base_simple, powers_test)
    assert np.allclose(reject_base_simple, reject_test)
    assert np.allclose(soc_base_simple, soc_test)

def test_LIB_regression_():


    dt = 0.5

    battery = LIB(test_input_dict, dt)

    times_test = np.arange(0, 5.5, dt)
    powers_test = np.zeros_like(times_test)
    reject_test = np.zeros_like(times_test)
    soc_test = np.zeros_like(times_test)

    for i, t in enumerate(times_test):
        out = battery.step({
            "time": t,
            "py_sims": {
                "inputs": {
                    "battery_signal": powers_requested[i],
                    "available_power": powers_requested[i]
                }
            }
        })
        powers_test[i] = out["power"]
        reject_test[i] = out["reject"]
        soc_test[i] = out["soc"]

    if PRINT_VALUES:
        print("Powers: ", powers_test)
        print("Rejected: ", reject_test)
        print("SOC: ", soc_test)

    assert np.allclose(powers_base_lib, powers_test)
    assert np.allclose(reject_base_lib, reject_test)
    assert np.allclose(soc_base_lib, soc_test)
