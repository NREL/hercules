"""
Standalone Solar PySAM example - to test functionality without Helics
for debugging PySAM integration
"""
import matplotlib.pyplot as plt
import numpy as np
from hercules.python_simulators.solar_pysam import SolarPySAM

# Initialize solar dict
# -------- using 1-minute data
# solar_dict = {
#     "py_sim_type": SolarPySAM,
#     "weather_file_name": "NonAnnualSimulation-sample_data-interpolated-daytime.csv"
#     "initial_conditions": {
#         "power": 25,
#         "irradiance": 1000
#     },
# }

# dt = 60 # s - input file has a dt of 1 min

# time_start = 0
# time_end = 4 * 60 # 800 * 60 #[s] NonAnnualSimulation-sample-data contains 24 hrs

# -------- using interpolated data
solar_dict = {
    "py_sim_type": SolarPySAM,
    "weather_file_name": "NonAnnualSimulation-sample_data-interpolated-daytime.csv",
    "system_info_file_name": "100MW_1axis_pvsamv1.json",
    "lat": 39.7442, 
    "lon": -105.1778, 
    "elev": 1829,
    "initial_conditions": {"power": 25, "dni": 1000},
}

dt = 0.5  # s - input file has a dt of 1 min

time_start = 0
time_end = 10 # 100  # 11*3600 #[s] NonAnnualSimulation-sample-data contains 24 hrs

# -------- start simulation
SPS = SolarPySAM(solar_dict, dt)

time_delta = dt
time = np.arange(time_start, time_end, time_delta)
print("time = ", time)


def simulate(SPS, time):
    inputs = {
        "controller": {"signal": 0},
        # "py_sims": {"inputs": {"available_power": 100, "time": 0}},
        "inputs": {"time": 0},
    }

    power = np.zeros(len(time))

    dc_power = np.zeros(len(time))
    aoi = np.zeros(len(time))
    irradiance = np.zeros(len(time))

    for i in range(len(time)):
        inputs["time"] = time[i]
        outputs = SPS.step(inputs)
        power[i] = outputs["power_mw"]
        # dc_power[i] = outputs["dc_power_mw"]
        aoi[i] = outputs["aoi"]
        irradiance[i] = outputs["dni"]

    fig, ax = plt.subplots(3, 1, sharex="col")  # , figsize=[6,5], dpi=250)

    ax[0].plot(time / 3600, power, ".-", label="power")
    ax[0].set_ylabel("ac power")
    # ax[0].legend()

    # ax[1].plot(time / 3600, dc_power, ".-", label="dc power")
    # ax[1].set_ylabel("dc power")

    ax[1].plot(time / 3600, irradiance, ".-", label="irradiance")
    ax[1].set_ylabel("irradiance")
    # ax[1].legend()

    ax[2].plot(time / 3600, aoi, ".-", label="aoi")
    ax[2].set_ylabel("aoi")
    ax[-1].set_xlabel("time [hr]")

    plt.show()


simulate(SPS, time)
