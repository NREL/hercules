# Plot the outputs of the simulation

import matplotlib.pyplot as plt
import pandas as pd

# Read the Hercules output file
df = pd.read_csv("outputs/hercules_output.csv", index_col=False)

# Set number of turbines
n_turbines = 3

# Define a consistent color map with 3 entries
colors = ["tab:blue", "tab:orange", "tab:green"]

fig, axarr = plt.subplots(sharex=True) #2, 1, sharex=True)

# Plot the wind speeds
# ax = axarr[0]
# for t_idx in range(3):
#     ax.plot(
#         df["time"],
#         df[f"py_sims.wind_farm_0.outputs.unwaked_velocity.{t_idx:03}"],
#         label=f"Unwaked {t_idx}",
#         color=colors[t_idx],
#     )
# for t_idx in range(3):
#     ax.plot(
#         df["time"],
#         df[f"py_sims.wind_farm_0.outputs.waked_velocity.{t_idx:03}"],
#         label=f"Waked {t_idx}",
#         linestyle="--",
#         color=colors[t_idx],
#     )

# Plot the FLORIS wind speed
# ax.plot(
#     df["time"],
#     df["py_sims.wind_farm_0.outputs.floris_wind_speed"],
#     label="FLORIS",
#     color="black",
#     lw=2,
# )

# ax.grid(True)
# ax.legend()
# ax.set_ylabel("Wind Speed [m/s]")


# Plot the power
ax = axarr
for t_idx in range(3):
    ax.plot(
        df["time"],
        df[f"py_sims.wind_farm_0.outputs.power.{t_idx:03}"],
        label=f"Turbine {t_idx}",
        # color=colors[t_idx],
    )
# for t_idx in range(3):
#     ax.plot(
#         df["time"],
#         df[f"py_sims.inputs.derating_{t_idx:03d}"],
#         label=f"Derating {t_idx}",
#         linestyle="--",
#         color=colors[t_idx],
#     )

ax.plot(
    df["time"],
    df[f"py_sims.solar_farm_0.outputs.power_mw"]*1000,
    label=f"Solar PV",
)

total_power = df[f"py_sims.solar_farm_0.outputs.power_mw"]*1000
for t_idx in range(3):
    total_power = total_power + df[f"py_sims.wind_farm_0.outputs.power.{t_idx:03}"]

ax.plot(
    df["time"],
    total_power,
    label=f"Total",
    color='k',
)

ax.grid(True)
ax.legend()
ax.set_xlabel("Time [s]")
ax.set_ylabel("Power [kW]")


# solar plots
# fig, axs = plt.subplots(2, 1, sharex=True)

# axs[0].plot(df["time"], df["py_sims.solar_farm_0.outputs.dni"])
# axs[0].grid(True)
# axs[0].set_ylabel("Direct Normal Irradiance [W/m^2]")

# axs[1].plot(df["time"], df["py_sims.solar_farm_0.outputs.power_mw"]*1000, label="solar PV")
# axs[1].grid(True)
# axs[1].legend()
# axs[1].set_xlabel("Time [s]")
# axs[1].set_ylabel("Power [kW]")
plt.show()
