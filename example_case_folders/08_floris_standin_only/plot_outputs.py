# Plot the outputs of the simulation

import matplotlib.pyplot as plt
import pandas as pd

# Read the Hercules output file
df = pd.read_csv("outputs/hercules_output.csv", index_col=False)


# Plot the turbine powers
fig, ax = plt.subplots()
time = df["hercules_comms.amr_wind.wind_farm_0.sim_time_s_amr_wind"]
ax.plot(time, df["hercules_comms.amr_wind.wind_farm_0.turbine_powers.000"], label="WT000", lw=3)
ax.plot(time, df["hercules_comms.amr_wind.wind_farm_0.turbine_powers.001"], label="WT001")
ax.set_ylabel("Power [kW]")
ax.set_xlabel("Time")
ax.legend()
ax.grid()


plt.show()
