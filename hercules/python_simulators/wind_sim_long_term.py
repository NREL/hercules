# Implements the long run wind model for Hercules.

import numpy as np
import pandas as pd
from floris import FlorisModel
from hercules.utilities import load_perffile, load_yaml
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
from scipy.stats import circmean

# Note time in this non-helics framework will take some thinking but thinking 
# that it will be something like this:
# 1. The wind input data will provide Timestamps per row with some actual date time
# 2. Solar data should be similar
# 3. Market data should be similar
# 4. The starttime and endtime in the hercules input file will be in seconds
#    and relative to the start of the wind input data

RPM2RADperSec = 2 * np.pi / 60.0

class WindSimLongTerm:
    def __init__(self, input_dict, dt):
        print("trying to read in verbose flag")
        if "verbose" in input_dict:
            self.verbose = input_dict["verbose"]
            print("read in verbose flag = ", self.verbose)
        else:
            self.verbose = True  # default value

        # Define needed inputs as empty dict
        self.needed_inputs = {}

        # Save the time step for Hercules
        self.dt = dt

        # Track the number of FLORIS calculation
        self.num_floris_calcs = 0

        # Get the start time
        # TODO: NEED TO ACTUALLY FIGURE OUT HOW TO DO THIS
        self.start_time_s = 0  # input_dict["sim_time_s"]

        # Get the start index
        self.start_idx = int(self.start_time_s / self.dt)

        # Read in the input file names
        self.floris_input_file = input_dict["floris_input_file"]
        self.wind_input_filename = input_dict["wind_input_filename"]
        self.turbine_file_name = input_dict["turbine_file_name"]

        # Read in the weather file data
        # If a csv file is provided, read it in
        if self.wind_input_filename.endswith(".csv"):
            df_wi = pd.read_csv(self.wind_input_filename)
        elif self.wind_input_filename.endswith(".p"):
            df_wi = pd.read_pickle(self.wind_input_filename)
        else:
            raise ValueError("Wind input file must be a .csv or .p file")

        # Like solar_pysam, make time a datetimeindex
        df_wi["Timestamp"] = pd.DatetimeIndex(pd.to_datetime(df_wi["Timestamp"], format="ISO8601"))
        df_wi = df_wi.set_index("Timestamp")

        # Determine the dt implied by the weather file
        self.dt_wi = df_wi.index[1] - df_wi.index[0]

        # Convert the dt to seconds
        self.dt_wi = self.dt_wi.total_seconds()

        # The time step within the weather file must be an integer multiple of the dt
        if self.dt % self.dt_wi != 0:
            raise ValueError(f"dt ({self.dt}) must be an integer multiple of dt_wi ({self.dt_wi})")

        # If dt_wi is less than dt, then resample df_wi so that its time steps are equal to dt
        if self.dt_wi < self.dt:
            num_steps_initial = df_wi.shape[0]
            df_wi = df_wi.iloc[:: int(self.dt / self.dt_wi)]
            if self.verbose:
                print(f"Resampled df_wi from {num_steps_initial} to {df_wi.shape[0]} rows")

        # FLORIS PREPARATION

        # Initialize the FLORIS model
        self.fmodel = FlorisModel(self.floris_input_file)

        # Change to the simple-derating model turbine
        # (Note this could also be done with the mixed model)
        self.fmodel.set_operation_model("simple-derating")

        # Get the layout and number of turbines from FLORIS
        self.layout_x = self.fmodel.layout_x
        self.layout_y = self.fmodel.layout_y
        self.n_turbines = self.fmodel.n_turbines

        # TODO Switch this to an input
        self.floris_wd_threshold = 1.0
        self.floris_ws_threshold = 0.5
        self.floris_ti_threshold = 0.01
        self.floris_derating_threshold = 10  # kW

        # TODO Make this settable in the future
        # TODO make this in seconds and convert to array indices internally
        # Establish the width of the FLORIS averaging window
        self.floris_time_window_width_s = 30
        self.floris_time_window_width = int(self.floris_time_window_width_s / self.dt)

        # How often to update the wake deficits
        self.floris_update_time_s = 10
        self.floris_update_time = int(self.floris_update_time_s / self.dt)

        # Declare the derating buffer to hold previous derating commands
        self.derating_buffer = np.zeros((self.floris_time_window_width, self.n_turbines)) * np.nan
        self.derating_buffer_idx = 0  # Initialize the index to 0

        # Add an initial non-nan value to be over-written on first step
        self.derating_buffer[0, :] = 1e12

        # Convert the wind directions and wind speeds and ti to simply numpy matrices
        self.wd_mat = df_wi[[f"wd_{t_idx:03d}" for t_idx in range(self.n_turbines)]].to_numpy()
        self.ws_mat = df_wi[[f"ws_{t_idx:03d}" for t_idx in range(self.n_turbines)]].to_numpy()
        self.ti_mat = df_wi[[f"ti_{t_idx:03d}" for t_idx in range(self.n_turbines)]].to_numpy()

        # Compute the turbine-averaged wind directions (axis = 1) using circmean
        self.wd_mat_mean = np.apply_along_axis(
            lambda x: circmean(x, high=360.0, low=0.0, nan_policy="omit"), axis=1, arr=self.wd_mat
        )

        # Compute the turbine averaged wind speeds (axis = 1) using mean
        self.ws_mat_mean = np.mean(self.ws_mat, axis=1)

        # Compute the turbine averaged turbulence intensities (axis = 1) using mean
        self.ti_mat_mean = np.mean(self.ti_mat, axis=1)

        # Get the initial wind speeds and directions per turbine
        self.initial_wind_directions = self.wd_mat[self.start_idx, :]
        self.initial_wind_speeds = self.ws_mat[self.start_idx, :]
        self.initial_tis = self.ti_mat[self.start_idx, :]

        # Compute the initial floris wind direction and wind speed as at the start index
        self.floris_wind_direction = self.wd_mat_mean[self.start_idx]
        self.floris_wind_speed = self.ws_mat_mean[self.start_idx]
        self.floris_ti = self.ti_mat_mean[self.start_idx]
        self.floris_derating = np.nanmean(self.derating_buffer, axis=0)

        # Iniialize the wake deficits
        self.floris_wake_deficits = np.zeros(self.n_turbines)

        # Get the initial unwaked velocities
        # TODO: This is more a debugging thing, not really necessary
        self.unwaked_velocities = self.ws_mat[self.start_idx, :]

        # # Compute the initial waked velocities
        self.update_wake_deficits(self.start_idx)

        # Compute waked velocities
        self.waked_velocities = self.ws_mat[self.start_idx, :] - self.floris_wake_deficits

        # Get the turbine information
        self.turbine_dict = load_yaml(self.turbine_file_name)
        self.turbine_model_type = self.turbine_dict["turbine_model_type"]

        # Initialize the turbine array
        if self.turbine_model_type == "filter_model":
            self.turbine_array = [
                TurbineFilterModel(
                    self.turbine_dict, self.dt, self.fmodel, self.waked_velocities[t_idx]
                )
                for t_idx in range(self.n_turbines)
            ]
        elif self.turbine_model_type == "dof1_model":
            self.turbine_array = [
                Turbine1dofModel(
                    self.turbine_dict, self.dt, self.fmodel, self.waked_velocities[t_idx]
                )
                for t_idx in range(self.n_turbines)
            ]
        else:
            raise Exception('Turbine model type should be either fileter_model or dof1_model')

        # Initialize the power array to the initial wind speeds
        self.power = np.array(
            [self.turbine_array[t_idx].prev_power for t_idx in range(self.n_turbines)]
        )

        # Update the user
        print(f"Initialized WindSimLongTerm with {self.n_turbines} turbines")

    def update_wake_deficits(self, time_idx):
        # Get the window start
        window_start = max(0, time_idx - self.floris_time_window_width)

        # Compute new values of the floris inputs
        # TODO: CONFIRM THE +1 in the slice is right
        floris_wind_direction = circmean(
            self.wd_mat_mean[window_start : time_idx + 1], high=360.0, low=0.0, nan_policy="omit"
        )
        floris_wind_speed = np.mean(self.ws_mat_mean[window_start : time_idx + 1])
        floris_ti = np.mean(self.ti_mat_mean[window_start : time_idx + 1])

        # Compute the deratings over the same window
        floris_derating = np.nanmean(self.derating_buffer, axis=0)

        # Reshape derating to be 2D with number on axis 1
        floris_derating = floris_derating.reshape(1, -1)

        # If any of the FLORIS inputs have sufficienty changed, update wake deficits
        if (
            np.abs(floris_wind_direction - self.floris_wind_direction) > self.floris_wd_threshold
            or np.abs(floris_wind_speed - self.floris_wind_speed) > self.floris_ws_threshold
            or np.abs(floris_ti - self.floris_ti) > self.floris_ti_threshold
            or np.any(
                np.abs(floris_derating - self.floris_derating) > self.floris_derating_threshold
            )
        ):
            # If verbose
            if self.verbose:
                print("...Updating FLORIS model==========================================")

            # Update the FLORIS inputs
            self.floris_wind_direction = floris_wind_direction
            self.floris_wind_speed = floris_wind_speed
            self.floris_ti = floris_ti
            self.floris_derating = floris_derating

            # Update the FLORIS model
            self.fmodel.set(
                wind_directions=[self.floris_wind_direction],
                wind_speeds=[self.floris_wind_speed],
                turbulence_intensities=[self.floris_ti],
                power_setpoints=1000 * self.floris_derating,
            )
            self.fmodel.run()

            # Compute the deficits
            velocities = self.fmodel.turbine_average_velocities.flatten()
            self.floris_wake_deficits = velocities.max() - velocities

            # Update the number of FLORIS calculations
            self.num_floris_calcs += 1

            if self.verbose:
                print(f"Num of FLORIS calculations = {self.num_floris_calcs}")

    def update_derating_buffer(self, derating):
        # Update the derating buffer
        self.derating_buffer[self.derating_buffer_idx, :] = derating

        # Increment the index
        self.derating_buffer_idx = (self.derating_buffer_idx + 1) % self.floris_time_window_width

    def return_outputs(self):
        return {
            "power": self.power,
            "unwaked_velocity": self.unwaked_velocities,
            "waked_velocity": self.waked_velocities,
            "floris_wind_speed": self.floris_wind_speed,
            "floris_wind_direction": self.floris_wind_direction,
        }

    def step(self, inputs):
        # Get the current time step
        sim_time_s = inputs["time"]
        if self.verbose:
            print("sim_time_s = ", sim_time_s)

        # select appropriate row based on current time
        time_index = int(sim_time_s / self.dt)
        if self.verbose:
            print("time_index = ", time_index)

        # Grab the instantaneous derating signal and update the derating buffer
        derating = np.array(
            [
                inputs["py_sims"]["inputs"][f"derating_{t_idx:03d}"]
                for t_idx in range(self.n_turbines)
            ]
        )
        self.update_derating_buffer(derating)

        # Get the unwaked velocities
        # TODO: This is more a debugging thing, not really necessary
        self.unwaked_velocities = self.ws_mat[time_index, :]

        # Check if it is time to update the waked velocities
        if time_index % self.floris_update_time == 0:
            if self.verbose:
                print(".check for floris update...")
            self.update_wake_deficits(time_index)

        # Compute waked velocities
        self.waked_velocities = self.ws_mat[time_index, :] - self.floris_wake_deficits

        # Update the turbine powers given the input wind speeds and derating
        self.power = np.array(
            [
                self.turbine_array[t_idx].step(
                    self.waked_velocities[t_idx],
                    derating=derating[t_idx],
                )
                for t_idx in range(self.n_turbines)
            ]
        )

        return self.return_outputs()


class TurbineFilterModel:
    def __init__(self, turbine_dict, dt, fmodel, initial_wind_speed):
        # Save the time step
        self.dt = dt

        # Save the turbine dict
        self.turbine_dict = turbine_dict

        # Save the filter time constant
        self.filter_time_constant = turbine_dict["filter_model"]["time_constant"]

        # Solve for the filter alpha value given dt and the time constant
        self.alpha = self.dt / (self.dt + self.filter_time_constant)

        # Grab the wind speed power curve from the fmodel and define a simple 1D LUT
        turbine_type = fmodel.core.farm.turbine_definitions[0]
        wind_speeds = turbine_type["power_thrust_table"]["wind_speed"]
        powers = turbine_type["power_thrust_table"]["power"]
        self.power_lut = interp1d(
            wind_speeds,
            powers,
            fill_value=0.0,
            bounds_error=False,
        )

        # Initialize the previous power to the initial wind speed
        self.prev_power = self.power_lut(initial_wind_speed)

    def step(self, wind_speed, derating=0.0):
        # Instantaneous power
        instant_power = self.power_lut(wind_speed)

        # Limit the current power to not be greater then derating
        instant_power = min(instant_power, derating)

        # Update the power
        power = self.alpha * instant_power + (1 - self.alpha) * self.prev_power

        # Limit the power to not be greater then derating
        power = min(power, derating)

        # Update the previous power
        self.prev_power = power

        # Return the power
        return power

class Turbine1dofModel:
    def __init__(self, turbine_dict, dt, fmodel, initial_wind_speed):
        # Save the time step
        self.dt = dt

        # Save the turbine dict
        self.turbine_dict = turbine_dict

        # Obtain more data from floris
        turbine_type = fmodel.core.farm.turbine_definitions[0]
        self.rotor_radius = turbine_type['rotor_diameter']/2
        self.rotor_area = np.pi*self.rotor_radius**2
        

        # Save performance data functions
        perffile = turbine_dict['dof1_model']['cq_table_file']
        self.perffuncs = load_perffile(perffile)

        self.rho = self.turbine_dict['dof1_model']['rho']
        self.max_pitch_rate = self.turbine_dict['dof1_model']['max_pitch_rate']
        self.max_torque_rate = self.turbine_dict['dof1_model']['max_torque_rate']
        omega0 = self.turbine_dict['dof1_model']['initial_rpm']*RPM2RADperSec
        pitch,gentq = self.simplecontroller(initial_wind_speed,omega0)
        tsr = self.rotor_radius*omega0/initial_wind_speed
        prev_power = (
            self.perffuncs["Cp"]([tsr, pitch])
            * 0.5
            * self.rho
            * self.rotor_area
            * initial_wind_speed**3
        )
        self.prev_power = np.array(prev_power[0]/1000.0)
        self.prev_omega = omega0
        self.prev_aerotq = (
            0.5
            * self.rho
            * self.rotor_area
            * self.rotor_radius
            * initial_wind_speed**2
            * self.perffuncs["Cq"]([tsr, pitch])
        )
        self.prev_gentq = gentq
        self.prev_pitch = pitch
        
        pass
        
    def step(self, wind_speed, derating=0.0):
        omega = (
            self.prev_omega
            + (
                self.prev_aerotq
                - self.prev_gentq * self.turbine_dict["dof1_model"]["gearbox_ratio"]
            )
            * self.dt
            / self.turbine_dict["dof1_model"]["rotor_inertia"]
        )
        pitch,gentq = self.simplecontroller(wind_speed,omega)
        tsr = float(omega * self.rotor_radius / wind_speed)
        if derating > 0:
            desiredcp = derating*1000 / ( 0.5 * self.rho * self.rotor_area * wind_speed**3)
            optpitch = minimize_scalar(
                lambda p: abs(float(self.perffuncs["Cp"]([tsr, float(p)])) - desiredcp),
                method='bounded',
                bounds=(0,1.57)
            )
            pitch = optpitch.x

        pitch = np.clip(
            pitch,
            self.prev_pitch - self.max_pitch_rate * self.dt,
            self.prev_pitch + self.max_pitch_rate * self.dt,
        )
        gentq = np.clip(
            gentq,
            self.prev_gentq - self.max_torque_rate * self.dt,
            self.prev_gentq + self.max_torque_rate * self.dt,
        )

        aerotq = (
            0.5
            * self.rho
            * self.rotor_area
            * self.rotor_radius
            * wind_speed ** 2
            * self.perffuncs["Cq"]([tsr, pitch])
        )

        power = (
            self.perffuncs["Cp"]([tsr, pitch]) * 0.5 * self.rho * self.rotor_area * wind_speed**3
        )

        self.prev_omega = omega
        self.prev_aerotq = aerotq
        self.prev_gentq = gentq
        self.prev_pitch = pitch
        self.prev_power = power[0] / 1000.0
        
        return self.prev_power

    def simplecontroller(self,wind_speed,omega):
        # if omega <= self.turbine_dict['dof1_model']['rated_wind_speed']:
        pitch = 0.0
        gentorque = self.turbine_dict['dof1_model']['controller']['r2_k_torque'] * omega**2
        # else
        #     raise Exception("Region-3 controller not implemented yet")
        return pitch,gentorque