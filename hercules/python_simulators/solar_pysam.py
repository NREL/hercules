# Using PySAM to predict PV power based on weather data
# code originally copied from https://github.com/NREL/pysam/blob/main/Examples/NonAnnualSimulation.ipynb

import numpy as np
import pandas as pd
import json
import PySAM.Pvwattsv7 as pvwatts

class SolarPySAM():

    def __init__(self, input_dict, dt):

        # load weather data
        data = pd.read_csv(input_dict["weather_file_name"]) # TODO - replace this with input
        data["Timestamp"] = pd.DatetimeIndex(pd.to_datetime(data["Timestamp"], format='ISO8601', utc=True))
        data = data.set_index("Timestamp")

        # set PV system model parameters
        sys_design = {
            "ModelParams": {
                "SystemDesign": {
                    "array_type": 2.0,
                    "azimuth": 180.0,
                    "dc_ac_ratio": 1.08,
                    "gcr": 0.592,
                    "inv_eff": 97.5,
                    "losses": 15.53,
                    "module_type": 2.0,
                    "system_capacity": 720,
                    "tilt": 0.0
                },
                "SolarResource": {
                }
            },
            "Other": {
                "lat": 39.7442,
                "lon": -105.1778,
                "elev": 1829
            }
        }
            
        self.model_params = sys_design['ModelParams']
        self.elev = sys_design['Other']['elev']
        self.lat = sys_design['Other']['lat']
        self.lon = sys_design['Other']['lon']
        self.tz = data.index[0].utcoffset().total_seconds()/60/60

        # Define needed inputs
        self.needed_inputs = {} # TODO: should this be a single timestep or the full time-series?
        self.data = data
        self.dt = dt

        # Save the initial condition
        self.power_mw = input_dict['initial_conditions']['power']
        self.dc_power_mw = input_dict['initial_conditions']['power']
        self.irradiance = input_dict['initial_conditions']['irradiance']
        self.aoi = 0

    def return_outputs(self):

        return {'power': self.power_mw,
                'dc_power': self.dc_power_mw,
                'irradiance': self.irradiance,
                'aoi': self.aoi
        }
    
    def step(self, inputs):
        #print('inputs',inputs)
        # print('dir(self) = ', dir(self))
        # predict power
        system_model = pvwatts.new()
        system_model.assign(self.model_params)

        # print('model params = ',self.model_params)

        print('sim_time_s = ',inputs['py_sims']['inputs']['sim_time_s'])
        sim_timestep = int(inputs['py_sims']['inputs']['sim_time_s']/self.dt)
        # sim_timestep = 0 # for debugging
        print('sim_timestep = ',sim_timestep)

        # if sim_timestep == 0:
        #     with open('model-params-example.json', 'w') as f:
        #         json.dump(self.model_params, f)

        data = self.data.iloc[[sim_timestep]] # a single timestep
        # TODO - replace sim_timestep with seconds in sim_time_s

        weather_data = np.array([
            data.index.year,
            data.index.month,
            data.index.day,
            data.index.hour,
            data.index.minute,
            data['SRRL BMS Direct Normal Irradiance (W/m²_irr)'],
            data['SRRL BMS Diffuse Horizontal Irradiance (W/m²_irr)'],
            data['SRRL BMS Global Horizontal Irradiance (W/m²_irr)'],
            data["SRRL BMS Wind Speed at 19' (m/s)"],
            data['SRRL BMS Dry Bulb Temperature (°C)']
        ])

        solar_resource_data = {
                'tz': self.tz, # timezone
                'elev': self.elev, # elevation
                'lat': self.lat, # latitude
                'lon': self.lon, # longitude
                'year': tuple(weather_data[0]), # year
                'month': tuple(weather_data[1]), # month
                'day': tuple(weather_data[2]), # day
                'hour': tuple(weather_data[3]), # hour
                'minute': tuple(weather_data[4]), # minute
                'dn': tuple(weather_data[5]), # direct normal irradiance
                'df': tuple(weather_data[6]), # diffuse irradiance
                'gh': tuple(weather_data[7]), # global horizontal irradiance
                'wspd': tuple(weather_data[8]), # windspeed
                'tdry': tuple(weather_data[9]) # dry bulb temperature
                }

        system_model.SolarResource.assign({'solar_resource_data': solar_resource_data})
        system_model.AdjustmentFactors.assign({'constant': 0})
        print('----------------------------------------------')
        # print('solar_resource_data = ',solar_resource_data)

        system_model.execute()
        out = system_model.Outputs.export()
        #print('out = ',out)
        if sim_timestep == 0:
            with open('out-example.json', 'w') as f:
                json.dump(out, f)

        # ac = np.array(out['ac']) / 1000
        ac = np.array(out['ac']) / 1000 # quick fix for issue being fixed by darice
        dc = np.array(out['dc']) / 1000

        # predictions = pd.DataFrame({"ac": ac, "dc": dc}, columns = ['ac','dc'])
        # predictions = predictions.set_index(data.index.copy())     

        self.power_mw = ac[0] # calculating one timestep at a time
        self.dc_power_mw = dc[0]
        print('self.power_mw = ',self.power_mw)
        if self.power_mw < 0.0:
            self.power_mw = 0.0
        # NOTE: need to talk about whether to have time step in here or not
        # Need to put outputs into input/output structure

        self.irradiance = out['dn'][0] # TODO change this to irradiance = dn + df + gh?

        self.aoi = out['aoi'][0] # anle of incidence

        return self.return_outputs()




