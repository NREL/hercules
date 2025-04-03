# Using PySAM to predict PV power based on weather data
# code originally copied from https://github.com/NREL/pysam/blob/main/Examples/NonAnnualSimulation.ipynb

import numpy as np
import pandas as pd
import PySAM.Pvwattsv8 as pvwatts


class SolarPySAM:
    def __init__(self, input_dict, dt):

        print('trying to read in verbose flag')
        if "verbose" in input_dict:
            self.verbose = input_dict["verbose"]
            print('read in verbose flag = ',self.verbose)
        else:
            self.verbose = True # default value

        # load weather data
        if input_dict["weather_file_name"]:  # using a weather file
            data = pd.read_csv(input_dict["weather_file_name"])
        else:  # using an input dictionary
            data = pd.DataFrame.from_dict(input_dict["weather_data_input"])

        # print(data)
        data["Timestamp"] = pd.DatetimeIndex(pd.to_datetime(data["Timestamp"], format="ISO8601"))
        data = data.set_index("Timestamp")

        # convert to numpy array for speedup
        weather_data_array = data.reset_index().to_numpy()
        self.create_col_dict(data) # create dictionary for indexing to correct column of numpy array

        # print('input_dict = ')
        # print(input_dict)

        # set PV system model parameters
        sys_design = {
            "ModelParams": {
                "SystemDesign": {
                    "array_type": 3.0,
                    "azimuth": 180.0,
                    "dc_ac_ratio": input_dict["target_dc_ac_ratio"],
                    "gcr": 0.29999999999999999,
                    "inv_eff": 96,
                    "losses": 14.075660688264469,
                    "module_type": 2.0,
                    "system_capacity": input_dict["target_system_capacity_kW"],
                    "tilt": 0.0
                },
            },
            "Other": {
                "lat": input_dict["lat"],
                "lon": input_dict["lon"],
                "elev": input_dict["elev"],
            },
        }

        if self.verbose:
            print("sys_design")
            print(sys_design)
            print("model_params")
            print(sys_design["ModelParams"])

        self.model_params = sys_design["ModelParams"]
        self.elev = sys_design["Other"]["elev"]
        self.lat = sys_design["Other"]["lat"]
        self.lon = sys_design["Other"]["lon"]
        # self.tz = data.index[0].utcoffset().total_seconds() / 60 / 60
        try:
            self.tz = data.index[0].utcoffset().total_seconds() / 60 / 60
        except Exception:
            print("Error: Timezone (UTC offset) required in input solar weather file timestamps.")
        
        if self.verbose:
            print("self.tz = ", self.tz)

        self.needed_inputs = {}
        self.data = weather_data_array
        self.dt = dt

        # Save the initial condition
        self.power_mw = input_dict["initial_conditions"]["power"]
        self.dc_power_mw = input_dict["initial_conditions"]["power"]
        self.dni = input_dict["initial_conditions"]["dni"]
        self.aoi = 0

        # create pysam model
        system_model = pvwatts.new()
        system_model.assign(self.model_params)

        system_model.AdjustmentFactors.adjust_constant = 0
        system_model.AdjustmentFactors.dc_adjust_constant = 0

        for k, v in self.model_params.items():
            try:
                system_model.value(k, v)
            except Exception:
                print(k)

        self.system_model = system_model

        

    def return_outputs(self):
        return {
            "power_mw": self.power_mw,
            "dni": self.dni,
            "aoi": self.aoi,
        }

    def control(self, power_setpoint_mw=None):
        """
        Low-level controller to enforce PV plant power setpoints
        Notes:
        - Currently applies uniform curtailment to entire plant
        - DC power output is not controlled because it is not used elsewhere in the code

        Inputs
        - power_setpoint_mw: [MW] the desired total PV plant output
        """
        # modify power output based on setpoint
        if power_setpoint_mw is not None:
            if self.verbose:
                print("power_setpoint = ", power_setpoint_mw)
            if self.power_mw > power_setpoint_mw:
                self.power_mw = power_setpoint_mw
                # Keep track of power that could go to charging battery
                self.excess_power = self.power_mw - power_setpoint_mw
            if self.verbose:
                print("self.power_mw after control = ", self.power_mw)

    def step(self, inputs):
        # print('-------------------')
        # print('inputs',inputs)
        # print('-------------------')
        # print('vars(self) = ',vars(self))

        sim_time_s = inputs["time"]
        if self.verbose:
            print("sim_time_s = ", sim_time_s)

        # select appropriate row based on current time
        time_index = self.data[0,0] + pd.Timedelta(seconds=sim_time_s)
        if self.verbose:
            print("time_index = ", time_index)
        try:
            condition = self.data[:,0] == time_index
            row_index = np.where(condition)[0][0]
        except Exception:
            print("ERROR: Input solar weather file doesn't have data at requested timestamp.")
            print(
                "Try setting dt in .yaml file equal to (or a multiple of) dt in solar weather file."
            )

        # forcing this to be an array of lists so that tuple doesn't 
        # unpack it in solar_resource_data
        weather_data = np.array( 
            [
                [time_index.year], 
                [time_index.month],
                [time_index.day],
                [time_index.hour],
                [time_index.minute],
                [self.data[row_index,self.col_dict['dni_col']]],
                [self.data[row_index,self.col_dict['dhi_col']]],
                [self.data[row_index,self.col_dict['ghi_col']]],
                [self.data[row_index,self.col_dict['ws_col']]],
                [self.data[row_index,self.col_dict['temp_col']]],
            ]
        )
        # print('weather_data = ', weather_data)

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

        self.system_model.SolarResource.assign({"solar_resource_data": solar_resource_data})
        self.system_model.AdjustmentFactors.assign({"constant": 0})
        # print('----------------------------------------------')
        # print('solar_resource_data = ',solar_resource_data)

        self.system_model.execute()

        ac = np.array(self.system_model.Outputs.gen) / 1000  # in MW
        self.power_mw = ac[0]  # calculating one timestep at a time
        if self.verbose:
            print("self.power_mw = ", self.power_mw)

        # Apply control, if setpoint is provided
        if "py_sims" in inputs and "solar_setpoint_mw" in inputs["py_sims"]["inputs"]:
            P_setpoint = inputs["py_sims"]["inputs"]["solar_setpoint_mw"]
        elif "external_signals" in inputs.keys():
            if "solar_power_reference_mw" in inputs["external_signals"].keys():
                P_setpoint = inputs["external_signals"]["solar_power_reference_mw"]
            else:
                P_setpoint = None
        else:
            P_setpoint = None
        self.control(P_setpoint)

        if self.power_mw < 0.0:
            self.power_mw = 0.0
        # NOTE: need to talk about whether to have time step in here or not

        self.dni = self.system_model.Outputs.dn[0]  # direct normal irradiance
        self.dhi = self.system_model.Outputs.df[0]  # diffuse horizontal irradiance
        self.ghi = self.system_model.Outputs.gh[0]  # global horizontal irradiance
        if self.verbose:
            print("self.dni = ", self.dni)

        self.aoi = self.system_model.Outputs.aoi[0]  # angle of incidence

        return self.return_outputs()

    def create_col_dict(self, data):
        col_dict = {}
        for i, col in enumerate(data.columns):
            if 'Global Horizontal Irradiance' in col:
                col_dict['ghi_col'] = data.columns.get_loc(col) + 1 # bc 1st col will be timestamp
            elif 'Direct Normal Irradiance' in col:
                col_dict['dni_col'] = data.columns.get_loc(col) + 1 # bc 1st col will be timestamp
            elif 'Diffuse Horizontal Irradiance' in col:
                col_dict['dhi_col'] = data.columns.get_loc(col) + 1 # bc 1st col will be timestamp
            elif 'Temperature' in col:
                col_dict['temp_col'] = data.columns.get_loc(col) + 1 # bc 1st col will be timestamp
            elif 'Wind Speed at 19' in col:
                col_dict['ws_col'] = data.columns.get_loc(col) + 1 # bc 1st col will be timestamp

        self.col_dict = col_dict