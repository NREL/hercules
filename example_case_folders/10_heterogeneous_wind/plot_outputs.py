# Plot the outputs of the simulation

import matplotlib.pyplot as plt
import pandas as pd

# Read the Hercules output file
df = pd.read_csv("outputs/hercules_output_cl.csv", index_col=False)

fig, ax = plt.subplots()
ax.fill_between(df['time'],0, df['hercules_comms.amr_wind.wind_farm_0.wind_farm_power'],
                 label="Wind Farm Power",color='blue', alpha=0.5)
ax.plot(df['time'],df['external_signals.wind_power_reference'],'k--',label="Wind Power Reference")
ax.grid(True)
ax.legend()
ax.set_xlabel("Time [s]")
ax.set_ylabel("Power [kW]")
plt.show()

