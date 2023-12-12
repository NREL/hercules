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

from SEAS.federate_agent import FederateAgent

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

# Define a function to read the amrwind input file
# Note simply copied from emulator
def read_amr_wind_input(amr_wind_input):

    # Probably want a file not found error instead
    return_dict = {}

    with open(amr_wind_input) as fp:
        Lines = fp.readlines()

        # Find the actuators
        for line in Lines:
            if 'Actuator.labels' in line:
                turbine_labels = line.split()[2:]
                num_turbines = len(turbine_labels)

        # Find the diameter
        for line in Lines:
            if 'rotor_diameter' in line:
                D = float(line.split()[-1])

        # Get the turbine locations
        turbine_locations = []
        for label in turbine_labels:
            for line in Lines:
                if 'Actuator.%s.base_position' % label in line:
                    locations = tuple([float(f)
                                        for f in line.split()[-3:-1]])
                    turbine_locations.append(locations)

        return_dict = {
            'num_turbines': num_turbines,
            'turbine_labels': turbine_labels,
            'rotor_diameter': D,
            'turbine_locations': turbine_locations
        }


    return return_dict


class DummyAMRWind(FederateAgent):
    def __init__(self, config_dict ,amr_wind_input):
        super(DummyAMRWind, self).__init__(
            name=config_dict['name'], 
            feeder_num=0, 
            starttime=config_dict['starttime'], 
            endtime=config_dict['stoptime'], 
            agent_num=0, 
            config_dict=config_dict)
        
        self.config_dict = config_dict

        # Read the amrwind input file
        self.amr_wind_input = amr_wind_input
        self.amr_wind_input_dict = read_amr_wind_input(self.amr_wind_input)

        # Get the number of turbines
        self.num_turbines = self.amr_wind_input_dict['num_turbines']

        # Print the number of turbines
        logger.info("Number of turbines: {}".format(self.num_turbines))

    def run(self):

        # Initialize the values
        turbine_powers = np.zeros(self.num_turbines)
        sim_time_s = 0.  # initialize time to 0
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

        logger.info("** Intial Wind Speed: {}".format(amr_wind_speed))
        logger.info("** Intial Wind Direction: {}".format(amr_wind_direction))
        logger.info("...STARTING TIME LOOP...")

        
        self.message_from_server = None

        while self.absolute_helics_time < (self.endtime - self.starttime + 1):

            # SIMULATE A CALCULATION STEP IN AMR WIND=========================
            logger.info("Calculating simulation time: %.1f" % sim_time_s)

            # Compute the turbine power using a simple formula
            turbine_powers = np.ones(
                self.num_turbines) * amr_wind_speed**3 + np.random.rand(self.num_turbines) * 50

            # Scale down later turbines as if waked
            turbine_powers[int(self.num_turbines/2):] = 0.75 * \
                turbine_powers[int(self.num_turbines/2):]

            # Convert to a list
            turbine_powers = turbine_powers.tolist()

            # ================================================================
            # Communicate with control center
            # Send the turbine powers for this time step and get wind speed and wind direction for the
            # nex time step
            logger.info('Time step: %d' % sim_time_s)
            logger.info("** Communicating with control center")
            message_from_client_array = [
                sim_time_s, amr_wind_speed, amr_wind_direction] + turbine_powers

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

                # Note dummy doesn't currently use received info for anything

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


def launch_dummy_amr_wind(amr_input_file):

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
        "stoptime": 1000,
        "Agent": "dummy_amr_wind"

    }
    obj = DummyAMRWind(config, amr_input_file)
    obj.run_helics_setup()
    obj.enter_execution(function_targets=[],
                        function_arguments=[[]])

