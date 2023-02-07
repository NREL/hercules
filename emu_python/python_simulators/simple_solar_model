# Very simple solar farm model  
import numpy as np


class SimpleSolar():

    def __init__(self, input_dict, dt):

        # Need dt, plant capacity and efficiency
        # Using base value of 1000 W/m^2 irradiance for sizing

        # Efficiency currently denotes the kind of solar panel you have
        self.efficiency = input_dict['efficiency']  # need a realistic efficiency for a solar panel
        self.capacity = input_dict['capacity']

        # Total area of solar panels
        base_irradiance = 1000  # W/m^2
        self.area = self.capacity / (self.efficiency * base_irradiance)  # in m^2

        # Fixed dt for solar simulations
        self.dt = dt

        # # compute power output of solar panels
        # self.compute_power()


    def compute_power(self, irradiance):

        # TODO add tilt tracking - haven't gotten to this yet
        # right now, just static
        # https://www.sciencedirect.com/science/article/pii/S1364032106001134

        # Note: irradiance is measured in W/m^2, so the power is calculated in Watts, and then scaled to MW
        self.power_mw = 0.0

        self.power_mw = irradiance * self.area * self.efficiency / 1e6 * self.dt
        if self.power_mw < 0.0:
            self.power_mw = 0.0
        # NOTE: need to talk about whether to have time step in here or not
        # Need to put outputs into input/output structure
