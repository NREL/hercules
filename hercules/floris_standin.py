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

import ast
import logging
import sys

import numpy as np
import pandas as pd
from SEAS.federate_agent import FederateAgent
from floris.tools import FlorisInterface
from floris.simulation.turbine import build_cosine_loss_turbine_dict

from hercules.amr_wind_standin import read_amr_wind_input, AMRWindStandin

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
    return_dict = {}

    with open(amr_wind_input) as fp:
        Lines = fp.readlines()

        # Get the turbine locations
        layout_x = []
        layout_y = []
        for line in Lines:
            if ".base_position" in line:
                loc = [float(l) for l in line.split()[2:]]
                layout_x.append(loc[0])
                layout_y.append(loc[1])

        # Check that uniform disk is specified
        for line in Lines:
            if "Actuator.type" in line:
                acuator_type = line.split()[2]
                if acuator_type == "UniformCtDisk":
                    pass
                else:
                    raise NotImplementedError(
                        "FLORIS standin requires UniformCtDisk actuators."
                    )

        # Get the turine parameters
        for line in Lines:
            if acuator_type+".rotor_diameter" in line:
                rotor_diameter = float(line.split()[2])
        for line in Lines:
            if acuator_type+".hub_height" in line:
                hub_height = float(line.split()[2])
        for line in Lines:
            if acuator_type+".density" in line:
                ref_air_density = float(line.split()[2])

        # construct turbine thrust and power curves
        for line in Lines:
            if acuator_type+".thrust_coeff" in line:
                thrust_coefficient = [float(l) for l in line.split()[2:]]
        for line in Lines:
            if acuator_type+".wind_speed" in line:
                wind_speed = [float(l) for l in line.split()[2:]]
        # The power curve needs to be constructed from available data
        ai = (1 - np.sqrt(1-np.array(thrust_coefficient)))/2
        power_coefficient = 4*ai*(1-ai)**2
        turbine_data_dict={
            "wind_speed":wind_speed,
            "thrust_coefficient":thrust_coefficient,
            "power_coefficient":list(power_coefficient)
        }

        # Build the turbine dictionary as expected by FLORIS
        turb_dict = build_cosine_loss_turbine_dict(
            turbine_data_dict=turbine_data_dict,
            turbine_name="FLORIS-standin-turbine",
            hub_height=hub_height,
            rotor_diameter=rotor_diameter,
            ref_air_density=ref_air_density
        )

        # load a default model
        fi = FlorisInterface("gch.yaml")
        fi.reinitialize(
            layout_x=layout_x,
            layout_y=layout_y,
            turbine_type=[turb_dict]*len(layout_x)
        )

    return fi


class FlorisStandin(AMRWindStandin):
    def __init__(self, config_dict, amr_input_file, amr_standin_data_file=None):
        super(FlorisStandin, self).__init__(
            config_dict=config_dict,
            amr_wind_input=amr_input_file,
            amr_standin_data_file=amr_standin_data_file
        )

        # Construct the floris object
        self.fi = construct_floris_from_amr_input(amr_input_file)

        # Get the number of turbines
        self.num_turbines = len(self.fi.layout_x)

        # Print the number of turbines
        logger.info("Number of turbines: {}".format(self.num_turbines))

        if amr_standin_data_file is not None:
            raise NotImplementedError("external data not yet supported.")
            self.standin_data = pd.read_csv(amr_standin_data_file)

    def run(self):
        # Initialize the values
        turbine_powers = np.zeros(self.num_turbines)
        sim_time_s = 0.0  # initialize time to 0
        amr_wind_speed = 8.0
        amr_wind_direction = 240.0

        # Before starting the main time loop need to do an initial connection to the
        # Control center to get the starting wind speed and wind direction
        # Code the time step as -1 and -1 (to ensure it is an array)
        logger.info("** First communication with control center")
        message_from_client_array = [0, -1, -1]
        # Send initial message via helics
        # publish on topic: status
        self.send_via_helics("status", str(message_from_client_array))
        logger.info("** Initial Message Sent: {}".format(message_from_client_array))

        # Subscribe to helics messages:
        incoming_messages = self.helics_connector.get_all_waiting_messages()
        if incoming_messages != {}:
            try:
                message_from_server = list(ast.literal_eval(incoming_messages))
            except Exception:
                message_from_server = None
        else:
            message_from_server = None

        # Synchronize time bewteen control center and AMRWind
        self.sync_time_helics(self.absolute_helics_time + self.deltat)
        logger.info("** Initial Received reply: {}".format(message_from_server))

        logger.info("** Intial Wind Speed: {}".format(amr_wind_speed))
        logger.info("** Intial Wind Direction: {}".format(amr_wind_direction))
        logger.info("...STARTING TIME LOOP...")

        self.message_from_server = None

        # while self.absolute_helics_time < (self.endtime - self.starttime + 1):
        while sim_time_s <= (self.endtime - self.starttime):
            # SIMULATE A CALCULATION STEP IN AMR WIND=========================
            logger.info("Calculating simulation time: %.1f" % sim_time_s)

            # Compute the turbine power using a simple formula
            (
                amr_wind_speed,
                amr_wind_direction,
                turbine_powers,
                turbine_wind_directions,
            ) = self.get_step(sim_time_s)

            # ================================================================
            # Communicate with control center
            # Send the turbine powers for this time step and get wind speed and wind direction for
            # the next time step
            logger.info("Time step: %d" % sim_time_s)
            logger.info("** Communicating with control center")
            message_from_client_array = (
                [
                    sim_time_s,
                    amr_wind_speed,
                    amr_wind_direction,
                ]
                + turbine_powers
                + turbine_wind_directions
            )

            # Send helics message to Control Center
            # publish on topic: status
            self.send_via_helics("status", str(message_from_client_array))
            logger.info("** Message Sent: {}".format(message_from_client_array))

            # Subscribe to helics messages from control center:
            incoming_messages = self.helics_connector.get_all_waiting_messages()
            if incoming_messages != {}:
                self.message_from_server = list(
                    ast.literal_eval(incoming_messages["control"]["message"])
                )
            else:
                self.message_from_server = None
            #  Now get the wind speed and wind direction back
            if self.message_from_server is not None:
                logger.info("** Received reply {}: {}".format(sim_time_s, self.message_from_server))

                # Note standin doesn't currently use received info for anything

            # Advance simulation time and time step counter
            sim_time_s += self.dt
            self.sync_time_helics(self.absolute_helics_time + self.deltat)

    # TODO cleanup code to move publish and subscribe here.

    def get_step(self, sim_time_s):
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
            turbine_powers = [
                np.interp(
                    sim_time_s,
                    self.standin_data["time"],
                    self.standin_data[f"turbine_power_{turb}"],
                )
                for turb in range(self.num_turbines)
            ]

            turbine_wind_directions = [0] * self.num_turbines

        else:
            amr_wind_speed = 8.0
            amr_wind_direction = 240.0

            # Compute the turbine power using a simple formula
            turbine_powers = (
                np.ones(self.num_turbines) * amr_wind_speed**3
                + np.random.rand(self.num_turbines) * 50
            )

            # Scale down later turbines as if waked
            turbine_powers[int(self.num_turbines / 2) :] = (
                0.75 * turbine_powers[int(self.num_turbines / 2) :]
            )

            # Convert to a list
            turbine_powers = turbine_powers.tolist()

            turbine_wind_directions = list(
                amr_wind_direction + 5.0 * np.random.randn(self.num_turbines)
            )
            turbine_wind_directions = [sim_time_s + 0.01, sim_time_s + 0.02]

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

    if amr_standin_data_file is not None:
        #obj = AMRWindStandin(config, amr_input_file, amr_standin_data_file)
        raise NotImplementedError("FLORIS standin is not yet configured for standin data.")
    else:
        obj = FlorisStandin(config, amr_input_file)

    obj.run_helics_setup()
    obj.enter_execution(function_targets=[], function_arguments=[[]])
