# Using PySAM to predict PV power based on weather data
# code originally copied from https://github.com/NREL/pysam/blob/main/Examples/NonAnnualSimulation.ipynb

import json

# import os
import numpy as np
import pandas as pd
import PySAM.Pvsamv1 as pvsam


class SolarPySAM:
    def __init__(self, input_dict, dt):
        # load weather data
        if input_dict["weather_file_name"]: # using a weather file
            data = pd.read_csv(input_dict["weather_file_name"])
        else: # using an input dictionary
            data = pd.DataFrame.from_dict(input_dict["weather_data_input"])

        print(data)
        data["Timestamp"] = pd.DatetimeIndex(
                pd.to_datetime(data["Timestamp"], format="ISO8601", utc=True)
        )
        data = data.set_index("Timestamp")
        
        # print('input_dict = ')
        # print(input_dict)

        # print('filename = ', input_dict["system_info_file_name"])
        # print('cwd = ',os.getcwd())
        # set PV system model parameters
        if input_dict["system_info_file_name"]: # using system info json file
            with open(input_dict["system_info_file_name"], "r") as f:
                model_params = json.load(f)
            sys_design = {
                "ModelParams": model_params,
                "Other": {"lat": 39.7442, "lon": -105.1778, "elev": 1829},
            }
        else: # using system info data dictionary in input file
            # sys_design = pvsam.default("FlatPlatePVSingleOwner") # use a default if none provided
            sys_design = input_dict["system_info_data_input"]
            print("sys_design")
            print(sys_design)
            print("model_params")
            print(sys_design["ModelParams"])

        self.model_params = sys_design["ModelParams"]
        self.elev = sys_design["Other"]["elev"]
        self.lat = sys_design["Other"]["lat"]
        self.lon = sys_design["Other"]["lon"]
        self.tz = data.index[0].utcoffset().total_seconds() / 60 / 60

        # Define needed inputs
        self.needed_inputs = {}
        self.data = data
        self.dt = dt

        # Save the initial condition
        self.power_mw = input_dict["initial_conditions"]["power"]
        self.dc_power_mw = input_dict["initial_conditions"]["power"]
        self.irradiance = input_dict["initial_conditions"]["irradiance"]
        self.aoi = 0

    def return_outputs(self):
        return {
            "power": self.power_mw,
            "dc_power": self.dc_power_mw,
            "irradiance": self.irradiance,
            "aoi": self.aoi,
        }

    def step(self, inputs):
        # print('inputs',inputs)

        # predict power
        system_model = pvsam.new()
        system_model.AdjustmentFactors.constant = 0
        system_model.AdjustmentFactors.dc_constant = 0

        for k, v in self.model_params.items():
            try:
                system_model.value(k, v)
            except Exception:
                print(k)
        #### TODO: Check with Brooke about this "except KeyError" line ####
                # Brooke: I got errors with KeyError so changed it to Exception and it's working
        # print('model params = ',self.model_params)

        print("sim_time_s = ", inputs["py_sims"]["inputs"]["sim_time_s"])
        sim_timestep = int(inputs["py_sims"]["inputs"]["sim_time_s"] / self.dt)
        print("sim_timestep = ", sim_timestep)

        data = self.data.iloc[[sim_timestep]]  # a single timestep
        # TODO - replace sim_timestep with seconds in sim_time_s and find corresponding
        #           timestep in weather file

        weather_data = np.array(
            [
                data.index.year,
                data.index.month,
                data.index.day,
                data.index.hour,
                data.index.minute,
                data["SRRL BMS Direct Normal Irradiance (W/m²_irr)"],
                data["SRRL BMS Diffuse Horizontal Irradiance (W/m²_irr)"],
                data["SRRL BMS Global Horizontal Irradiance (W/m²_irr)"],
                data["SRRL BMS Wind Speed at 19' (m/s)"],
                data["SRRL BMS Dry Bulb Temperature (°C)"],
            ]
        )

        solar_resource_data = {
            "tz": self.tz,  # timezone
            "elev": self.elev,  # elevation
            "lat": self.lat,  # latitude
            "lon": self.lon,  # longitude
            "year": tuple(weather_data[0]),  # year
            "month": tuple(weather_data[1]),  # month
            "day": tuple(weather_data[2]),  # day
            "hour": tuple(weather_data[3]),  # hour
            "minute": tuple(weather_data[4]),  # minute
            "dn": tuple(weather_data[5]),  # direct normal irradiance
            "df": tuple(weather_data[6]),  # diffuse irradiance
            "gh": tuple(weather_data[7]),  # global horizontal irradiance
            "wspd": tuple(weather_data[8]),  # windspeed
            "tdry": tuple(weather_data[9]),  # dry bulb temperature
        }

        system_model.SolarResource.assign({"solar_resource_data": solar_resource_data})
        system_model.AdjustmentFactors.assign({"constant": 0})
        # print('----------------------------------------------')
        # print('solar_resource_data = ',solar_resource_data)

        system_model.execute()
        out = system_model.Outputs.export()

        if sim_timestep == 0:
            with open("out-example.json", "w") as f:
                json.dump(out, f)

        ac = np.array(out["gen"]) / 1000  # quick fix for issue being fixed by darice
        dc = np.array(out["dc_net"]) / 1000

        self.power_mw = ac[0]  # calculating one timestep at a time
        self.dc_power_mw = dc[0]
        print("self.power_mw = ", self.power_mw)
        print("self.dc_power_mw = ", self.dc_power_mw)
        
        if self.power_mw < 0.0:
            self.power_mw = 0.0
        # NOTE: need to talk about whether to have time step in here or not

        self.irradiance = out["gh"][0]  # TODO check that gh is the accurate irradiance output
        print("self.irradiance = ", self.irradiance)

        self.aoi = out["subarray1_aoi"][0]  # angle of incidence

        return self.return_outputs()
