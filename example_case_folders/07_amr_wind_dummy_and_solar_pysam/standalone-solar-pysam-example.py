"""
Standalone Solar PySAM example - to test functionality without Helics
for debugging PySAM integration
"""
import numpy as np
import matplotlib.pyplot as plt

from hercules.python_simulators.solar_pysam import SolarPySAM

# Initialize solar dict
# -------- using 1-minute data
# solar_dict = {
#     "py_sim_type": SolarPySAM,
#     "weather_file_name": '/Users/bstanisl/hercules-pysam/hercules/example_case_folders/07_amr_wind_dummy_and_solar_pysam/NonAnnualSimulation-sample_data.csv',

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
    "weather_file_name": '/Users/bstanisl/hercules-pysam/hercules/example_case_folders/07_amr_wind_dummy_and_solar_pysam/NonAnnualSimulation-sample_data-interpolated-daytime.csv',
    "system_info_file_name": '/Users/bstanisl/hercules-pysam/hercules/example_case_folders/07_amr_wind_dummy_and_solar_pysam/100MW_1axis_pvsamv1.json',

    "initial_conditions": {
        "power": 25, 
        "irradiance": 1000
    },
}

dt = 0.5 # s - input file has a dt of 1 min

time_start = 0
time_end = 100 # 11*3600 #[s] NonAnnualSimulation-sample-data contains 24 hrs

# -------- start simulation
SPS = SolarPySAM(solar_dict, dt)

time_delta = dt
time = np.arange(time_start, time_end, time_delta)
print('time = ', time)

def simulate(SPS, time):
    inputs = {
        "controller": {"signal": 0},
        "py_sims": {"inputs": {"available_power": 100,
                               "sim_time_s": 0}},
    }

    power = np.zeros(len(time))
    dc_power = np.zeros(len(time))
    aoi = np.zeros(len(time))
    irradiance = np.zeros(len(time))

    for i in range(len(time)):
        inputs["py_sims"]["inputs"]["sim_time_s"] = time[i]
        outputs = SPS.step(inputs)
        power[i] = outputs["power"]
        dc_power[i] = outputs["dc_power"]
        aoi[i] = outputs["aoi"]
        irradiance[i] = outputs["irradiance"]

    fig, ax = plt.subplots(4, 1, sharex="col") #, figsize=[6,5], dpi=250)

    ax[0].plot(time/3600, power, '.-', label="power")
    ax[0].set_ylabel('ac power')
    # ax[0].legend()

    ax[1].plot(time/3600, dc_power, '.-', label="dc power")
    ax[1].set_ylabel('dc power')

    ax[2].plot(time/3600, irradiance, '.-', label="irradiance")
    ax[2].set_ylabel('irradiance')
    # ax[1].legend()

    ax[3].plot(time/3600, aoi, '.-', label="aoi")
    ax[3].set_ylabel('aoi')
    ax[-1].set_xlabel('time [hr]')

    plt.show()

simulate(SPS, time)