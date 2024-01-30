# Copyright 2022 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# This script implements a test client to test out the server against
# It is based on code from
# https://github.com/TUDelft-DataDrivenControl/SOWFA/blob/master/exampleCases/example.12.piso.NREL5MW.ADM.zmqSSC.python/ssc/testclient.py

# The basic operation for this script is to pretend to be the wind farm simulator by:
# - First connecting to the front-end server
# - Than in a loop:
# - - Send the measurement values of 4 turbines
# - - Receive the wind speed and wind direction measurements
# - - Update the turbine measurements
# - - Sleep for 1 s

import logging
import sys

import numpy as np
from floris.tools import FlorisInterface
from floris.turbine_library import build_cosine_loss_turbine_dict

from hercules.amr_wind_standin import AMRWindStandin, read_amr_wind_input

# Set up the logger
# Useful for when running on eagle
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    filename="log_test_client.log",
    filemode="w",
)
logger = logging.getLogger("amr_wind_standin")

# Perhaps a small hack to also send log to the terminal outout
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

#  Make an announcement
logger.info("Emulator amr_wind_standin (standing in for AMR-Wind) connecting to server")


# Define a function to read the amrwind input file
# Note simply copied from emulator
def construct_floris_from_amr_input(amr_wind_input):
    # Probably want a file not found error instead

    with open(amr_wind_input) as fp:
        Lines = fp.readlines()

        # Get the turbine locations
        layout_x = []
        layout_y = []
        for line in Lines:
            if ".base_position" in line:
                loc = [float(d) for d in line.split()[2:]]
                layout_x.append(loc[0])
                layout_y.append(loc[1])

        # Check that uniform disk is specified
        for line in Lines:
            if "Actuator.type" in line:
                acuator_type = line.split()[2]
                if acuator_type == "UniformCtDisk":
                    pass
                else:
                    raise NotImplementedError("FLORIS standin requires UniformCtDisk actuators.")

        # Get the turine parameters
        for line in Lines:
            if acuator_type + ".rotor_diameter" in line:
                rotor_diameter = float(line.split()[2])
        for line in Lines:
            if acuator_type + ".hub_height" in line:
                hub_height = float(line.split()[2])
        for line in Lines:
            if acuator_type + ".density" in line:
                ref_air_density = float(line.split()[2])

        # construct turbine thrust and power curves
        for line in Lines:
            if acuator_type + ".thrust_coeff" in line:
                thrust_coefficient = [float(d) for d in line.split()[2:]]
        for line in Lines:
            if acuator_type + ".wind_speed" in line:
                wind_speed = [float(d) for d in line.split()[2:]]
        # The power curve needs to be constructed from available data
        thrust_coefficient = np.array(thrust_coefficient)
        if (thrust_coefficient < 0).any() or (thrust_coefficient > 1).any():
            print("Clipping thrust_coefficient to (0, 1) interval.")
            thrust_coefficient = np.clip(thrust_coefficient, 0.0, 1.0)
        ai = (1 - np.sqrt(1 - np.array(thrust_coefficient))) / 2
        power_coefficient = 4 * ai * (1 - ai) ** 2
        turbine_data_dict = {
            "wind_speed": wind_speed,
            "thrust_coefficient": thrust_coefficient,
            "power_coefficient": list(power_coefficient),
        }

        # Build the turbine dictionary as expected by FLORIS
        turb_dict = build_cosine_loss_turbine_dict(
            turbine_data_dict=turbine_data_dict,
            turbine_name="FLORIS-standin-turbine",
            hub_height=hub_height,
            rotor_diameter=rotor_diameter,
            ref_air_density=ref_air_density,
        )

        # load a default model
        fi = FlorisInterface(default_floris_dict)
        fi.reinitialize(
            layout_x=layout_x, layout_y=layout_y, turbine_type=[turb_dict] * len(layout_x)
        )

    return fi


class FlorisStandin(AMRWindStandin):
    def __init__(self, config_dict, amr_input_file, amr_standin_data_file=None):
        super(FlorisStandin, self).__init__(
            config_dict=config_dict,
            amr_wind_input=amr_input_file,
            amr_standin_data_file=amr_standin_data_file,
        )

        # Construct the floris object
        self.fi = construct_floris_from_amr_input(amr_input_file)

        # Get the number of turbines
        self.num_turbines = len(self.fi.layout_x)

        # Print the number of turbines
        logger.info("Number of turbines: {}".format(self.num_turbines))

        # Initialize storage
        self.yaw_angles_stored = [0.0] * self.num_turbines

    def get_step(self, sim_time_s, yaw_angles=None):
        """Retreive or calculate wind speed, direction, and turbine powers

        Input:
        sim_time_s: simulation time step

        Output:
        amr_wind_speed: wind speed at current time step
        amr_wind_direction: wind direction at current time step
        turbine_powers: turbine powers at current time step
        """

        if hasattr(self, "standin_data"):
            amr_wind_speed = np.interp(
                sim_time_s,
                self.standin_data["time"],
                self.standin_data["amr_wind_speed"],
            )
            amr_wind_direction = np.interp(
                sim_time_s,
                self.standin_data["time"],
                self.standin_data["amr_wind_direction"],
            )

        else:
            amr_wind_speed = 8.0
            amr_wind_direction = 240.0

        turbine_wind_directions = [amr_wind_direction] * self.num_turbines

        # Compute the turbine power using FLORIS
        self.fi.reinitialize(wind_speeds=[amr_wind_speed], wind_directions=[amr_wind_direction])

        if yaw_angles is not None:
            yaw_misalignments = (amr_wind_direction - np.array(yaw_angles))[
                None, :
            ]  # TODO: remove 2

            if (np.abs(yaw_misalignments) > 45).any():  # Bad yaw angles
                print(
                    (
                        "Large yaw misalignment detected. "
                        + "Wind direction: {0:.2f} deg, ".format(amr_wind_direction)
                        + "Yaw angles: "
                    ),
                    yaw_angles,
                    "Using previous yaw angles.",
                )
                yaw_misalignments = (amr_wind_direction - np.array(self.yaw_angles_stored))[None, :]
            else:  # Reasonable yaw angles, save in case bad angles received later
                self.yaw_angles_stored = yaw_angles
        else:
            yaw_misalignments = yaw_angles
        self.fi.calculate_wake(yaw_angles=yaw_misalignments)
        # This converts the output power from Floris, which is in watts, to kW to interact with the rest of Hercules
        turbine_powers = (self.fi.get_turbine_powers() / 1000).flatten().tolist()  # in kW

        return (
            amr_wind_speed,
            amr_wind_direction,
            turbine_powers,
            turbine_wind_directions,
        )

    def process_endpoint_event(self, msg):
        pass

    def process_periodic_endpoint(self):
        pass

    def process_periodic_publication(self):
        # Periodically publish data to the surrpogate
        pass

    def process_subscription_messages(self, msg):
        pass


def launch_floris(amr_input_file, amr_standin_data_file=None):
    temp = read_amr_wind_input(amr_input_file)

    config = {
        "name": "floris_standin",
        "gridpack": {},
        "helics": {
            "deltat": temp["dt"],
            "subscription_topics": ["control"],
            "publication_topics": ["status"],
            "endpoints": [],
            "helicsport": temp["helics_port"],
        },
        "publication_interval": 1,
        "endpoint_interval": 1,
        "starttime": 0,
        "stoptime": temp["stop_time"],
        "Agent": "floris_standin",
    }

    obj = FlorisStandin(config, amr_input_file, amr_standin_data_file)

    obj.run_helics_setup()
    obj.enter_execution(function_targets=[], function_arguments=[[]])


default_floris_dict = {
    "logging": {
        "console": {"enable": True, "level": "WARNING"},
        "file": {"enable": False, "level": "WARNING"},
    },
    "solver": {"type": "turbine_grid", "turbine_grid_points": 3},
    "wake": {
        "model_strings": {
            "combination_model": "sosfs",
            "deflection_model": "gauss",
            "turbulence_model": "crespo_hernandez",
            "velocity_model": "gauss",
        },
        "enable_secondary_steering": True,
        "enable_yaw_added_recovery": True,
        "enable_transverse_velocities": True,
        "wake_deflection_parameters": {
            "gauss": {
                "ad": 0.0,
                "alpha": 0.58,
                "bd": 0.0,
                "beta": 0.077,
                "dm": 1.0,
                "ka": 0.38,
                "kb": 0.004,
            },
            "jimenez": {"ad": 0.0, "bd": 0.0, "kd": 0.05},
        },
        "wake_turbulence_parameters": {
            "crespo_hernandez": {"initial": 0.1, "constant": 0.5, "ai": 0.8, "downstream": -0.32}
        },
        "wake_velocity_parameters": {
            "gauss": {"alpha": 0.58, "beta": 0.077, "ka": 0.38, "kb": 0.004},
            "jensen": {"we": 0.05},
        },
    },
    "farm": {
        "layout_x": [0.0],
        "layout_y": [0.0],
        "turbine_type": ["nrel_5MW"],
    },
    "flow_field": {
        "wind_speeds": [8.0],
        "wind_directions": [270.0],
        "wind_veer": 0.0,
        "wind_shear": 0.12,
        "air_density": 1.225,
        "turbulence_intensity": 0.06,
        "reference_wind_height": 90.0,
    },
    "name": "GCH_for_FlorisStandin",
    "description": "FLORIS Gauss Curl Hybrid model standing in for AMR-Wind",
    "floris_version": "v4.x",
}
