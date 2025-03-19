# Plot the outputs of the simulation

import matplotlib.pyplot as plt
import pandas as pd

# Read the Hercules output file
df = pd.read_csv("outputs/hercules_output.csv", index_col=False)

power_ref_input = pd.read_csv("inputs/power_reference_signal.csv")

# Extract individual components powers as well as total power
if "py_sims.solar_farm_0.outputs.power_mw" in df.columns:
    solar_power = df["py_sims.solar_farm_0.outputs.power_mw"]
else:
    solar_power = [0] * len(df)
n_wind_turbines = 2
wind_power = df[["hercules_comms.amr_wind.wind_farm_0.turbine_powers.{0:03d}".format(t)
                 for t in range(n_wind_turbines)]].to_numpy().sum(axis=1) / 1e3
if "py_sims.battery_0.outputs.power" in df.columns:
    battery_power = -df["py_sims.battery_0.outputs.power"] / 1e3 # discharging positive
else:
    battery_power = [0] * len(df)
power_output = (df["py_sims.inputs.available_power"] / 1e3 + battery_power)
time = df["hercules_comms.amr_wind.wind_farm_0.sim_time_s_amr_wind"] / 60 # minutes

# Set plotting aesthetics
wind_col = "C0"
solar_col = "C1"
battery_col = "C2"
plant_col = "C3"

# Plotting power outputs from each technology as well as the total power output (top)
# Plotting the SOC of the battery (bottom)
fig, ax = plt.subplots(1, 1, sharex=True, figsize=(7,5))
ax.plot(time, wind_power, label="Wind", color=wind_col)
ax.plot(time, battery_power, label="Battery", color=battery_col)
ax.plot(time, power_output, label="Plant output", color=plant_col)
ax.plot(power_ref_input['time'] / 60, power_ref_input['plant_power_reference']/1e3,\
            'k--', label="Reference")
ax.set_ylabel("Power [MW]")
ax.set_xlabel("Time [mins]")
ax.grid()
ax.legend(loc="lower right")
# ax.set_xlim([0, 10])

# fig.savefig("../../docs/graphics/simple-hybrid-example-plot.png", dpi=300, format="png")

# Plot the battery power and state of charge, if battery component included
if "py_sims.battery_0.outputs.power" in df.columns:
    battery_soc = df["py_sims.battery_0.outputs.soc"]
    fig, ax = plt.subplots(2, 1, sharex=True, figsize=(7,5))
    ax[0].plot(time, battery_power, color=battery_col)
    ax[1].plot(time, battery_soc, color=battery_col)
    ax[0].set_ylabel("Battery power [MW]")
    ax[0].grid()
    ax[1].set_ylabel("Battery SOC")
    ax[1].set_xlabel("Time [mins]")
    ax[1].grid()

    battery_cycle_usage = df["py_sims.battery_0.outputs.usage_in_cycles"]
    battery_time_usage = df["py_sims.battery_0.outputs.usage_in_time"]
    battery_cycle_count = df["py_sims.battery_0.outputs.total_cycles"]


    fig, ax = plt.subplots(3, 1, sharex=True, figsize=(7,5))
    ax[0].set_title("Battery Usage Comparison")
    ax[0].plot(time, battery_time_usage, color=battery_col)
    ax[0].set_ylabel("Time Use %")
    ax[1].plot(time, battery_cycle_usage, color=battery_col)
    ax[0].grid()
    ax[1].grid()
    ax[1].set_ylabel("Cycle Use %")
    ax[2].set_xlabel("Time [mins]")
    ax[2].plot(time, battery_cycle_count, color=battery_col)
    ax[2].grid()
    ax[2].set_ylabel("Cycle Count")


# Plot the wind data
wind_power_individuals = df[["hercules_comms.amr_wind.wind_farm_0.turbine_powers.{0:03d}".format(t)
                             for t in range(n_wind_turbines)]].to_numpy() / 1e3
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(7,5))
ax[0].plot(time, wind_power, color=wind_col)
for i in range (n_wind_turbines):
    ax[1].plot(time, wind_power_individuals[:,i], label="WT"+str(i), alpha=0.7, color=wind_col)
ax[0].set_ylabel("Total wind power [MW]")
ax[1].set_ylabel("Individual turbine power [MW]")
ax[0].grid()
ax[1].grid()
ax[1].set_xlabel("Time [mins]")


# Plot the turbine powers
fig, ax = plt.subplots()
time = df["hercules_comms.amr_wind.wind_farm_0.sim_time_s_amr_wind"]
ax.plot(time, df["hercules_comms.amr_wind.wind_farm_0.turbine_powers.000"], label="WT000",lw=3)
ax.plot(time, df["hercules_comms.amr_wind.wind_farm_0.turbine_powers.001"], label="WT001")
ax.plot(time, df["py_sims.inputs.available_power"], label="available power")
ax.set_ylabel("Power [kW]")
ax.set_xlabel("Time")
ax.legend()
ax.grid()

fig, ax = plt.subplots()
ax.plot(time, df["py_sims.battery_0.outputs.power"], label="Battery Power")
ax.set_ylabel("Power")
ax.set_xlabel("Time")
ax.legend()

fig, ax = plt.subplots()
ax.plot(time, df["py_sims.battery_0.outputs.soc"], label="Battery SOC")
ax.set_ylabel("SOC")
ax.set_xlabel("Time")
ax.legend()
plt.show()