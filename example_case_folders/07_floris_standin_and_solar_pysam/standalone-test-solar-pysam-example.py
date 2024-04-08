"""
Standalone Solar PySAM example - to test functionality without Helics
for debugging PySAM integration
"""
import matplotlib.pyplot as plt
import numpy as np
from hercules.python_simulators.solar_pysam import SolarPySAM

# Initialize solar dict
# -------- using interpolated data
# solar_dict = {
#     "py_sim_type": SolarPySAM,
#     "weather_file_name": 'NonAnnualSimulation-sample_data-interpolated-daytime.csv',
#     "system_info_file_name": '100MW_1axis_pvsamv1.json',

#     "initial_conditions": {
#         "power": 25, 
#         "irradiance": 1000
#     },
# }

# -------- testing functionality without a weather file - single timestep
# solar_dict = {
#     "py_sim_type": SolarPySAM,
#     "weather_file_name": None,
#     "weather_data_input": {
#         "Timestamp": ['2018-05-10 12:31:00+00:00'],
#         "SRRL BMS Direct Normal Irradiance (W/m²_irr)": [330.8601989746094],
#         "SRRL BMS Diffuse Horizontal Irradiance (W/m²_irr)": [68.23037719726561],
#         "SRRL BMS Global Horizontal Irradiance (W/m²_irr)": [68.23037719726561],
#         "SRRL BMS Wind Speed at 19' (m/s)": [0.4400002620664621],
#         "SRRL BMS Dry Bulb Temperature (°C)": [11.990000406901045],
#     },

#     "system_info_file_name": '100MW_1axis_pvsamv1.json',
#     # "system_info_file_name": None,
#     "lat": 39.7442, 
#     "lon": -105.1778, 
#     "elev": 1829,
#     "initial_conditions": {
#         "power": 25, 
#         "dni": 1000 # direct normal irradiance
#     },

#     "power_setpoints": {"time_s": 0.0, "power_mw": 10.}
# }

# -------- using interpolated data - five timesteps
solar_dict = {
    "py_sim_type": SolarPySAM,
    "weather_file_name": 'fivetimesteps-sample_data-interpolated.csv',
    "system_info_file_name": '100MW_1axis_pvsamv1.json',
    "lat": 39.7442, 
    "lon": -105.1778, 
    "elev": 1829,
    "initial_conditions": {
        "power": 25, 
        "dni": 1000 # direct normal irradiance
    },

    # "power_setpoints": {"time_s": [0.0, 0.5, 1.0, 1.5, 2.0], 
    #                               "power_mw": [10., 11., 12., 11., 10.]}

    "external_data_file": "solar_power_reference_data.csv"
}

dt = 0.5 # s - input file has a dt of 1 min

time_start = 0
time_end = 2.5 # 11*3600 #[s] NonAnnualSimulation-sample-data contains 24 hrs

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
        "external_signals": {"solar_power_reference": {"time_s": 0.0, "power_mw": 10.}},
    }

    power = np.zeros(len(time))
    dc_power = np.zeros(len(time))
    aoi = np.zeros(len(time))
    dni = np.zeros(len(time))

    for i in range(len(time)):
        inputs["py_sims"]["inputs"]["sim_time_s"] = time[i]
        outputs = SPS.step(inputs)
        power[i] = outputs["power_mw"]
        dc_power[i] = outputs["dc_power_mw"]
        aoi[i] = outputs["aoi"]
        dni[i] = outputs["dni"]

    fig, ax = plt.subplots(3, 1, sharex="col") #, figsize=[6,5], dpi=250)

    ax[0].plot(time/3600, power, '.-', label="power")
    ax[0].set_ylabel('ac power')
    # ax[0].legend()

    # ax[1].plot(time/3600, dc_power, '.-', label="dc power")
    # ax[1].set_ylabel('dc power')

    ax[1].plot(time/3600, dni, '.-', label="irradiance")
    ax[1].set_ylabel('irradiance')
    # ax[1].legend()

    ax[2].plot(time/3600, aoi, '.-', label="aoi")
    ax[2].set_ylabel('aoi')
    ax[-1].set_xlabel('time [hr]')

    plt.show()

simulate(SPS, time)