"""
Simple battery dispatch model
Author: Zack tully - zachary.tully@nrel.gov

References:
[1] M.-K. Tran et al., “A comprehensive equivalent circuit model for lithium-ion 
batteries, incorporating the effects of state of health, state of charge, and 
temperature on model parameters,” Journal of Energy Storage, vol. 43, p. 103252, 
Nov. 2021, doi: 10.1016/j.est.2021.103252.


TODO: docstrings
"""

import numpy as np


def kJ2kWh(kWh):
    """Convert a value in kWh to kJ"""
    return kWh / 3600


def kWh2kJ(kJ):
    """Convert a value in kJ to kWh"""
    return kJ * 3600


# From Fig. 4
OCV_data = np.genfromtxt(
    "/Users/ztully/Documents/battery_model/batterymodel/batterymodel/Tran2021/OCV_SOC_Tran2021.csv",
    delimiter=",",
)

# Table 2
R0_b = np.array([10424.73, -48.2181, -114.74, -1.40433])  # micro ohms
R1_b = np.array([13615.54, -68.0889, -87.527, -37.1084])  # micro ohms
C1_b = np.array([-11116.7, 180.4576, 237.4219, 40.14711])  # F

# Table 1
V_nom = 3.3
C_all5 = np.array([18.40, 15.70, 13.00, 14.58, 17.10])  # Ah
cap = np.mean(C_all5)
# Cathode Material LiFePO4 (all 5 cells)
# Anode Material Graphite (all 5 cells)


def emp_fit(params, SOH, T, SOC):
    return params[0] + params[1] * SOH + params[2] * T + params[3] * SOC

def R0(SOH, T, SOC):
    return emp_fit(R0_b, SOH, T, SOC) * 1e-6  # ohms


def R1(SOH, T, SOC):
    return emp_fit(R1_b, SOH, T, SOC) * 1e-6  # ohms


def C1(SOH, T, SOC):
    return emp_fit(C1_b, SOH, T, SOC)

# TODO: test full range of SOC
def OCV(SOC):
    return np.interp(SOC, OCV_data[:, 0], OCV_data[:, 1])


def build_SS(SOC, T, SOH):
    R_0 = R0(SOH * 100, T, SOC * 100)
    R_1 = R1(SOH * 100, T, SOC * 100)
    C_1 = C1(SOH * 100, T, SOC * 100)

    A = -1 / (R_1 * C_1)
    B = 1
    C = 1 / C_1
    D = R_0

    return A, B, C, D


class LIB:
# class SimpleBattery:
    def __init__(self, input_dict, dt):

        # From Tran et al. 2021
        self.V_cell_nom = 3.3  # [V]
        self.C_cell = 15.756  # [Ah] mean value from Table 1
        # self.max_C_rate = 1 # [capacity / hr] C-rate = 1 means the cell discharges fully in one hour

        self.dt = dt

        self.energy_capacity = input_dict["energy_capacity"] * 1e3  # [kWh]
        self.n_cells = self.energy_capacity * 1e3 / (self.V_cell_nom * self.C_cell)

        # TODO: need a systematic way to decide parallel and series cells
        # TODO: choose a default voltage to choose the series and parallel configuration.
        self.n_p = np.sqrt(self.n_cells)  # number of cells in parallel
        self.n_s = np.sqrt(self.n_cells)  # number of cells in series

        self.C = self.C_cell * self.n_cells  # [Ah] capacity

        max_charge_power = input_dict["charge_rate"] * 1e3  # [kW]
        max_discharge_power = input_dict["discharge_rate"] * 1e3  # [kW]

        C_rate_charge = max_charge_power / self.energy_capacity
        C_rate_discharge = max_discharge_power / self.energy_capacity

        self.max_C_rate = np.max(
            [C_rate_charge, C_rate_discharge]
        )  # [A] [capacity / hr] C-rate = 1 means the cell discharges fully in one hour

        self.V_bat_nom = self.V_cell_nom * self.n_s
        self.I_bat_max = self.C_cell * self.max_C_rate * self.n_p

        self.P_max = self.C * self.max_C_rate * self.V_cell_nom * 1e-3
        self.P_min = -self.P_max

        inititial_conditions = input_dict["initial_conditions"]
        self.SOC = inititial_conditions["SOC"]  # [fraction]
        self.charge = self.SOC * self.C  # [Ah]

        self.SOC_max = input_dict["max_SOC"]
        self.SOC_min = input_dict["min_SOC"]

        self.charge_max = self.SOC_max * self.C
        self.charge_min = self.SOC_min * self.C

        self.power_mw = 0
        self.P_reject = 0
        self.P_charge = 0

        self.T = 25  # C temperature
        self.SOH = 1  # State of Health

        # TODO: initial state of RC branch
        self.x = 0
        self.V_RC = 0

    def step(self, inputs):
        P_signal = inputs["setpoints"]["battery"][
            "signal"
        ]  # power available for the battery to use for charging (should be >=0)
        P_avail = inputs["py_sims"]["inputs"][
            "available_power"
        ]  # power signal desired by the controller

        I_signal = P_signal * 1e3 / self.V_bat_nom
        I_avail = P_avail * 1e3 / self.V_bat_nom

        I_charge, I_reject = self.control(I_avail, I_signal)
        i_charge = I_charge / self.n_p

        # Charge at some current with and nominal voltage to consume a desired power

        self.charge += I_charge * self.dt
        self.SOC = self.charge / self.C

        self.step_cell(i_charge)

        self.power_mw = self.calc_power(I_charge) * 1e-3
        self.P_reject = P_signal - self.power_mw

        return self.return_outputs()

    def step_cell(self, i):
        # TODO: What if dt is very slow? skip this integration

        # update the state of the cell model
        A, B, C, D = build_SS(self.SOC, self.T, self.SOH)

        u = i
        xd = A * self.x + B * u
        y = C * self.x + D * u

        self.x = self.integrate(self.x, xd)

        self.V_RC = y

    # def step_cell(self, i):

    #     R_0 = R0(self.SOH * 100, self.T, self.SOC * 100)
    #     R_1 = R1(self.SOH * 100, self.T, self.SOC * 100)
    #     C_1 = C1(self.SOH * 100, self.T, self.SOC * 100)

    #     self.V_RC = (
    #         R_0 * i
    #         + np.exp(-self.dt / (R_1 * C_1)) * self.V_RC
    #         + R_1 * (1 - np.exp(-self.dt / (R_1 * C_1))) * i
    #     )

    def integrate(self, x, xd):
        # better integration -> use the closed form step response solution?
        return x + xd * self.dt  # Euler integration

    def V_cell(self, i):
        V = OCV(self.SOC) + self.V_RC
        return V

    def calc_power(self, I_bat):
        # return power in kW
        i_cell = I_bat / self.n_p
        return self.V_cell(i_cell) * self.n_s * I_bat

    def return_outputs(self):
        return {"power": self.power_mw, "reject": self.P_reject, "soc": self.SOC}

    def control(self, I_avail, I_signal):

        # Amperage constraints

        # energy constraint, upper. Charging amperage that would fill the battery up completely
        c_hi1 = (self.charge_max - self.charge) / self.dt
        # charge rate constraint, upper
        c_hi2 = self.I_bat_max
        # available power
        c_hi3 = I_avail

        # energy constraint, lower
        c_lo1 = (self.charge_min - self.charge) / self.dt
        # discharge rate constraint, lower
        c_lo2 = -self.I_bat_max

        c_hi = np.min([c_hi1, c_hi2, c_hi3])
        c_lo = np.max([c_lo1, c_lo2])

        if (I_signal >= c_lo) & (I_signal <= c_hi):
            # It is possible to fulfill the requested signal
            I_charge = I_signal
            I_reject = 0
        elif I_signal < c_lo:
            # The battery is constrained to charge/discharge higher than the requested signal
            I_charge = c_lo
            I_reject = I_signal - I_charge
        elif I_signal > c_hi:
            # The battery is constrained to charge/discharge lower than the requested signal
            I_charge = c_hi
            I_reject = I_signal - I_charge

        return I_charge, I_reject

    def estimate_energy(self):
        pass


# class SimpleBattery:
#     # TODO: keep consistent units. Everything in kW or everything in MW but not both
#     def __init__(self, input_dict, dt):
#         self.dt = dt

#         # size = input_dict["size"]
#         self.energy_capacity = input_dict["energy_capacity"] * 1e3  # [kWh]

#         inititial_conditions = input_dict["initial_conditions"]

#         self.SOC = inititial_conditions["SOC"]  # [fraction]

#         self.SOC_max = input_dict["max_SOC"]
#         self.SOC_min = input_dict["min_SOC"]

#         # Charge (Energy) limits [kJ]
#         self.E_min = kWh2kJ(self.SOC_min * self.energy_capacity)
#         self.E_max = kWh2kJ(self.SOC_max * self.energy_capacity)

#         charge_rate = input_dict["charge_rate"] * 1e3  # [kW]
#         discharge_rate = input_dict["discharge_rate"] * 1e3  # [kW]

#         # Charge/discharge (Power) limits [kW]
#         self.P_min = -discharge_rate
#         self.P_max = charge_rate

#         # Ramp up/down limits [kW/s]
#         self.R_min = -np.inf
#         self.R_max = np.inf

#         # self.total_battery_capacity = 3600 * self.energy_capacity / self.dt
#         self.current_batt_state = self.SOC * self.energy_capacity
#         self.E = kWh2kJ(self.current_batt_state)

#         self.power_mw = 0
#         self.P_reject = 0
#         self.P_charge = 0

#         self.needed_inputs = {}

#     def return_outputs(self):
#         return {"power": self.power_mw, "reject": self.P_reject, "soc": self.SOC}

#     def step(self, inputs):
#         P_signal = inputs["setpoints"]["battery"][
#             "signal"
#         ]  # power available for the battery to use for charging (should be >=0)
#         P_avail = inputs["py_sims"]["inputs"][
#             "available_power"
#         ]  # power signal desired by the controller

#         self.control(P_avail, P_signal)

#         # Update energy state
#         self.E += self.P_charge * self.dt

#         self.current_batt_state = kJ2kWh(self.E)

#         self.power_mw = self.P_charge
#         self.SOC = self.current_batt_state / self.energy_capacity

#         return self.return_outputs()

#     def control(self, P_avail, P_signal):
#         """
#         Low-level controller to enforce charging and energy constraints

#         InputsL
#         - P_avail: [kW] the available power for charging
#         - P_signal: [kW] the desired charging power

#         This method calculates
#         - P_charge: [kW] (positive of negative) the charging/discharging power
#         - P_reject: [kW] (positive or negative) either the extra power that the
#                     battery cannot absorb (positive) or the power required but
#                     not provided for the battery to charge/discharge without violating
#                     constraints (negative)
#         """

#         # Upper constraints [kW]
#         c_hi1 = (self.E_max - self.E) / self.dt  # energy
#         c_hi2 = self.P_max  # power
#         c_hi3 = self.R_max * self.dt + self.P_charge  # ramp rate

#         # Lower constraints [kW]
#         c_lo1 = (self.E_min - self.E) / self.dt  # energy
#         c_lo2 = self.P_min  # power
#         c_lo3 = self.R_min * self.dt + self.P_charge  # ramp rate

#         # High constraint is the most restrictive of the high constraints
#         c_hi = np.min([c_hi1, c_hi2, c_hi3, P_avail])

#         # Low constraint is the most restrictive of the low constraints
#         c_lo = np.max([c_lo1, c_lo2, c_lo3])
#         # TODO: force low constraint to be no higher than lowest high constraint

#         if (P_signal >= c_lo) & (P_signal <= c_hi):
#             self.P_charge = P_signal
#             self.P_reject = 0
#         elif P_signal < c_lo:
#             self.P_charge = c_lo
#             self.P_reject = P_signal - self.P_charge
#         elif P_signal > c_hi:
#             self.P_charge = c_hi
#             self.P_reject = P_signal - self.P_charge


if __name__ == "__main__":

    battery_dict = {
        "py_sim_type": SimpleBattery,
        "size": 20,  # MW size of the battery
        "energy_capacity": 3.3*15.756 * 1e-6,  # total capcity of the battery in MWh (4-hour 20 MW battery)
        "charge_rate": 2,  # charge rate of the battery in MW
        "discharge_rate": 2,  # discharge rate of the battery in MW
        "max_SOC": 0.9,  # upper boundary on battery SOC
        "min_SOC": 0.1,  # lower boundary on battery SOC
        "initial_conditions": {"SOC": 0.9},
    }
    dt = 1
    SB = SimpleBattery(battery_dict, dt)

    high = 15
    low = -15

    I_CCDC = -np.concatenate([
        high * np.ones(1000),
        np.zeros(1000),
        low * np.ones(666),
        np.zeros(666),
        high*np.ones(666),
        np.zeros(666),
        low*np.ones(666),
        np.zeros(666),
        high*np.ones(666),
        np.zeros(2000)
    ])

    V_cell = np.zeros(len(I_CCDC))
    SOC = np.zeros(len(I_CCDC))


    SB.SOC = .5

    for i in range(len(I_CCDC)):
        i_charge = I_CCDC[i] 
        I_charge = i_charge * SB.n_p
        SB.step_cell(i_charge)
        V_cell[i] = SB.V_cell(I_charge)
        SOC[i] = SB.SOC
        SB.SOC = SB.SOC + I_charge / (SB.C*3600 )
        if not i%500:
            print(SB.SOC)

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 1, sharex='col')

    ax0t = ax[0].twinx()
    ax0t.plot(I_CCDC, zorder=.9, color="red", linewidth=.75)
    ax0t.set_ylabel("Cell current [A]")

    ax[0].plot(V_cell)
    ax[0].set_ylabel("Cell voltage [V]")
    
    ax[1].plot(SOC)
    ax[1].set_ylabel("SOC")
    ax[1].set_xlabel("Time [s]" )


    fig, ax = plt.subplots(1,1)
    SOCs = np.linspace(0, 1, 100)
    ax.plot(SOCs, OCV(SOCs))
    ax.set_xlabel("SOC")
    ax.set_ylabel("OCV")


    # test parameters

    temperatures = np.arange(5, 45+1, 10)
    SOCs = np.arange(10, 90+1, 10) 
    SOH = np.array([92, 78, 65])

    for temp in temperatures:
        for soc in SOCs:
            A, B, C, D = build_SS(soc, temp, SOH[0])
            print(f"Temp: {temp}, SOC: {soc}, R0: {R0(SOH[0], temp, soc)*1e6:.0f}, R1: {R1(SOH[0], temp, soc)*1e6:.0f}, C1: {C1(SOH[0], temp, soc):.0f}, eig A: {A:.2e}")



    []

