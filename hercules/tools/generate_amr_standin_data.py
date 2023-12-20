"""
TODO:
1. Throw an error if the amr output data does not have the same time as the hercules input file
2. 


"""

import os

import matplotlib.pyplot as plt
import netCDF4 as ncdf
import numpy as np
import pandas as pd
from hercules.amr_wind_standin import read_amr_wind_input
from hercules.utilities import load_yaml


class StandinData:
    def __init__(
        self,
        method="user",
        amr_inp_path=None,
        amr_out_path=None,
        herc_inp_path=None,
        save_path=None,
    ):
        self.method = method

        # if self.method is not "user" then amr_data_path must be defined
        # if save_path is not given then use amr_inp_path

        self.amr_input_path = amr_inp_path
        self.amr_data_path = amr_out_path  # optional if self.method is "user"
        self.hercules_input_path = herc_inp_path
        self.standin_data_save_path = save_path

        self.parse_hercules_input(self.hercules_input_path)
        self.parse_amr_input(self.amr_input_path)

    def generate_standin_data(self, user_inputs=None):
        if self.method == "user":
            self.from_user_definition(**user_inputs)
        elif self.method == "amr_actuator":
            self.from_amr_actuators()
        elif self.method == "amr_openfast":
            self.from_amr_openfast()

    def from_user_definition(
        self,
        time=None,
        amr_wind_speed=None,
        amr_wind_direction=None,
        turbine_powers=None,
    ):
        if (
            (time is not None)
            & (amr_wind_speed is not None)
            & (amr_wind_direction is not None)
            & (turbine_powers is not None)
        ):
            pass
        else:
            turb_rating = 1000
            time = np.arange(self.time_start, self.time_stop, self.time_delta)
            amr_wind_speed = np.linspace(0, 20, len(time))
            amr_wind_direction = np.linspace(200, 240, len(time))

            turbine_powers = np.zeros([len(time), self.num_turbines])

            for i in range(len(time)):
                turb_powers = (
                    np.ones(self.num_turbines) * amr_wind_speed[i] ** 3
                    + np.random.rand(self.num_turbines) * 50
                )
                turb_powers[int(self.num_turbines / 2) :] = (
                    0.75 * turb_powers[int(self.num_turbines / 2) :]
                )
                turb_powers = [np.min([turb_rating, tp]) for tp in turb_powers]
                turbine_powers[i, :] = turb_powers

        self.time = time
        self.amr_wind_speed = amr_wind_speed
        self.amr_wind_direction = amr_wind_direction
        self.turbine_powers = turbine_powers

    def from_amr_actuators(self):
        case_folder = self.amr_data_path

        # TODO: make this more general. It might not be "actuator14400"
        actuator_dir = os.path.join(case_folder, "post_processing/actuator14400")

        # TODO: if there are a different number of actuators in the amr data files
        #       and the amr input file, raise an error. They probably do not belong
        #       to the same run
        actuators = os.listdir(os.path.join(case_folder, actuator_dir))

        actuator_data = []
        for actuator_name in actuators:
            rootgrp = ncdf.Dataset(
                os.path.join(os.path.join(case_folder, actuator_dir), actuator_name),
                "r",
                format="NETCDF4",
            )

            rootgrp_name = list(rootgrp.groups.keys())[0]

            # What is the difference between vref and vdisk?
            # vref = rootgrp["/".join([rootgrp_name, "vref"])][:]
            vdisk = rootgrp["/".join([rootgrp_name, "vdisk"])][:]

            v_abs = np.linalg.norm(vdisk, axis=1)
            # What direction is 0 degrees?
            v_direction = 360 / (2 * np.pi) * np.arctan2(vdisk[:, 1], vdisk[:, 0])

            time = rootgrp["/".join([rootgrp_name, "time"])][:]
            power = rootgrp["/".join([rootgrp_name, "power"])][:]

            actuator_data.append(
                {
                    "actuator_name": rootgrp_name,
                    "time": time,
                    "v_direction": v_direction,
                    "v_abs": v_abs,
                    "power": power,
                }
            )

        if (actuator_data[1]["time"] == actuator_data[0]["time"]).all():
            time = actuator_data[0]["time"]

        amr_wind_speed = np.mean([ad["v_abs"] for ad in actuator_data], axis=0)
        amr_wind_direction = np.mean([ad["v_direction"] for ad in actuator_data], axis=0)

        powers = np.stack([ad["power"] for ad in actuator_data], axis=1)

        self.time = time
        self.amr_wind_speed = amr_wind_speed
        self.amr_wind_direction = amr_wind_direction
        self.turbine_powers = powers

    def from_amr_openfast(self):
        pass

    def save(self):
        df_dict = {
            "time": self.time,
            "amr_wind_speed": self.amr_wind_speed,
            "amr_wind_direction": self.amr_wind_direction,
        }

        for i in range(self.num_turbines):
            df_dict.update({f"turbine_power_{i}": self.turbine_powers[:, i]})

        df = pd.DataFrame(df_dict)
        df.to_csv(os.path.join(self.standin_data_save_path, "amr_standin_data.csv"))

    def plot(self):
        fig, ax = plt.subplots(3, 1, sharex="col")

        ax[0].plot(self.time, self.amr_wind_speed)
        ax[0].set_title("wind speed [m/s]")
        ax[1].plot(self.time, self.amr_wind_direction)
        ax[1].set_title("wind direction [deg]")
        ax[2].plot(self.time, self.turbine_powers)
        ax[2].set_title("turbine powers")
        ax[2].set_xlabel("time")

    def parse_amr_input(self, fname):
        amr_input_dict = read_amr_wind_input(fname)
        self.num_turbines = amr_input_dict["num_turbines"]
        self.turbine_labels = amr_input_dict["turbine_labels"]
        self.rotor_diameter = amr_input_dict["rotor_diameter"]
        self.turbine_locations = amr_input_dict["turbine_locations"]

    def parse_hercules_input(self, fname):
        hercules_input = load_yaml(fname)
        self.time_start = hercules_input["hercules_comms"]["helics"]["config"]["starttime"]
        self.time_stop = hercules_input["hercules_comms"]["helics"]["config"]["stoptime"]
        self.time_delta = hercules_input["dt"]


# Example usage
if __name__ == "__main__":
    # # generate standin data file from amr-wind outputs
    # fpaths = {
    #   "amr_inp_path":
    #        "example_case_folders/06_amr_wind_standin_and_battery/amr_input.inp",
    #   "amr_out_path":
    #        "/Users/ztully/Documents/HERCULES/hercules_project/amr_wind_runs/2023_10_20",
    #   "herc_inp_path":
    #        "example_case_folders/06_amr_wind_standin_and_battery/hercules_input_000.yaml",
    #   "save_path":
    #        "example_case_folders/06_amr_wind_standin_and_battery",
    # }

    # SD = StandinData(method="amr_actuator", **fpaths)
    # SD.generate_standin_data()
    # SD.save()
    # SD.plot()

    # generate standin data file from user-defined timeseries
    fpaths = {
        "amr_inp_path": 
            "example_case_folders/06_amr_wind_standin_and_battery/amr_input.inp",
        # "amr_out_path":
        #       "/Users/ztully/Documents/HERCULES/hercules_project/amr_wind_runs/2023_10_20",
        "herc_inp_path":
            "example_case_folders/06_amr_wind_standin_and_battery/hercules_input_000.yaml",
        "save_path": 
            "example_case_folders/06_amr_wind_standin_and_battery",
    }
    SD = StandinData(method="user", **fpaths)

    # generate user inputs

    num_turbines = 2
    time_start = 0
    time_stop = 900
    time_delta = 0.5

    turb_rating = 1000
    time = np.arange(time_start, time_stop, time_delta)
    amr_wind_speed = np.linspace(0, 20, len(time))
    amr_wind_direction = np.linspace(200, 240, len(time))

    turbine_powers = np.zeros([len(time), num_turbines])
    for i in range(len(time)):
        turb_powers = (
            np.ones(num_turbines) * amr_wind_speed[i] ** 3 + np.random.rand(num_turbines) * 50
        )
        turb_powers[int(num_turbines / 2) :] = 0.75 * turb_powers[int(num_turbines / 2) :]
        turb_powers = [np.min([turb_rating, tp]) for tp in turb_powers]
        turbine_powers[i, :] = turb_powers

    my_inputs = {
        "time": time,
        "amr_wind_speed": amr_wind_speed,
        "amr_wind_direction": amr_wind_direction,
        "turbine_powers": turbine_powers,
    }

    SD.generate_standin_data(my_inputs)
    SD.save()
