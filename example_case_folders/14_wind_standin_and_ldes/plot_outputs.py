# Plot the outputs of the simulation

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Read the Hercules output file
df_ag = pd.read_csv("outputs/hercules_output_ag.csv", index_col=False)
df_pr = pd.read_csv("outputs/hercules_output_pr.csv", index_col=False)

power_ref_input = df_ag["external_signals.plant_power_reference"] / 1e3

# Extract individual components powers as well as total power
n_wind_turbines = 2
wind_power_ag = df_ag[["hercules_comms.amr_wind.wind_farm_0.turbine_powers.{0:03d}".format(t)
                 for t in range(n_wind_turbines)]].to_numpy().sum(axis=1) / 1e3
wind_power_pr = df_pr[["hercules_comms.amr_wind.wind_farm_0.turbine_powers.{0:03d}".format(t)
                 for t in range(n_wind_turbines)]].to_numpy().sum(axis=1) / 1e3
battery_power_ag = -df_ag["py_sims.battery_0.outputs.power"] / 1e3 # discharging positive
battery_power_pr = -df_pr["py_sims.battery_0.outputs.power"] / 1e3 # discharging positive

power_output_ag = (df_ag["py_sims.inputs.available_power"] / 1e3 + battery_power_ag)
power_output_pr = (df_pr["py_sims.inputs.available_power"] / 1e3 + battery_power_pr)

time_ag = df_ag["hercules_comms.amr_wind.wind_farm_0.sim_time_s_amr_wind"] / 60 # minutes
time_pr = df_pr["hercules_comms.amr_wind.wind_farm_0.sim_time_s_amr_wind"] / 60 # minutes

# Set plotting aesthetics
wind_col = "C0"
solar_col = "C1"
battery_col = "C2"
plant_col = "C3"

# Calculate RMSE for power reference
N_ag = len(power_output_ag)
rmse_ag = np.sqrt( sum((power_output_ag-power_ref_input)**2) / N_ag)
print('RMSE of agressive controller: ', rmse_ag)

N_pr = len(power_output_pr)
rmse_pr = np.sqrt( sum((power_output_pr-power_ref_input)**2) / N_pr)
print('RMSE of protective controller: ', rmse_pr)

# Plotting power outputs from each technology as well as the total power output (top)
# Plotting the SOC of the battery (bottom)
fig, ax = plt.subplots(1, 1, sharex=True, figsize=(7,5))
ax.plot(time_ag, wind_power_ag, label="Wind", color=wind_col)
ax.plot(time_ag, battery_power_ag, label="Battery", color=battery_col)
ax.plot(time_ag, power_output_ag, label="Plant output", color=plant_col)
ax.plot(time_ag, power_ref_input,\
            'k--', label="Reference")
ax.set_ylabel("Power [MW]")
ax.set_xlabel("Time [mins]")
ax.grid()
ax.legend(loc="best")
ax.text(15, 4, "RMSE ="+str(round(rmse_ag,4)), fontsize=12)
ax.set_xlim([-0.5, 20.5])
ax.set_ylim([-3, 11])
ax.set_title("Plant behavior with agressive battery controller")

fig, ax = plt.subplots(1, 1, sharex=True, figsize=(7,5))
ax.plot(time_pr, wind_power_pr, label="Wind", color=wind_col)
ax.plot(time_pr, battery_power_pr, label="Battery", color=battery_col)
ax.plot(time_pr, power_output_pr, label="Plant output", color=plant_col)
ax.plot(time_ag, power_ref_input,\
            'k--', label="Reference")
ax.set_ylabel("Power [MW]")
ax.set_xlabel("Time [mins]")
ax.grid()
ax.legend(loc="best")
ax.text(15, 4, "RMSE ="+str(round(rmse_pr,4)), fontsize=12)
ax.set_xlim([-0.5, 20.5])
ax.set_ylim([-3, 11])
ax.set_title("Plant behavior with protective battery controller")

# fig.savefig("../../docs/graphics/simple-hybrid-example-plot.png", dpi=300, format="png")

# Plot to compare battery behavior 
battery_soc_ag = df_ag["py_sims.battery_0.outputs.soc"]
battery_soc_pr = df_pr["py_sims.battery_0.outputs.soc"]
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(7,5))
ax[0].plot(time_ag, battery_power_ag, color=battery_col, label="Agressive")
ax[0].plot(time_pr, battery_power_pr, '--', color="teal", label="Protective")
ax[0].legend()
ax[1].plot(time_ag, battery_soc_ag, color=battery_col, label="Agressive")
ax[1].plot(time_pr, battery_soc_pr, '--', color="teal", label="Protective")
ax[0].set_ylabel("Battery power [MW]")
ax[0].grid()
ax[1].set_ylabel("Battery SOC")
ax[1].set_xlabel("Time [mins]")
ax[1].legend()
ax[1].grid()

# battery_cycle_usage = df["py_sims.battery_0.outputs.usage_in_cycles"]
# battery_time_usage = df["py_sims.battery_0.outputs.usage_in_time"]
battery_cycle_count_ag = df_ag["py_sims.battery_0.outputs.total_cycles"]
battery_cycle_count_pr = df_pr["py_sims.battery_0.outputs.total_cycles"]

fig, ax = plt.subplots(1, 1, sharex=True, figsize=(7,5))
ax.set_title("Battery Cycle Comparison")
ax.set_xlabel("Time [mins]")
ax.plot(time_ag, battery_cycle_count_ag, color=battery_col, label="Agressive")
ax.plot(time_pr, battery_cycle_count_pr, '--', color="teal", label="Protective")
ax.grid()
ax.legend()
ax.set_ylabel("Cycle Count")


# # Plot the wind data
# wind_power_individuals = df[["hercules_comms.amr_wind.wind_farm_0.turbine_powers.{0:03d}".format(t)
#                              for t in range(n_wind_turbines)]].to_numpy() / 1e3
# fig, ax = plt.subplots(2, 1, sharex=True, figsize=(7,5))
# ax[0].plot(time, wind_power, color=wind_col)
# for i in range (n_wind_turbines):
#     ax[1].plot(time, wind_power_individuals[:,i], label="WT"+str(i), alpha=0.7, color=wind_col)
# ax[0].set_ylabel("Total wind power [MW]")
# ax[1].set_ylabel("Individual turbine power [MW]")
# ax[0].grid()
# ax[1].grid()
# ax[1].set_xlabel("Time [mins]")


# # Plot the turbine powers
# fig, ax = plt.subplots()
# time = df["hercules_comms.amr_wind.wind_farm_0.sim_time_s_amr_wind"]
# ax.plot(time, df["hercules_comms.amr_wind.wind_farm_0.turbine_powers.000"], label="WT000",lw=3)
# ax.plot(time, df["hercules_comms.amr_wind.wind_farm_0.turbine_powers.001"], label="WT001")
# ax.plot(time, df["py_sims.inputs.available_power"], label="available power")
# ax.set_ylabel("Power [kW]")
# ax.set_xlabel("Time")
# ax.legend()
# ax.grid()

# fig, ax = plt.subplots()
# ax.plot(time, df["py_sims.battery_0.outputs.power"], label="Battery Power")
# ax.set_ylabel("Power")
# ax.set_xlabel("Time")
# ax.legend()

# fig, ax = plt.subplots()
# ax.plot(time, df["py_sims.battery_0.outputs.soc"], label="Battery SOC")
# ax.set_ylabel("SOC")
# ax.set_xlabel("Time")
# ax.legend()
plt.show()