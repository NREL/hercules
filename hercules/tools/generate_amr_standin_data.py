"""
TODO:
1. Make two options: standin data from amr-wind outputs or from user definition
2. Save amr-wind standin data in amr-wind outputs location
3. Make into a class


"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import netCDF4 as ncdf

from hercules.utilities import load_yaml
from hercules.dummy_amr_wind import read_amr_wind_input

class StandinData:
    
    def __init__(self):
        
        self.amr_input_path = None
        self.amr_data_path = None
        self.hercules_input_path = None
        self.standin_data_save_path = None


        self.parse_hercules_input(self.hercules_input_path)
        self.parse_amr_input(self.amr_input_path)

    def generate_standin_data(self):
        pass

    def from_user_definition(self):
        turb_rating = 1000
        time = np.arange(self.time_start, self.time_stop, self.time_delta)
        amr_wind_speed = np.linspace(0, 20, len(time))
        amr_wind_direction = np.linspace(200, 240, len(time))

        turbine_powers = np.zeros([len(time), self.num_turbines])

        for i in range(len(time)):
            turb_powers = (
                np.ones(self.num_turbines) * amr_wind_speed[i] ** 3 + np.random.rand(self.num_turbines) * 50
            )
            turb_powers[int(self.num_turbines / 2) :] = 0.75 * turb_powers[int(self.num_turbines / 2) :]
            turb_powers = [np.min([turb_rating, tp]) for tp in turb_powers]
            turbine_powers[i, :] = turb_powers

        self.time = time
        self.amr_wind_speed = amr_wind_speed
        self.amr_wind_direction = amr_wind_direction
        self.turbine_powers = turbine_powers

    def from_amr_actuators(self):
        case_folder = self.amr_data_path

        # TODO: make this more general. It might not be "actuator14400"
        actuator_dir = os.join(case_folder, "post_processing/actuator14400")

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
            vref = rootgrp["/".join([rootgrp_name, "vref"])][:]
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

        powers = []

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
        df.to_csv(self.standin_data_save_path)


    def plot(self):
        fig, ax = plt.subplots(3, 1, sharex="col")

        ax[0].plot(time, amr_wind_speed)
        ax[0].set_title("wind speed [m/s]")
        ax[1].plot(time, amr_wind_direction)
        ax[1].set_title("wind direction [deg]")
        ax[2].plot(time, turbine_powers)
        ax[2].set_title("turbine powers")
        ax[2].set_xlabel("time")

    def parse_amr_input(self, fname):
        amr_input_dict = read_amr_wind_input(fname)
        self.num_turbines = amr_input_dict["num_turbines"]
        self.turbine_labels = amr_input_dict["turbine_labels"]
        self.rotor_diameter = amr_input_dict["rotor_diamter"]
        self.turbine_locations = amr_input_dict["turbine_locations"]

    def parse_hercules_input(self, fname):
        hercules_input = load_yaml(fname)
        self.time_start = hercules_input["hercules_comms"]["helics"]["config"]["starttime"]
        self.time_stop = hercules_input["hercules_comms"]["helics"]["config"]["stoptime"]
        self.time_delta = hercules_input["dt"]




n_turbines = 2
turb_rating = 1000  # kW


time_start = 0
time_end = 1000
time_delta = 1
time = np.arange(time_start, time_end, time_delta)

amr_wind_speed = np.linspace(0, 20, len(time))
amr_wind_direction = np.linspace(200, 240, len(time))

turbine_powers = np.zeros([len(time), n_turbines])

for i in range(len(time)):
    turb_powers = (
        np.ones(n_turbines) * amr_wind_speed[i] ** 3 + np.random.rand(n_turbines) * 50
    )
    turb_powers[int(n_turbines / 2) :] = 0.75 * turb_powers[int(n_turbines / 2) :]
    turb_powers = [np.min([turb_rating, tp]) for tp in turb_powers]
    turbine_powers[i, :] = turb_powers

df_dict = {
    "time": time,
    "amr_wind_speed": amr_wind_speed,
    "amr_wind_direction": amr_wind_direction,
}

for i in range(n_turbines):
    df_dict.update({f"turbine_power_{i}": turbine_powers[:, i]})

df = pd.DataFrame(df_dict)
df.to_csv("project/battery_example/amr_standin_windpower.csv")

fig, ax = plt.subplots(3, 1, sharex="col")

ax[0].plot(time, amr_wind_speed)
ax[0].set_title("wind speed [m/s]")
ax[1].plot(time, amr_wind_direction)
ax[1].set_title("wind direction [deg]")
ax[2].plot(time, turbine_powers)
ax[2].set_title("turbine powers")




sim_time_s = 775.2

amr_wind_speed = np.interp(sim_time_s, df["time"], df["amr_wind_speed"])
amr_wind_direction = np.interp(sim_time_s, df["time"], df["amr_wind_direction"])
turbine_powers = [
    np.interp(sim_time_s, df["time"], df[f"turbine_power_{turb}"])
    for turb in range(n_turbines)
]


