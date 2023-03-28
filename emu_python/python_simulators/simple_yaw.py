# Very simple solar farm model  
import numpy as np


class SimpleYaw():
    """
    Simple pass-through of wind direction to set yaw angle.
    """

    def __init__(self, input_dict, dt):

        # Perhaps these should inherit from an abstract class that 
        # requires a certain input structure.

        self.dt = dt # Won't be needed here, but generally good to have
        self.n_turbines = input_dict['num_turbines']
        self.turbines = range(self.n_turbines)
        self.wind_farm_name = input_dict['wind_farm_name']
        
        # Set initial conditions
        self.yaw_angles = [input_dict['initial_conditions']['yaw']]*self.n_turbines

    def return_outputs(self):

        return {'turbine_yaws':self.yaw_angles}

    def step(self, input_dict):
        
        # Commands are simply the current wind directions
        self.yaw_angles = input_dict['turbine_wind_directions']

        return self.return_outputs()