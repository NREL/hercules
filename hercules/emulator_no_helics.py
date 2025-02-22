import datetime as dt
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

LOGFILE = str(dt.datetime.now()).replace(":", "_").replace(" ", "_").replace(".", "_")

Path("outputs").mkdir(parents=True, exist_ok=True)


class EmulatorNoHelics:
    def __init__(self, controller, py_sims, input_dict):
        # Make sure output folder exists
        Path("outputs").mkdir(parents=True, exist_ok=True)

        # Save the input dict to main dict
        self.main_dict = input_dict

        # Initialize the flattend main_dict
        self.main_dict_flat = {}

        # Initialize the output file
        if "output_file" in input_dict:
            self.output_file = input_dict["output_file"]
        else:
            self.output_file = "outputs/hercules_output.csv"

        # Save time step
        self.dt = input_dict["dt"]

        # Save time step, start time and end time
        self.dt = input_dict["dt"]
        self.starttime = input_dict["starttime"]
        self.endtime = input_dict["endtime"]
        self.total_simulation_time = self.endtime - self.starttime
        self.total_simulation_days = self.total_simulation_time / 86400
        self.time = 0.0

        # Initialize components
        self.controller = controller
        self.py_sims = py_sims

        # Update the input dict components
        self.main_dict["py_sims"] = self.py_sims.get_py_sim_dict()

        # Initialize time # TODO - does this belong in 'initial conditions' instead?
        if self.main_dict["py_sims"]:
            self.main_dict["py_sims"]["inputs"]["sim_time_s"] = self.starttime

        # Read in any external data
        self.external_data_all = {}
        if "external_data_file" in input_dict:
            self._read_external_data_file(input_dict["external_data_file"])
            self.external_signals = {}
            self.main_dict["external_signals"] = {}

        # TODO: NOT SURE WHETHER ANY OF THIS STUFF NEEDS TO BE BROUGHT IN
        # # TODO For now, need to assume for simplicity there is one and only
        # # one AMR_Wind simulation
        # self.num_turbines = self.amr_wind_dict[self.amr_wind_names[0]]["num_turbines"]
        # self.rotor_diameter = self.amr_wind_dict[self.amr_wind_names[0]]["rotor_diameter"]
        # self.turbine_locations = self.amr_wind_dict[self.amr_wind_names[0]]["turbine_locations"]
        # self.turbine_labels = self.amr_wind_dict[self.amr_wind_names[0]]["turbine_labels"]

        # # TODO In fugure could cover multiple farms
        # # Initialize the turbine power array
        # self.turbine_power_array = np.zeros(self.num_turbines)
        # self.amr_wind_dict[self.amr_wind_names[0]]["turbine_powers"] = np.zeros(self.num_turbines)
        # self.amr_wind_dict[self.amr_wind_names[0]]["turbine_wind_directions"] = [
        #     0.0
        # ] * self.num_turbines
        # # Write to hercules_comms so that controller can access
        # self.main_dict["hercules_comms"]["amr_wind"][self.amr_wind_names[0]]["turbine_powers"] = [
        #     0.0
        # ] * self.num_turbines
        # self.main_dict["hercules_comms"]["amr_wind"][self.amr_wind_names[0]][
        #     "turbine_wind_directions"
        # ] = [0.0] * self.num_turbines
        # self.main_dict["hercules_comms"]["amr_wind"][self.amr_wind_names[0]]["wind_direction"] = 0
        # self.main_dict["hercules_comms"]["amr_wind"][self.amr_wind_names[0]][
        #     "sim_time_s_amr_wind"
        # ] = 0

        # self.wind_speed = 0
        # self.wind_direction = 0

    def _read_external_data_file(self, filename):
        # Read in the external data file
        df_ext = pd.read_csv(filename)
        if "time" not in df_ext.columns:
            raise ValueError("External data file must have a 'time' column")

        # Interpolate the external data according to time.
        # Goes to 1 time step past stoptime specified in the input file.
        times = np.arange(
            self.helics_config_dict["starttime"],
            self.helics_config_dict["stoptime"] + (2 * self.dt),
            self.dt,
        )
        self.external_data_all["time"] = times
        for c in df_ext.columns:
            if c != "time":
                self.external_data_all[c] = np.interp(times, df_ext.time, df_ext[c])

    def enter_execution(self, function_targets=[], function_arguments=[[]]):
        # Record the current wall time
        self.start_time_wall = dt.datetime.now()

        # Run the main loop
        self.run()

        # Note the total elapsed time
        self.end_time_wall = dt.datetime.now()
        self.total_time_wall = self.end_time_wall - self.start_time_wall

        # Update the user on time performance
        print("=====================================")
        print(
            f"Total simulated time: {self.total_simulation_time} seconds ({self.total_simulation_days} days)"
        )
        print(f"Total wall time: {self.total_time_wall}")
        print(
            "Rate of simulation: ",
            f"{self.total_simulation_time/self.total_time_wall.total_seconds():.1f}x real time"
        )
        print("=====================================")

    def run(self):
        print(" #### Entering main loop #### ")

        self.first_iteration = True

        # Run simulation till endtime
        # while self.absolute_helics_time < self.endtime:
        while self.time < (self.endtime):
            print(self.time)

            for k in self.external_data_all:
                self.main_dict["external_signals"][k] = self.external_data_all[k][
                    self.external_data_all["time"] == self.time
                ][0]

            # Update controller and py sims
            # TODO: Update this when I've figured out time
            self.main_dict["time"] = self.time
            self.main_dict = self.controller.step(self.main_dict)
            if self.main_dict["py_sims"]:
                self.py_sims.step(self.main_dict)
                self.main_dict["py_sims"] = self.py_sims.get_py_sim_dict()

            # Log the current state
            self.log_main_dict()

            # If this is first iteration print the input dict
            # And turn off the first iteration flag
            if self.first_iteration:
                print(self.main_dict)
                self.save_main_dict_as_text()
                self.first_iteration = False

            # Update the time
            self.time = self.time + self.dt

    def recursive_flatten_main_dict(self, nested_dict, prefix=""):
        # Recursively flatten the input dict
        for k, v in nested_dict.items():
            if isinstance(v, dict):
                self.recursive_flatten_main_dict(v, prefix + k + ".")
            else:
                # If v is a list or np.array, enter each element seperately
                if isinstance(v, (list, np.ndarray)):
                    for i, vi in enumerate(v):
                        if isinstance(vi, (int, float)):
                            self.main_dict_flat[prefix + k + ".%03d" % i] = vi

                # If v is a string, int, or float, enter it directly
                if isinstance(v, (int, np.integer, float)):
                    self.main_dict_flat[prefix + k] = v

    def log_main_dict(self):
        # Update the flattened input dict
        self.recursive_flatten_main_dict(self.main_dict)

        # Add the current time
        self.main_dict_flat["clock_time"] = dt.datetime.now()

        # The keys and values as two lists
        keys = list(self.main_dict_flat.keys())
        values = list(self.main_dict_flat.values())

        # If this is first iteration, write the keys as csv header
        if self.first_iteration:
            with open(self.output_file, "w") as filex:
                filex.write(",".join(keys) + os.linesep)

        # Load the csv header and check if it matches the current keys
        with open(self.output_file, "r") as filex:
            header = filex.readline().strip().split(",")
            if header != keys:
                print(
                    "WARNING: Input dict keys have changed since first iteration.\
                        Not writing to csv file."
                )
                return

        # Append the values to the csv file
        with open(self.output_file, "a") as filex:
            filex.write(",".join([str(v) for v in values]) + os.linesep)

    def save_main_dict_as_text(self):
        # Echo the dictionary to a seperate file in case it is helpful
        # to see full dictionary in interpreting log

        original_stdout = sys.stdout
        with open("outputs/main_dict.echo", "w") as f_i:
            sys.stdout = f_i  # Change the standard output to the file we created.
            print(self.main_dict)
            sys.stdout = original_stdout  # Reset the standard output to its original value

    def parse_input_yaml(self, filename):
        pass
