import csv
import datetime as dt
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

LOGFILE = str(dt.datetime.now()).replace(":", "_").replace(" ", "_").replace(".", "_")

Path("outputs").mkdir(parents=True, exist_ok=True)


class EmulatorNoHelics:
    def __init__(self, controller, py_sims, input_dict, logger):
        # Make sure output folder exists
        Path("outputs").mkdir(parents=True, exist_ok=True)

        # Use the provided logger
        self.logger = logger

        # Save the input dict to main dict
        self.main_dict = input_dict

        # Initialize the flattend main_dict
        self.main_dict_flat = {}

        # Initialize the output file
        if "output_file" in input_dict:
            self.output_file = input_dict["output_file"]
        else:
            self.output_file = "outputs/hercules_output.csv"

        # Initialize the csv writer
        self.csv_file = None
        self.csv_writer = None
        self.header_written = False
        self.header = None

        # Initialize the csv buffer
        self.csv_buffer_size = 1000
        self.csv_buffer = []

        # Save time step
        self.dt = input_dict["dt"]

        # How often to update the user on current emulator time
        self.time_log_interval = 600  # seconds
        self.last_log_time = 0

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
        # Open the output file
        self.open_output_file()

        # Wrap this effort in a try block so on failure or completion sure to purge csv buffer
        try:
            # Record the current wall time
            self.start_time_wall = dt.datetime.now()

            # Run the main loop
            self.run()

            # Note the total elapsed time
            self.end_time_wall = dt.datetime.now()
            self.total_time_wall = self.end_time_wall - self.start_time_wall

            # Update the user on time performance
            self.logger.info("=====================================")
            self.logger.info(
                (
                    "Total simulated time: ",
                    f"{self.total_simulation_time} seconds ({self.total_simulation_days} days)",
                )
            )
            self.logger.info(f"Total wall time: {self.total_time_wall}")
            self.logger.info(
                (
                    "Rate of simulation: ",
                    f"{self.total_simulation_time/self.total_time_wall.total_seconds():.1f}",
                    "x real time",
                )
            )
            self.logger.info("=====================================")

        except Exception as e:
            # Log the error
            self.logger.error(f"Error during execution: {str(e)}", exc_info=True)
            # Re-raise the exception after cleanup
            raise

        finally:
            # Ensure the CSV file is properly flushed and closed
            self.logger.info("Closing output files and flushing buffers")
            self.flush_buffer()  # Flush any remaining buffered rows
            self.close_output_file()

    def run(self):
        self.logger.info(" #### Entering main loop #### ")

        self.first_iteration = True

        # Run simulation till endtime
        # while self.absolute_helics_time < self.endtime:
        while self.time < (self.endtime):
            # Log the current time
            if self.time - self.last_log_time > self.time_log_interval or self.first_iteration:
                self.last_log_time = self.time
                self.logger.info(f"Emulator time: {self.time} (ending at {self.endtime})")
                self.logger.info(f"--Percent completed: {100 * self.time / self.endtime:.2f}%")

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

            # If this is first iteration log the input dict
            # And turn off the first iteration flag
            if self.first_iteration:
                self.logger.info(self.main_dict)
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

    def open_output_file(self):
        """Open the output file with bufferinge."""
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(os.path.abspath(self.output_file))
        os.makedirs(output_dir, exist_ok=True)

        # Open the file with buffering
        self.csv_file = open(self.output_file, "a", newline="", buffering=8192)  # 8KB buffer
        self.csv_writer = csv.writer(self.csv_file)

        # Check if file is empty to determine if header needs to be written
        if os.path.getsize(self.output_file) == 0:
            self.header_written = False
        else:
            self.header_written = True
            # Read the header from file
            with open(self.output_file, "r") as f:
                self.header = f.readline().strip().split(",")

    def close_output_file(self):
        """Properly close the output file."""
        if self.csv_file:
            self.flush_buffer()
            self.csv_file.flush()
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None

    def flush_buffer(self):
        """Write buffered rows to the file."""
        if not self.csv_buffer:
            return

        for row in self.csv_buffer:
            self.csv_writer.writerow(row)

        # Clear the buffer
        self.csv_buffer = []

    def log_main_dict(self):
        # Update the flattened input dict
        self.recursive_flatten_main_dict(self.main_dict)

        # Add the current time
        self.main_dict_flat["clock_time"] = dt.datetime.now()

        # The keys and values as two lists
        keys = list(self.main_dict_flat.keys())
        values = list(self.main_dict_flat.values())

        # Ensure the output file is open
        if not self.csv_file:
            self.open_output_file()

        # Handle header
        if not self.header_written:
            self.csv_writer.writerow(keys)
            self.header = keys
            self.header_written = True
        elif self.header != keys:
            self.logger.warning(
                "Input dict keys have changed since first iteration. Not writing to csv file."
            )
            return

        # Add the values to the buffer
        self.csv_buffer.append(values)

        # Flush if buffer is full
        if len(self.csv_buffer) >= self.csv_buffer_size:
            self.flush_buffer()

        # # If this is first iteration, write the keys as csv header
        # if self.first_iteration:
        #     with open(self.output_file, "w") as filex:
        #         filex.write(",".join(keys) + os.linesep)

        # # Load the csv header and check if it matches the current keys
        # with open(self.output_file, "r") as filex:
        #     header = filex.readline().strip().split(",")
        #     if header != keys:
        #         self.logger.warning(
        #             "WARNING: Input dict keys have changed since first iteration.\
        #                 Not writing to csv file."
        #         )
        #         return

        # # Append the values to the csv file
        # with open(self.output_file, "a") as filex:
        #     filex.write(",".join([str(v) for v in values]) + os.linesep)

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
