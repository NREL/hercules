import ast
import datetime as dt
import json
import os
import sys
import random
import time

import numpy as np
import pandas as pd

from SEAS.federate_agent import FederateAgent

LOGFILE = str(dt.datetime.now()).replace(
    ":", "_").replace(" ", "_").replace(".", "_")


class Emulator(FederateAgent):

    def __init__(self, controller, py_sims, input_dict):

        # Save the input dict to main dict
        self.main_dict = input_dict

        # Initialize the flattend main_dict
        self.main_dict_flat = {}

        # Initialize the output file
        self.output_file = 'hercules_output.csv'

        # Save timt step
        self.dt = input_dict['dt']

        # Initialize components
        self.controller = controller
        self.py_sims = py_sims

        # Update the input dict components
        self.main_dict['py_sims'] = self.py_sims.get_py_sim_dict()

        # HELICS dicts
        self.hercules_comms_dict = input_dict['hercules_comms']
        self.hercules_helics_dict = self.hercules_comms_dict['helics']
        self.helics_config_dict = self.hercules_comms_dict['helics']['config']

        # Write the time step into helics config dict
        self.helics_config_dict['helics']['deltat'] = self.dt

        # Initialize the Federate class for HELICS communitation
        super(Emulator, self).__init__(
            name=self.helics_config_dict['name'],
            starttime=self.helics_config_dict['starttime'],
            endtime=self.helics_config_dict['stoptime'],
            config_dict=self.helics_config_dict
        )

        # TODO: Store other things
        self.use_dash_frontend = self.helics_config_dict["use_dash_frontend"]
        self.KAFKA = self.helics_config_dict["KAFKA"]

        # TODO Copied direct from control_center.py but not actually ready yet
        if self.KAFKA:
            from dav_kafka_python.configuration import Configuration
            from dav_kafka_python.producer import PythonProducer
            # Kafka topic :
            self.topic = self.helics_config_dict["KAFKA_TOPIC"]
            print("KAFKA topic", self.topic)
            config = Configuration(env_path='./.env')
            self.python_producer = PythonProducer(config)
            self.python_producer.connect()

        # AMR wind files
        # Grab py sim details
        self.amr_wind_dict = self.hercules_comms_dict['amr_wind']

        self.n_amr_wind = len(self.amr_wind_dict)
        self.amr_wind_names = list(self.amr_wind_dict.keys())

        # Save information about amr_wind simulations
        for amr_wind_name in self.amr_wind_names:
            self.amr_wind_dict[amr_wind_name].update(
                self.read_amr_wind_input(
                    self.amr_wind_dict[amr_wind_name]['amr_wind_input_file']
                )
            )

        # TODO For now, need to assume for simplicity there is one and only
        # one AMR_Wind simualtion
        self.num_turbines = self.amr_wind_dict[self.amr_wind_names[0]
                                               ]['num_turbines']
        self.rotor_diameter = self.amr_wind_dict[self.amr_wind_names[0]
                                                 ]['rotor_diameter']
        self.turbine_locations = self.amr_wind_dict[self.amr_wind_names[0]
                                                    ]['turbine_locations']
        self.turbine_labels = self.amr_wind_dict[self.amr_wind_names[0]
                                                 ]['turbine_labels']

        # TODO In fugure could cover multiple farms
        # Initialize the turbine power array
        self.turbine_power_array = np.zeros(self.num_turbines)
        self.amr_wind_dict[self.amr_wind_names[0]
                           ]['turbine_powers'] = np.zeros(self.num_turbines)

        # TODO Could set up logging here

        # TODO Set interface comms to either dash or kenny's front end

        # TODO Set comms to non-helics based things like http polling

        # TODO not positive if this is the right place but I think it is
        # Hold here and wait for AMR Wind to respond
        # Note we're passing a few intiial wind speed and direction things
        # but we can come back to all that

        # FORMER CODE
        # self.logger.info("... waiting for initial connection from AMRWind")
        # list(self.pub.values())[0].publish(str("[-1,-1,-1]"))
        # self.logger.info(" #### Entering main loop #### ")

    def run(self):

        # TODO In future code that doesnt insist on AMRWInd can make this optional
        print("... waiting for initial connection from AMRWind")
        # Send initial connection signal to AMRWind
        # publish on topic: control
        self.send_via_helics("control", str("[-1,-1,-1]"))
        print(" #### Entering main loop #### ")

        # Initialize the first iteration flag
        self.first_iteration = True

        # Run simulation till  endtime
        while self.absolute_helics_time < self.endtime:

            # Loop till we reach simulation startime.
            if (self.absolute_helics_time < self.starttime):
                continue

            # Update controller and py sims
            self.main_dict['time'] = self.absolute_helics_time
            self.main_dict = self.controller.step(self.main_dict)
            self.py_sims.step(self.main_dict)
            self.main_dict['py_sims'] = self.py_sims.get_py_sim_dict()

            # Print the input dict
            # print(self.input_dict)

            # Subscribe to helics messages:
            incoming_messages = self.helics_connector.get_all_waiting_messages()
            if incoming_messages != {}:
                subscription_value = self.process_subscription_messages(
                    incoming_messages)
            else:
                print(
                    "Emulator: Did not receive subscription from AMRWind, setting everyhthing to 0.")
                subscription_value = [
                    0, 0, 0] + [0 for t in range(self.num_turbines)] + [0 for t in range(self.num_turbines)]

            # TODO Parse returns from AMRWind
            sim_time_s_amr_wind, wind_speed_amr_wind, wind_direction_amr_wind = subscription_value[
                :3]
            turbine_power_array = subscription_value[3:3+self.num_turbines]
            turbine_wd_array = subscription_value[3+self.num_turbines:]
            self.wind_speed = wind_speed_amr_wind
            self.wind_direction = wind_direction_amr_wind

            # Assign Py_sim outputs
            if self.main_dict['py_sims']:
                self.main_dict['py_sims']['inputs']['available_power'] = sum(turbine_power_array)


            ## TODO add other parameters that need to be logged to csv here. 
            # Write turbine power and turbine wind direction to csv logfile. 
            aa = [str(xx) for xx in turbine_power_array]
            xyz = ",".join(aa)
            bb = [str(xx) for xx in turbine_wd_array]
            zyx = ",".join(bb)
            with open(f'{LOGFILE}.csv', 'a') as filex:
                filex.write(str(self.absolute_helics_time) + ',' + str(sim_time_s_amr_wind) + ',' + str(
                    wind_speed_amr_wind) + ',' + str(wind_direction_amr_wind) + ',' + xyz + ',' + zyx + os.linesep)


            # TODO F-Strings
            print("=======================================")
            print("AMRWindTime:", sim_time_s_amr_wind)
            print("AMRWindSpeed:", wind_speed_amr_wind)
            print("AMRWindDirection:", wind_direction_amr_wind)
            print("AMRWindTurbinePowers:", turbine_power_array)
            print(" AMRWIND number of turbines here: ", self.num_turbines)
            print("AMRWindTurbineWD:", turbine_wd_array)
            print("=======================================")

            # Process periocdic functions.
            self.process_periodic_publication()

            # Send control center values through Kafka if enabled:
            if self.KAFKA:
                key = json.dumps({"key": "wind_tower"})
                value = json.dumps({"helics_time": self.absolute_helics_time, "bucket": "wind_tower", "AMRWind_speed": wind_speed_amr_wind,
                                    "AMRWind_direction": wind_direction_amr_wind, "AMRWind_time": sim_time_s_amr_wind})
                self.python_producer.write(key=key, value=value,
                                           topic=self.topic, token='test-token')

            # Store turbine powers back to the dict
            # TODO hard-coded for now assuming only one AMR-WIND
            self.amr_wind_dict[self.amr_wind_names[0]
                               ]['turbine_powers'] = turbine_power_array
            self.turbine_power_array = turbine_power_array
            self.amr_wind_dict[self.amr_wind_names[0]
                               ]['sim_time_s_amr_wind'] = sim_time_s_amr_wind

            # Send turbine powers through Kafka if enabled:
            if self.KAFKA:
                if len(turbine_power_array) == 0:
                    turbine_power_array = np.ones(self.num_turbines)*-1.0
                for t in range(self.num_turbines):
        
                        keyname = f"wind_turbine_{t}"
                        key = json.dumps({"key": keyname})
                        value = json.dumps({"helics_time": self.currenttime, "bucket":  keyname, "turbine_wd_direction": turbine_wd_array[t], "power": turbine_power_array[
                            t], "AMRWind_speed": wind_speed_amr_wind, "AMRWind_direction": wind_direction_amr_wind, "AMRWind_time": sim_time_s_amr_wind})
                        self.python_producer.write(
                            key=key, value=value, topic=self.topic, token='test-token')

            self.sync_time_helics(self.absolute_helics_time + self.deltat)

            # Log the input dict
            self.log_main_dict()

            # If this is first iteration print the input dict
            # And turn off the first iteration flag
            if self.first_iteration:
                print(self.main_dict)
                self.first_iteration = False

                # Echo the dictionary to a seperate file in case it is helpful 
                # to see full dictionary in interpreting log
                
                original_stdout = sys.stdout
                with open('main_dict.echo', 'w') as f_i:
                    sys.stdout = f_i # Change the standard output to the file we created.
                    print(self.main_dict)
                    sys.stdout = original_stdout # Reset the standard output to its original value

    def recursive_flatten_main_dict(self, nested_dict, prefix = ''):

        # Recursively flatten the input dict
        for k, v in nested_dict.items():
            if isinstance(v, dict):
                self.recursive_flatten_main_dict(v, prefix + k + '.')
            else:
                # If v is a list or np.array, enter each element seperately
                if isinstance(v, (list, np.ndarray)):
                    for i, vi in enumerate(v):
                        if isinstance(vi, (int, float)):
                            self.main_dict_flat[prefix + k + '.%03d' % i] = vi

                # If v is a string, int, or float, enter it directly
                if isinstance(v, (int, float)):
                    self.main_dict_flat[prefix + k] = v


    def log_main_dict(self):
        
        # Update the flattened input dict
        self.recursive_flatten_main_dict(self.main_dict)

        # Add the current time
        self.main_dict_flat['clock_time'] = dt.datetime.now()

        # The keys and values as two lists
        keys = list(self.main_dict_flat.keys())
        values = list(self.main_dict_flat.values())

        # If this is first iteration, write the keys as csv header
        if self.first_iteration:
            with open(self.output_file, 'w') as filex:
                filex.write(','.join(keys) + os.linesep)

        # Load the csv header and check if it matches the current keys
        with open(self.output_file, 'r') as filex:
            header = filex.readline().strip().split(',')
            if header != keys:
                print("WARNING: Input dict keys have changed since first iteration.\
                        Not writing to csv file.")
                return

        # Append the values to the csv file
        with open(self.output_file, 'a') as filex:
            filex.write(','.join([str(v) for v in values]) + os.linesep)



    def parse_input_yaml(self, filename):
        pass

    def process_subscription_messages(self, msg):
        # process data from HELICS subscription
        print(
            f"{self.name}, {self.absolute_helics_time} subscribed to message {msg}", flush=True)
        try:
            return list(ast.literal_eval(str(msg["status"]["message"])))
        except Exception as e:
            print(f"Subscription error:  {e} , returning 0s ", flush=True)
            return [0, 0, 0] + [0 for t in range(self.num_turbines)] + [0 for t in range(self.num_turbines)]

    def process_periodic_publication(self):
        # Periodically publish data to the surrogate

        # self.get_signals_from_front_end()
        # self.set_wind_speed_direction()

        #yaw_angles = [270 for t in range(self.num_turbines)]
        yaw_angles = [240 for t in range(self.num_turbines)]
        # log these in kafka
        #yaw_angles[1] = 260

        # Send timing and yaw information to AMRWind via helics
        # publish on topic: control
        tmp = np.array([self.absolute_helics_time, self.wind_speed,
                       self.wind_direction] + yaw_angles).tolist()

        self.send_via_helics("control", str(tmp))

    def process_endpoint_event(self, msg):
        pass

    def process_periodic_endpoint(self):
        pass

    def read_amr_wind_input(self, amr_wind_input):

        # TODO this function is ugly and uncommented

        # TODO Initialize to empty in case doesn't run
        # Probably want a file not found error instead
        return_dict = {}

        with open(amr_wind_input) as fp:
            Lines = fp.readlines()

            # Find the actuators
            for line in Lines:
                if 'Actuator.labels' in line:
                    turbine_labels = line.split()[2:]
                    num_turbines = len(turbine_labels)

            self.num_turbines = num_turbines
            print("Number of turbines in amrwind: ", num_turbines)

            aa = [f"power_{i}" for i in range(num_turbines)]
            xyz = ",".join(aa)
            bb = [f"turbine_wd_direction_{i}" for i in range(
                num_turbines)]
            zyx = ",".join(bb)
            with open(f'{LOGFILE}.csv', 'a') as filex:
                filex.write('helics_time' + ',' + 'AMRwind_time' + ',' +
                            'AMRWind_speed' + ',' + 'AMRWind_direction' + ',' + xyz + ',' + zyx + os.linesep)

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

            print(return_dict)

            # Write header for logfile: 
            aa = [f"power_{i}" for i in range(self.num_turbines)]
            xyz = ",".join(aa)
            bb = [f"turbine_wd_direction_{i}" for i in range(
                self.num_turbines)]
            zyx = ",".join(bb)
            with open(f'{LOGFILE}.csv', 'a') as filex:
                filex.write('helics_time' + ',' + 'AMRwind_time' + ',' +
                            'AMRWind_speed' + ',' + 'AMRWind_direction' + ',' + xyz + ',' + zyx + os.linesep)


        return return_dict
