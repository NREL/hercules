# Plot the outputs of the simulation

import matplotlib.pyplot as plt
import pandas as pd

# Read the Hercules output file
df = pd.read_csv("outputs/hercules_output.csv", index_col=False)

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