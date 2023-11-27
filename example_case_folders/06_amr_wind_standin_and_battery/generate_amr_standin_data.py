import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

n_turbines = 2
turb_rating = 1000  # kW


time_start = 0
time_end = 1000
time_delta = 1
time = np.arange(time_start, time_end, time_delta)

amr_wind_speed = np.linspace(0, 20, len(time))
amr_wind_direction = np.linspace(200, 240, len(time))

turbine_powers = np.zeros([len(time), n_turbines])

for i in range(len(time)):
    turb_powers = (
        np.ones(n_turbines) * amr_wind_speed[i] ** 3 + np.random.rand(n_turbines) * 50
    )
    turb_powers[int(n_turbines / 2) :] = 0.75 * turb_powers[int(n_turbines / 2) :]
    turb_powers = [np.min([turb_rating, tp]) for tp in turb_powers]
    turbine_powers[i, :] = turb_powers

df_dict = {
    "time": time,
    "amr_wind_speed": amr_wind_speed,
    "amr_wind_direction": amr_wind_direction,
}

for i in range(n_turbines):
    df_dict.update({f"turbine_power_{i}": turbine_powers[:, i]})

df = pd.DataFrame(df_dict)
df.to_csv("project/battery_example/amr_standin_windpower.csv")

fig, ax = plt.subplots(3, 1, sharex="col")

ax[0].plot(time, amr_wind_speed)
ax[0].set_title("wind speed [m/s]")
ax[1].plot(time, amr_wind_direction)
ax[1].set_title("wind direction [deg]")
ax[2].plot(time, turbine_powers)
ax[2].set_title("turbine powers")

# plt.show()


sim_time_s = 775.2

amr_wind_speed = np.interp(sim_time_s, df["time"], df["amr_wind_speed"])
amr_wind_direction = np.interp(sim_time_s, df["time"], df["amr_wind_direction"])
turbine_powers = [
    np.interp(sim_time_s, df["time"], df[f"turbine_power_{turb}"])
    for turb in range(n_turbines)
]

[]
# wind_power = np.concatenate(
#     [np.zeros(10), np.linspace(1, 1e3, 100), 1e3 * np.ones(50), 750 * np.ones(200)]
# )
# # wind_powers = np.tile(wind_power, [n_turbines, 1])
# wind_powers = [wind_power] * n_turbines
# time = np.arange(0, len(wind_power), 1)
# wind_powers.append(time)

# amr_standin = np.stack(wind_powers)

# np.savetxt(
#     "project/battery_example/amr_standin_windpower.csv", amr_standin, delimiter=","
# )

# if __name__ == "__main__":
#     fig, ax = plt.subplots(2, 1, sharex="col")
#     ax[0].plot(wind_power)

#     time = np.linspace(0, len(wind_power), len(wind_power))
#     time_rand = time + 3 * np.random.random(len(wind_power))

#     def sample_wind(sample_time):
#         return np.interp(sample_time, time, wind_power)

#     wind_rand = np.zeros(len(time_rand))

#     for i in range(len(wind_power)):
#         wind_rand[i] = sample_wind(time_rand[i])

#     ax[1].plot(time_rand, wind_rand, "b.-")

#     plt.show()

#     []
