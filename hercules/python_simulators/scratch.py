import json

model_params = json.load('example_case_folders/07_amr_wind_standin_and_solar_pysam/100MW_1axis_pvsamv1.json')

# solar_dict = {
#     "weather_file_name": None,
#     "weather_data_input": {
#         "Timestamp": ['2018-05-10 12:31:00+00:00'],
#         "SRRL BMS Direct Normal Irradiance (W/m²_irr)": [330.8601989746094],
#         "SRRL BMS Diffuse Horizontal Irradiance (W/m²_irr)": [68.23037719726561],
#         "SRRL BMS Global Horizontal Irradiance (W/m²_irr)": [68.23037719726561],
#         "SRRL BMS Wind Speed at 19' (m/s)": [0.4400002620664621],
#         "SRRL BMS Dry Bulb Temperature (°C)": [11.990000406901045],
#     },

#     "system_info_file_name": "100MW_1axis_pvsamv1.json",
#     "system_info_data_input": {
#         "ModelParams": {
#             "array_type": 2.0,
#             "azimuth": 180.0,
#             "dc_ac_ratio": 1.08,
#             "gcr": 0.592,
#             "inv_eff": 97.5,
#             "losses": 15.53,
#             "module_type": 2.0,
#             "system_capacity": 720,
#             "tilt": 0.0,
#             "SolarResource": {
#             }
#         },
#         "Other": {
#             "lat": 39.7442,
#             "lon": -105.1778,
#             "elev": 1829
#         }
#     },

#     "initial_conditions": {
#         "power": 25, 
#         "irradiance": 1000
#     },
# }

# with open("/Users/bstanisl/hercules-pysam/hercules/example_case_folders/07_amr_wind_standin_and_solar_pysam/{}".format(solar_dict["system_info_file_name"]), "r") as f:
#     model_params = json.load(f)
# sys_design_1 = {
#     "ModelParams": model_params,
#     "Other": {"lat": 39.7442, "lon": -105.1778, "elev": 1829},
# }
# print("sys_design_1")
# print(sys_design_1)

# sys_design_2 = solar_dict["system_info_data_input"]
# print("sys_design_2")
# print(sys_design_2)

step_inputs = {
    "py_sims": {
        "inputs": {
            "sim_time_s": 0,
        },
    },
}

print(step_inputs["py_sims"]["inputs"]["sim_time_s"])