# simple battery dispatch model

import numpy as np


def kJ2kWh(kWh):
    return kWh / 3600


def kWh2kJ(kJ):
    return kJ * 3600


class SimpleBattery:
    # TODO: keep consistent units. Everything in kW or everything in MW but not both
    def __init__(self, input_dict, dt):
        self.dt = dt

        # size = input_dict["size"]
        self.energy_capacity = input_dict["energy_capacity"] * 1e3  # [kWh]

        inititial_conditions = input_dict["initial_conditions"]

        self.SOC = inititial_conditions["SOC"]  # [fraction]

        self.SOC_max = input_dict["max_SOC"]
        self.SOC_min = input_dict["min_SOC"]

        # Charge (Energy) limits [kJ]
        self.E_min = kWh2kJ(self.SOC_min * self.energy_capacity)
        self.E_max = kWh2kJ(self.SOC_max * self.energy_capacity)

        charge_rate = input_dict["charge_rate"] * 1e3  # [kW]
        discharge_rate = input_dict["discharge_rate"] * 1e3  # [kW]

        # Charge/discharge (Power) limits [kW]
        self.P_min = -discharge_rate
        self.P_max = charge_rate

        # Ramp up/down limits [kW/s]
        self.R_min = -np.inf
        self.R_max = np.inf

        # self.total_battery_capacity = 3600 * self.energy_capacity / self.dt
        self.current_batt_state = self.SOC * self.energy_capacity
        self.E = kWh2kJ(self.current_batt_state)

        self.power_mw = 0
        self.P_reject = 0
        self.P_charge = 0

        self.needed_inputs = {}

    def return_outputs(self):
        return {"power": self.power_mw, "reject": self.P_reject, "soc": self.SOC}

    def step(self, inputs):
        P_signal = inputs["setpoints"]["battery"][
            "signal"
        ]  # power available for the battery to use for charging (should be >=0)
        P_avail = inputs["py_sims"]["inputs"][
            "available_power"
        ]  # power signal desired by the controller

        self.control(P_avail, P_signal)

        # Update energy state
        self.E += self.P_charge * self.dt

        self.current_batt_state = kJ2kWh(self.E)

        self.power_mw = self.P_charge
        self.SOC = self.current_batt_state / self.energy_capacity

        return self.return_outputs()

    def control(self, P_avail, P_signal):
        """
        Low-level controller to enforce charging and energy constraints

        InputsL
        - P_avail: [kW] the available power for charging
        - P_signal: [kW] the desired charging power

        This method calculates
        - P_charge: [kW] (positive of negative) the charging/discharging power
        - P_reject: [kW] (positive or negative) either the extra power that the battery cannot absorb (positive) or the power required but not provided for the battery to charge/discharge without violating constraints (negative)
        """

        # TODO battery state in SI units like J, kJ, or MJ
        # self.E = kWh2kJ(self.current_batt_state)  # * self.dt / 3600 * 1e3
        # self.E = self.current_batt_state

        # Upper constraints [kW]
        c_hi1 = (self.E_max - self.E) / self.dt  # energy
        c_hi2 = self.P_max  # power
        c_hi3 = self.R_max * self.dt + self.P_charge  # ramp rate

        # Lower constraints [kW]
        c_lo1 = (self.E_min - self.E) / self.dt  # energy
        c_lo2 = self.P_min  # power
        c_lo3 = self.R_min * self.dt + self.P_charge  # ramp rate

        # High constraint is the most restrictive of the high constraints
        c_hi = np.min([c_hi1, c_hi2, c_hi3, P_avail])

        # Low constraint is the most restrictive of the low constraints
        c_lo = np.max([c_lo1, c_lo2, c_lo3])
        # TODO: force low constraint to be no higher than lowest high constraint

        if (P_signal >= c_lo) & (P_signal <= c_hi):
            self.P_charge = P_signal
            self.P_reject = 0
        elif P_signal < c_lo:
            self.P_charge = c_lo
            # self.P_reject = P_avail - self.P_charge
            self.P_reject = P_signal - self.P_charge
        elif P_signal > c_hi:
            self.P_charge = c_hi
            # self.P_reject = P_avail - self.P_charge
            self.P_reject = P_signal - self.P_charge


# class SimpleBattery:
#     # def __init__(self, size, charge_rate, discharge_rate):
#     def __init__(self, input_dict, dt):
#         # properties of the storage
#         self.dt = dt
#         self.size = input_dict["size"]
#         self.energy_capacity = input_dict["energy_capacity"]
#         self.charge_rate = input_dict[
#             "charge_rate"
#         ]  # MW/hr  -> need these for dynamics
#         self.discharge_rate = input_dict["discharge_rate"]  # MW
#         self.SOC = input_dict["initial_conditions"]["SOC"]

#         self.max_SOC = input_dict["max_SOC"]
#         self.min_SOC = input_dict["min_SOC"]

#         self.total_battery_capacity = 3600 * self.energy_capacity / self.dt
#         self.current_batt_state = self.SOC * self.total_battery_capacity
#         self.max_capacity = self.max_SOC * self.total_battery_capacity
#         self.min_capacity = self.min_SOC * self.total_battery_capacity

#         # Define needed inputs as empty dict
#         self.needed_inputs = {}

#         self.power_mw = 0
#         print("battery", self.size, self.charge_rate, self.discharge_rate)

#         # initialize storage
#         # self.SOC = np.random.rand(1) * self.size
#         # self.SOC = 0.5 * self.size

#     def return_outputs(self):
#         return {"power": self.power_mw, "soc": self.SOC}

#     def step(self, inputs):
#         # storage module

#         ## Note: signal, available_power, charge_rate, and discharge_rate need to have consistent units ##
#         ####### Currently in MW ###########
#         # Decides based on total power available and signal what to do
#         """Battery step function
#         Necessary inputs:
#             signal: power signal asked of the total plant
#             available power: total available power from the plant

#         Returns:
#             power_mw: power output, positive or negative, from the battery (discharging or charging)
#             soc: current state of charge of the battery
#         """
#         signal = inputs["controller"]["signal"]
#         available_power = inputs["py_sims"]["inputs"]["available_power"]

#         diff = available_power - signal

#         amount_charged = 0.0
#         if signal > 0:
#             if diff > 0:
#                 # charge
#                 if self.current_batt_state == self.max_capacity:
#                     amount_charged = 0
#                 else:
#                     diff_value = np.min([self.charge_rate, diff])
#                     amount_charged = np.min(
#                         [
#                             self.charge_rate,
#                             diff_value,
#                             self.max_capacity - self.current_batt_state,
#                         ]
#                     )
#                     self.current_batt_state = np.min(
#                         self.current_batt_state + amount_charged, self.max_capacity
#                     )

#             elif diff < 0:
#                 # discharge
#                 if self.SOC == 0:
#                     amount_charged = 0
#                 else:
#                     diff_value = np.min([self.discharge_rate, np.abs(diff)])
#                     amount_charged = -np.min(
#                         [self.discharge_rate, diff_value, self.current_batt_state]
#                     )
#                     self.current_batt_state = np.min(
#                         self.current_batt_state + amount_charged, self.min_capacity
#                     )

#         self.SOC = self.current_batt_state / self.total_battery_capacity
#         self.power_mw = -amount_charged
#         power_left = available_power - amount_charged
#         signal_left = signal + amount_charged

#         return self.return_outputs()
