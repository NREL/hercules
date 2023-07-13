# simple battery dispatch model

import numpy as np

class SimpleBattery():

    # def __init__(self, size, charge_rate, discharge_rate):
    def __init__(self, input_dict, dt):

        # properties of the storage
        self.dt = dt
        self.size = input_dict['size']
        self.energy_capacity = input_dict['energy_capacity']
        self.charge_rate = input_dict['charge_rate'] # MW/hr  -> need these for dynamics
        self.discharge_rate = input_dict['discharge_rate'] # MW
        self.SOC = input_dict['initial_conditions']['SOC']

        self.max_SOC = input_dict['max_SOC']
        self.min_SOC = input_dict['min_SOC']

        self.total_battery_capacity = 3600 * self.energy_capacity / self.dt
        self.current_batt_state = self.SOC * self.total_battery_capacity
        self.max_capacity = self.max_SOC*self.total_battery_capacity
        self.min_capacity = self.min_SOC*self.total_battery_capacity

        # Define needed inputs as empty dict
        self.needed_inputs = {}

        self.power_mw = 0
        print('battery', self.size, self.charge_rate, self.discharge_rate)

        # initialize storage
        # self.SOC = np.random.rand(1) * self.size
        # self.SOC = 0.5 * self.size

    def return_outputs(self):

        return {'power': self.power_mw,
                'soc': self.SOC
        }

    def step(self, inputs):

        # storage module

        ## Note: signal, available_power, charge_rate, and discharge_rate need to have consistent units ##
        ####### Currently in MW ###########
        # Decides based on total power available and signal what to do 
        """ Battery step function
        Necessary inputs: 
            signal: power signal asked of the total plant
            available power: total available power from the plant

        Returns:
            power_mw: power output, positive or negative, from the battery (discharging or charging)
            soc: current state of charge of the battery
        """
        signal = inputs['signal']
        available_power = inputs['available_power']

        diff = available_power  - signal

        amount_charged = 0.0
        if signal > 0:
            if diff > 0:
                # charge
                if self.current_batt_state == self.max_capacity:
                    amount_charged = 0
                else:
                    diff_value = np.min([self.charge_rate, diff])
                    amount_charged = np.min([self.charge_rate, diff_value, self.max_capacity-self.current_batt_state])
                    self.current_batt_state = np.min(self.current_batt_state+amount_charged, self.max_capacity)

            elif diff < 0:
                # discharge
                if self.SOC == 0:
                    amount_charged = 0
                else:
                    diff_value = np.min([self.discharge_rate, np.abs(diff)])
                    amount_charged = -np.min([self.discharge_rate, diff_value, self.current_batt_state])
                    self.current_batt_state = np.min(self.current_batt_state+amount_charged, self.min_capacity)

        self.SOC = self.current_batt_state / self.total_battery_capacity
        self.power_mw = -amount_charged
        power_left = available_power - amount_charged
        signal_left = signal + amount_charged     

        return self.return_outputs()

 
