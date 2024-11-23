# Very simple solar farm model


class SimpleSolar:
    def __init__(self, input_dict, dt):
        # Need dt, plant capacity and efficiency
        # Using base value of 1000 W/m^2 irradiance for sizing

        # Efficiency currently denotes the kind of solar panel you have
        self.efficiency = input_dict["efficiency"]  # need a realistic efficiency for a solar panel
        self.capacity = input_dict["capacity"]

        # Total area of solar panels
        base_irradiance = 1000  # W/m^2
        self.area = self.capacity * 1e3 / (self.efficiency * base_irradiance)  # in m^2

        # Fixed dt for solar simulations
        self.dt = dt

        # Save the initial condition
        self.power_kw = input_dict["initial_conditions"]["power"]
        self.irradiance = input_dict["initial_conditions"]["irradiance"]

        # Define needed inputs as empty dict
        self.needed_inputs = {}

        # # compute power output of solar panels
        # self.compute_power()

    def return_outputs(self):
        return {"power_kw": self.power_kw,
                 "dni": self.irradiance,
                 "aoi": None,
                 }

    def step(self, inputs):
        # TODO add tilt tracking - haven't gotten to this yet
        # right now, just static
        # https://www.sciencedirect.com/science/article/pii/S1364032106001134

        # Note: irradiance is measured in W/m^2, so the power is calculated in Watts,
        #           and then scaled to kW

        # Assume model generates its own irradiance
        if inputs:
            sim_time_s = inputs["time"]
            irradiance = inputs["irradiance"]
        else:
            irradiance = 1000.0


        # Save this as an output for now
        self.irradiance = irradiance

        # Gather inputs
        # irradiance = inputs['irradiance']

        self.power_kw = irradiance * self.area * self.efficiency / 1e3 * self.dt
        if self.power_kw < 0.0:
            self.power_kw = 0.0
        # NOTE: need to talk about whether to have time step in here or not
        # Need to put outputs into input/output structure

        return self.return_outputs()
