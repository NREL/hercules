# Plot the outputs of the simulation

import matplotlib.pyplot as plt
import pandas as pd

# Read the Hercules output file
df = pd.read_csv("outputs/hercules_output.csv", index_col=False)

fig, ax = plt.subplots()
for t_idx in range(3):
    ax.plot(df["time"], df[f"py_sims.wind_farm_0.outputs.power_mw.{t_idx:03}"], label=f"Turbine {t_idx}")
for t_idx in range(3):
    ax.plot(df["time"], df[f"py_sims.inputs.derating_kw_{t_idx}"]/1000., label=f"Derating {t_idx}", linestyle="--")
ax.grid(True)
ax.legend()
ax.set_xlabel("Time [s]")
ax.set_ylabel("Power [kW]")
plt.show()
