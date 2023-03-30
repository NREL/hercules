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
import datetime
import logging
import os
import random
import sys
import time
from io import StringIO

import numpy as np
import pandas as pd
import zmq
from SEAS.federate_agent import FederateAgent

# PARAMETERS
num_turbines = 2

# Initialize to all zeros
turbine_powers = np.zeros(num_turbines)

# Set up the logger
# Useful for when running on eagle
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    filename='log_test_client.log',
                    filemode='w')
logger = logging.getLogger("dummy_amr_wind")

# Perhaps a small hack to also send log to the terminal outout
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

#  Make an announcement
logger.info(
    "Emulator dummy_amr_wind (standing in for AMR-Wind) connecting to server")


class DummyAMRWind(FederateAgent):
    def __init__(self, config_dict):
        super(DummyAMRWind, self).__init__(
            name=config_dict['name'], feeder_num=0, starttime=config_dict['starttime'], endtime=config_dict['stoptime'], agent_num=0, config_dict=config_dict)
        self.config_dict = config_dict

    def run(self):

        # Before starting the main time loop need to do an initial connection to the
        # Control center to get the starting wind speed and wind direction
        # Code the time step as -1 and -1 (to ensure it is an array)
        logger.info("** First communication with control center")
        message_from_client_array = [0, -1, -1]
        # Send initial message via helics
        # publish on topic: status
        self.send_via_helics("status", str(message_from_client_array))
        logger.info(
            "** Initial Message Sent: {}".format(message_from_client_array))

        # Subscribe to helics messages:
        incoming_messages = self.helics_connector.get_all_waiting_messages()
        if incoming_messages != {}:
            try:
                message_from_server = list(ast.literal_eval(incoming_messages))
            except Exception as e: 
                message_from_server = None
        else:
            message_from_server = None

        # Synchronize time bewteen control center and AMRWind
        self.sync_time_helics(self.absolute_helics_time + self.deltat)
        logger.info("** Initial Received reply: {}".format(message_from_server))

        # # Unpack the reply and update wind speed and wind direction
        # Initialize variables
        # This case only happens in the first time-step.
        if message_from_server == None:
            received_data = [7, 270]
        received_data = [7, 270]
        wind_speed = 8  # float(received_data[0]) #TODO: HARDCODED
        wind_direction = 270  # float(received_data[1]) #TODO: HARDCODED
        logger.info("** Intial Wind Speed: {}".format(wind_speed))
        logger.info("** Intial Wind Direction: {}".format(wind_direction))
        logger.info("...STARTING TIME LOOP...")

        sim_time_s = 0.  # initialize time to 0
        self.message_from_server = None
        # while True:
        while self.absolute_helics_time < (self.endtime - self.starttime + 1):

            # SIMULATE A CALCULATION STEP IN AMR WIND=========================
            logger.info("Calculating simulation time: %.1f" % sim_time_s)

            # Compute the turbine power using a simple formula
            turbine_powers = np.ones(
                num_turbines) * wind_speed**3 + np.random.rand(num_turbines) * 50

            # Scale down later turbines as if waked
            turbine_powers[int(num_turbines/2):] = 0.75 * \
                turbine_powers[int(num_turbines/2):]

            # Convert to a list
            turbine_powers = turbine_powers.tolist()

            # Set dummy wind directions to be passed out
            turbine_wind_directions = list(
                wind_direction + 5.*np.random.randn(num_turbines)
            )

            # ================================================================
            # Communicate with control center
            # Send the turbine powers for this time step and get wind speed and wind direction for the
            # nex time step
            logger.info('Time step: %d' % sim_time_s)
            logger.info("** Communicating with control center")

            # Write the turbine values to seperate files
            for t_idx, p_val in enumerate(turbine_powers):
                t_file = 't_%04d' % t_idx
                with open(t_file, "a") as file_object:
                    file_object.write('%.1f %.1f\n' % (sim_time_s, p_val))

            # Pass the current simulation time and the turbine powers from the previous time step
            message_code = 0
            # [34 + random.random(), 45.3+random.random() , 67+random.random()]
            message_from_client_array = [
                sim_time_s] + [wind_speed, wind_direction] + turbine_powers + turbine_wind_directions

            # Send helics message to Control Center
            # publish on topic: status
            self.send_via_helics("status", str(message_from_client_array))
            logger.info(
                "** Message Sent: {}".format(message_from_client_array))

            # Subscribe to helics messages from control center:
            incoming_messages = self.helics_connector.get_all_waiting_messages()
            if incoming_messages != {}:
                self.message_from_server = list(ast.literal_eval(
                    incoming_messages["control"]["message"]))
            else:
                self.message_from_server = None
            #  Now get the wind speed and wind direction back
            if self.message_from_server != None:
                logger.info(
                    "** Received reply {}: {}".format(sim_time_s, self.message_from_server))

                # Unpack the reply and update wind speed and wind direction
                # Get wind speed and wind direction for the next time step

                received_data = self.message_from_server
                wind_speed = float(received_data[1])
                wind_direction = float(received_data[2])

            # Advance simulation time
            sim_time_s += 1
            self.sync_time_helics(self.absolute_helics_time + self.deltat)

    # TODO cleanup code to move publish and subscribe here.

    def process_endpoint_event(self, msg):
        pass

    def process_periodic_endpoint(self):
        pass

    def process_periodic_publication(self):
        # Periodically publish data to the surrpogate
        pass

    def process_subscription_messages(self, msg):
        pass


def launch_dummy_amr_wind():
    config = {
        "name": "dummy_amr_wind",
        "gridpack": {
        },
        "helics": {
            "deltat": 1,
            "subscription_topics": [
                "control"

            ],
            "publication_topics": [
                "status"

            ],
            "endpoints": [
            ]
        },

        "publication_interval": 1,
        "endpoint_interval": 1,
        "starttime": 0,
        "stoptime": 100,
        "Agent": "dummy_amr_wind"

    }
    obj = DummyAMRWind(config)
    obj.run_helics_setup()
    obj.enter_execution(function_targets=[],
                        function_arguments=[[]])


launch_dummy_amr_wind()
