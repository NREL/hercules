"""
Standalone Solar PySAM example - to test functionality without Helics
for debugging PySAM integration
"""
import numpy as np
import matplotlib.pyplot as plt

from hercules.python_simulators.solar_pysam import SolarPySAM

# Initialize solar dict
solar_dict = {
    "py_sim_type": SolarPySAM,
    "weather_file_name": '/Users/bstanisl/hercules-pysam/hercules/example_case_folders/07_amr_wind_dummy_and_solar_pysam/NonAnnualSimulation-sample_data.csv',
    #  "capacity": 700, # MW

    "initial_conditions": {
        "power": 25, 
        "irradiance": 1000
    },
}

dt = 60 # s - input file has a dt of 1 min

SPS = SolarPySAM(solar_dict, dt)

# Simple simulation
# inputs = {"controller": {"signal": 0}, "py_sims": {"inputs": {"available_power": 2000}}}

# outputs = SPS.step(inputs, 0)

time_start = 0
time_end = 4 * 60
time_delta = dt
time = np.arange(time_start, time_end, time_delta)

print('time = ', time)

# available_power = 2.5e3 * np.ones(len(time)) + np.concatenate(
#     [np.zeros(int((1 - 0.5) * len(time))), np.linspace(0, -2e3, int(0.5 * len(time)))]
# )

# signal = np.concatenate(
#     [
#         np.linspace(2.5e3, -2.5e3, int(0.4 * len(time))),
#         np.zeros(int((1 - 0.4) * len(time))),
#     ]
# ) + np.concatenate(
#     [np.zeros(int((1 - 0.5) * len(time))), np.linspace(0, 2e3, int(0.5 * len(time)))]
# )

def simulate(SPS, time):
    inputs = {
        "controller": {"signal": 0},
        "py_sims": {"inputs": {"available_power": 100}},
    }

    power = np.zeros(len(time))
    irradiance = np.zeros(len(time))

    for i in range(len(time)):
        # inputs["py_sims"]["inputs"]["available_power"] = available_power[i]
        outputs = SPS.step(inputs,time[i])
        power[i] = outputs["power"]
        irradiance[i] = outputs["irradiance"]

    fig, ax = plt.subplots(3, 1, sharex="col")

    ax[0].plot(time, power, '.-', label="power")
    # ax[0].plot(time, irradiance, linestyle="dashed", label="irradiance")
    # ax[0].plot(time, available_power - batt_power, linestyle="dotted", label="P_down_batt")
    # ax[0].plot(time, batt_reject, linestyle="dashdot", label="P_down_cont")
    ax[0].legend()

    # ax[1].hlines(
    #     [batt_dict["charge_rate"] * 1e3, -batt_dict["discharge_rate"] * 1e3],
    #     time_start,
    #     time_end,
    #     alpha=0.5,
    #     linewidth=0.5,
    #     color="black",
    # )

    ax[1].plot(time, irradiance, '.-', label="irradiance")
    # ax[1].plot(time, batt_reject, linestyle="dashed", label="P_reject")
    ax[1].legend()
    # ax[1].set_ylim(
    #     [-1.5 * batt_dict["discharge_rate"] * 1e3, 1.5 * batt_dict["charge_rate"] * 1e3]
    # )

    # ax[2].hlines(
    #     [batt_dict["min_SOC"], batt_dict["max_SOC"]],
    #     time_start,
    #     time_end,
    #     alpha=0.5,
    #     linewidth=0.5,
    #     color="black",
    # )

    # ax[2].plot(time, batt_soc, label="SOC")
    # ax[2].legend()

    plt.show()

simulate(SPS, time)