# Implements the long run wind model for Hercules
import numpy as np
import pandas as pd
from floris import FlorisModel
from hercules.utilities import load_yaml
from scipy.interpolate import interp1d

# Note time in this non-helics framework will take some thinking but thinking that it will be something like this:
# 1. The weather data will provide Timestamps per row with some actual date time
# 2. Solar data should be similar
# 3. Market data should be similar
# 4. The starttime and endtime in the hercules input file will be in seconds and relative to the start of the weather data

class WindSimLongTerm:
    def __init__(self, input_dict, dt):
        print("trying to read in verbose flag")
        if "verbose" in input_dict:
            self.verbose = input_dict["verbose"]
            print("read in verbose flag = ", self.verbose)
        else:
            self.verbose = True  # default value

        # Read in the input file names
        self.floris_input_file = input_dict["floris_input_file"]
        self.weather_file_name = input_dict["weather_file_name"]
        self.turbine_file_name = input_dict["turbine_file_name"]

        # Save the time step
        self.dt = dt

        # Define needed inputs as empty dict
        self.needed_inputs = {}

        # Initialize the FLORIS model
        self.fmodel = FlorisModel(self.floris_input_file)

        # Get the layout and number of turbines from FLORIS
        self.layout_x = self.fmodel.layout_x
        self.layout_y = self.fmodel.layout_y
        self.n_turbines = self.fmodel.n_turbines

        # Read in the weather file data
        df_wd_ws = pd.read_csv(self.weather_file_name)

        # Like solar_pysam, make time a datetimeindex
        df_wd_ws["Timestamp"] = pd.DatetimeIndex(pd.to_datetime(df_wd_ws["Timestamp"], format="ISO8601"))
        df_wd_ws = df_wd_ws.set_index("Timestamp")

        # Determine the dt implied by the weather file
        self.dt_wd_ws = df_wd_ws.index[1] - df_wd_ws.index[0]

        # Convert the dt to seconds
        self.dt_wd_ws = self.dt_wd_ws.total_seconds()

        # The time step within the weather file must be an integer multiple of the dt
        if self.dt % self.dt_wd_ws != 0:
            raise ValueError(f"dt ({self.dt}) must be an integer multiple of dt_wd_ws ({self.dt_wd_ws})")
        
        # Determine the start index for wd_ws and the stride
        self.start_idx = int(self.dt / self.dt_wd_ws)
        self.stride = int(self.dt / self.dt_wd_ws)

        # Convert the wind directions and wins speeds to simply numpy matrices
        self.ws_mat = df_wd_ws[[f"ws_{t_idx:03d}" for t_idx in range(self.n_turbines)]].to_numpy()
        self.wd_mat = df_wd_ws[[f"wd_{t_idx:03d}" for t_idx in range(self.n_turbines)]].to_numpy()

        # Remove all columns from self.df_wd_ws, keeping just the index
        # self.df_wd_ws = self.df_wd_ws[[]]

        # Get the initial wind speeds and directions per turbine
        self.initial_wind_speeds = np.zeros(self.n_turbines)
        self.initial_wind_directions = np.zeros(self.n_turbines)
        for t_idx in range(self.n_turbines):
            self.initial_wind_speeds[t_idx] = self.ws_mat[self.start_idx, t_idx]
            self.initial_wind_directions[t_idx] = self.wd_mat[self.start_idx, t_idx]

        # # Get the number of time steps and final time
        # self.n_time_steps = len(self.df_wd_ws)
        # self.final_time = self.n_time_steps * self.dt

        # Get the turbine information
        self.turbine_dict = load_yaml(self.turbine_file_name)
        self.turbine_model_type = self.turbine_dict["turbine_model_type"]

        # Initialize the turbine array
        if self.turbine_model_type == "filter_model":
            self.turbine_array = [TurbineFilterModel(self.turbine_dict, self.dt, self.fmodel, self.initial_wind_speeds[t_idx]) for t_idx in range(self.n_turbines)]

        # Initialze the power array to the initial wind speeds
        self.power_mw = np.array([self.turbine_array[t_idx].prev_power/1000.0 for t_idx in range(self.n_turbines)])

        # Update the user
        print(f"Initialized WindSimLongTerm with {self.n_turbines} turbines")# and {self.n_time_steps} time steps")



    def return_outputs(self):

        return {"power_mw": self.power_mw}
    
    def step(self, inputs):

        # Get the current time step
        sim_time_s = inputs["time"]
        if self.verbose:
            print("sim_time_s = ", sim_time_s)

        # select appropriate row based on current time
        time_index = self.start_idx + int(sim_time_s * self.stride)
        if self.verbose:
            print("time_index = ", time_index)

        #TODO THIS IS MISSING A STEP SHOULD BE SOMETHING MORE LIKE
        # 1) GET FLORIS WS/WD
        # 2) RUN FLORIS AND GET WAKE REDUCTIONS IN WIND SPEED AT EACH TURBINE
        # 3) NOW PASS THAT WAKE REDUCED WIND SPEED TO THE FUNCTION BELOW

        # Update the turbine powers given the input wind speeds and derating
        self.power_mw = np.array([
            self.turbine_array[t_idx].step(
                self.ws_mat[time_index, t_idx],
                derating_kw=inputs["py_sims"]['inputs'][f"derating_kw_{t_idx}"] 
            ) / 1000.0
            for t_idx in range(self.n_turbines)
        ])

        return self.return_outputs()


class TurbineFilterModel:
    def __init__(self, turbine_dict, dt, fmodel, initial_wind_speed):
        # Save the time step
        self.dt = dt

        # Save the turbine dict
        self.turbine_dict = turbine_dict

        # Save the filter time constant
        self.filter_time_constant = turbine_dict['filter_model']["time_constant"]

        # Solve for the filter alpha value given dt and the time constant
        self.alpha = self.dt / (self.dt + self.filter_time_constant)

        # Grab the wind speed power curve from the fmodel and define a simple 1D LUT
        turbine_type = fmodel.core.farm.turbine_definitions[0]
        wind_speeds = turbine_type["power_thrust_table"]["wind_speed"]
        powers = turbine_type["power_thrust_table"]["power"]
        self.power_lut =  interp1d(
            wind_speeds,
            powers,
            fill_value=0.0,
            bounds_error=False,
        )

        # Initialize the previous power to the initial wind speed
        self.prev_power = self.power_lut(initial_wind_speed)
    
    def step(self, wind_speed, derating_kw=0.0):
        
        # Instantaneous power
        instant_power = self.power_lut(wind_speed)

        # Limit the current power to not be greater then derating_kw
        instant_power = min(instant_power, derating_kw)

        # Update the power
        power = self.alpha * instant_power + (1 - self.alpha) * self.prev_power

        # Limit the power to not be greater then derating_kw
        power = min(power, derating_kw)

        # Update the previous power
        self.prev_power = power

        # Return the power
        return power
