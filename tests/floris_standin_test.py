from pathlib import Path
import numpy as np

from SEAS.federate_agent import FederateAgent
from floris.tools import FlorisInterface

from hercules.floris_standin import (
    FlorisStandin,
    construct_floris_from_amr_input,
    default_floris_dict,
)
from hercules.amr_wind_standin import AMRWindStandin

AMR_INPUT = Path(__file__).resolve().parent / "test_inputs" / "amr_input_florisstandin.inp"

CONFIG = {
    "name": "floris_standin",
    "gridpack": {},
    "helics": {
        "deltat": 1.0,
        "subscription_topics": ["control"],
        "publication_topics": ["status"],
        "endpoints": [],
        "helicsport": None,
    },
    "publication_interval": 1,
    "endpoint_interval": 1,
    "starttime": 0,
    "stoptime": 10.0,
    "Agent": "floris_standin",
}


def test_construct_floris_from_amr_input():
    fi_test = construct_floris_from_amr_input(AMR_INPUT)
    assert isinstance(fi_test, FlorisInterface)


def test_FlorisStandin_instantiation():
    # Check instantiates correctly
    floris_standin = FlorisStandin(CONFIG, AMR_INPUT)

    # Check inheritance
    assert isinstance(floris_standin, FederateAgent)
    assert isinstance(floris_standin, AMRWindStandin)

    # Get FLORIS equivalent, match layout and turbines
    fi_true = FlorisInterface(default_floris_dict)
    fi_true.reinitialize(
        layout_x=floris_standin.fi.layout_x,
        layout_y=floris_standin.fi.layout_y,
        turbine_type=floris_standin.fi.floris.farm.turbine_definitions,
    )

    assert fi_true.floris.as_dict() == floris_standin.fi.floris.as_dict()


def test_FlorisStandin_get_step():
    floris_standin = FlorisStandin(CONFIG, AMR_INPUT)

    # Get FLORIS equivalent, match layout and turbines
    fi_true = FlorisInterface(default_floris_dict)
    fi_true.reinitialize(
        layout_x=floris_standin.fi.layout_x,
        layout_y=floris_standin.fi.layout_y,
        turbine_type=floris_standin.fi.floris.farm.turbine_definitions,
    )

    default_wind_direction = 240.0  # Matches default in FlorisStandin
    default_wind_speed = 8.0  # Matches default in FlorisStandin

    # Test with None yaw angles
    fs_ws, fs_wd, fs_tp, fs_twd = floris_standin.get_step(5.0)
    fi_true.reinitialize(wind_speeds=[default_wind_speed], wind_directions=[default_wind_direction])
    fi_true.calculate_wake()
    fi_true_tp = fi_true.get_turbine_powers()

    assert fs_ws == default_wind_speed
    assert fs_wd == default_wind_direction
    assert fs_twd == [default_wind_direction] * 2
    assert np.allclose(fs_tp, fi_true_tp.flatten().tolist())

    # Test with aligned turbines
    yaw_angles = [240.0, 240.0]
    fs_ws, fs_wd, fs_tp, fs_twd = floris_standin.get_step(5.0, yaw_angles)
    fi_true.reinitialize(wind_speeds=[default_wind_speed], wind_directions=[default_wind_direction])
    fi_true.calculate_wake()  # Aligned in any case
    fi_true_tp = fi_true.get_turbine_powers()

    assert np.allclose(fs_tp, fi_true_tp.flatten().tolist())

    # Test with misaligned turbines
    yaw_angles = [260.0, 230.0]
    fs_ws, fs_wd, fs_tp, fs_twd = floris_standin.get_step(5.0, yaw_angles)
    fi_true.reinitialize(wind_speeds=[default_wind_speed], wind_directions=[default_wind_direction])
    fi_true.calculate_wake()  # Don't expect to work
    fi_true_tp = fi_true.get_turbine_powers()
    assert not np.allclose(fs_tp, fi_true_tp.flatten().tolist())

    # Correct yaw angles
    fi_true.calculate_wake(yaw_angles=default_wind_direction - np.array([yaw_angles]))
    fi_true_tp = fi_true.get_turbine_powers()
    assert np.allclose(fs_tp, fi_true_tp.flatten().tolist())


def test_FlorisStandin_with_standin_data():
    # TODO: write this test once standin_data capability built out
    pass
