"""This module provides unit tests for 'SimpleBattery'."""
import pytest
from hercules.python_simulators.simple_battery import SimpleBattery
from numpy.testing import assert_almost_equal


def get_battery_params():
    battery_dict = {
        "py_sim_type": SimpleBattery,
        "size": 20,  # MW size of the battery
        "energy_capacity": 80,  # total capcity of the battery in MWh (4-hour 20 MW battery)
        "charge_rate": 2,  # charge rate of the battery in MW
        "discharge_rate": 2,  # discharge rate of the battery in MW
        "max_SOC": 0.9,  # upper boundary on battery SOC
        "min_SOC": 0.1,  # lower boundary on battery SOC
        "initial_conditions": {"SOC": 0.102},
    }
    dt = 1
    return battery_dict, dt


def create_simple_battery():
    battery_dict, dt = get_battery_params()
    return SimpleBattery(battery_dict, dt)


@pytest.fixture
def SB():
    return create_simple_battery()


def test_init():
    battery_dict, dt = get_battery_params()
    SB = SimpleBattery(battery_dict, dt)

    assert SB.dt == dt

    assert SB.SOC == battery_dict["initial_conditions"]["SOC"]
    assert SB.SOC_min == battery_dict["min_SOC"]
    assert SB.SOC_max == battery_dict["max_SOC"]

    assert SB.P_min == -2000
    assert SB.P_max == 2000
    assert SB.P_max > SB.P_min

    assert SB.energy_capacity == battery_dict["energy_capacity"] * 1e3

    assert SB.power_mw == 0
    assert SB.P_reject == 0
    assert SB.P_charge == 0


def test_return_outputs(SB: SimpleBattery):
    # outputs after initialization - all outputs should reflect input dict
    outputs_init = SB.return_outputs()

    assert outputs_init["power"] == 0
    assert outputs_init["reject"] == 0
    assert outputs_init["soc"] == 0.102

    # change simple battery state as if during simulation
    SB.power_mw = 35
    SB.P_reject = 2
    SB.SOC = 0.25

    # check that outputs return the changed battery state
    outputs_sim = SB.return_outputs()

    assert outputs_sim["power"] == 35
    assert outputs_sim["reject"] == 2
    assert outputs_sim["soc"] == 0.25


def prep_control(SB: SimpleBattery):
    SB.P_charge = 1000
    SB.E = 0.5 * 80e3 * 3600  # SOC=0.5, units of kJ
    return SB


def step_inputs(P_avail, P_signal):
    return dict(
        {
            "setpoints": {"battery": {"signal": P_signal}},
            "py_sims": {"inputs": {"available_power": P_avail}},
        }
    )
def test_control_power_constraint(SB: SimpleBattery):

    # step_inputs = dict(
    #     {
    #         "setpoints": {"battery": {"signal": 2e3}},
    #         "py_sims": {"inputs": {"available_power": 0.5e3}},
    #     }
    # )

    # test upper charging limit
    # SB.control(i_avail=3e3, i_signal=2.5e3)
    SB.x = 0
    # out = SB.step(step_inputs(P_avail=3e3, P_signal=2.5e3))
    out = SB.step(step_inputs(P_avail=2e3, P_signal=1.5e3))
    assert out["power"] == 2e3
    assert out["reject"] == 0.5e3

    # Test lower charging limit
    SB.x = 0
    (power, reject, soc) = SB.step(step_inputs(P_avail=3e3, P_signal=-2.5e3))
    assert power == -2e3
    assert reject == -0.5e3

    SB.x = 0
    (power, reject, soc) = SB.step(step_inputs(P_avail=0.25e3, P_signal=1e3))
    assert power == 0.25e3
    assert reject == 0.75e3


def test_control_energy_constraint(SB: SimpleBattery):
    SB.E = SB.E_min + 500
    SB.control(P_avail=3e3, P_signal=-1.5e3)
    assert SB.P_charge == -500
    assert SB.P_reject == -1000

    SB.E = SB.E_max - 500
    SB.control(P_avail=3e3, P_signal=1.5e3)
    assert SB.P_charge == 500
    assert SB.P_reject == 1000


def test_step(SB: SimpleBattery):
    step_inputs = {
        "setpoints": {"battery": {"signal": 1e3}},
        "py_sims": {"inputs": {"available_power": 1e3}},
    }

    SB.step(step_inputs)

    assert_almost_equal(SB.E, 29377000, decimal=0)
    assert_almost_equal(SB.current_batt_state, 8160.27, decimal=1)
    assert_almost_equal(SB.SOC, 0.102003472, decimal=8)
    assert SB.P_charge == 1e3

    SB.E = SB.E_min + 5e3
    step_inputs["setpoints"]["battery"].update({"signal": -2e3})

    for i in range(4):
        SB.step(step_inputs)

    assert SB.E == 28800000
    assert SB.current_batt_state == 8000
    assert SB.SOC == 0.1
    assert SB.P_charge == 0
