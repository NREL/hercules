from pathlib import Path

import numpy as np
from hercules.floris_standin import FlorisStandin

PRINT_VALUES = True

AMR_INPUT = Path(__file__).resolve().parents[1] / "test_inputs" / "amr_input_florisstandin.inp"
AMR_EXTERNAL_DATA = Path(__file__).resolve().parents[1] / "test_inputs" / "amr_standin_data.csv"
AMR_EXTERNAL_DATA_HET = (
    Path(__file__).resolve().parents[1] / "test_inputs" / "amr_standin_data_het.csv"
)

CONFIG = {
    "name": "floris_standin",
    "gridpack": {},
    "helics": {
        "deltat": 0.5,
        "subscription_topics": ["control"],
        "publication_topics": ["status"],
        "endpoints": [],
        "helicsport": None,
    },
    "publication_interval": 1,
    "endpoint_interval": 1,
    "starttime": 0,
    "stoptime": 10.0,
    "Agent": "floris_standin",
}

turbine_powers_base_homogeneous = np.array(
    [
        [1113.52361802, 1113.52361802],
        [2142.64210082, 2142.64210082],
        [3244.17171329, 3244.17171329],
        [3794.93651953, 3794.93651953],
        [4070.31892264, 4070.31892264],
        [3621.03975313, 3621.03975313],
        [2924.04349459, 2924.04349459],
        [2575.54536532, 2575.48482357],
        [2401.29630068, 1793.55047863],
        [2314.17176836, 1402.58330616],
        [2270.6095022 , 1207.09971992],
        [2248.82836912, 1109.3579268 ],
        [2237.93780259, 1060.48703024],
        [2232.49251932, 1036.05158196],
        [2229.76987768, 1023.83385782],
        [2700.76523065, 1227.51135281],
        [3523.23327821, 1577.36566855],
        [3934.46730198, 1752.29282642],
        [4140.08431387, 1839.75640535],
        [4242.89281982, 1883.48819482],
    ]
)

turbine_powers_base_power_setpoints_homogeneous = np.array(
    [
        [3234.97002793, 1941.74409741],
        [2967.48501397, 1970.87204871],
        [2833.74250698, 1985.43602435],
        [2766.87125349, 1992.71801218],
        [2733.43562675, 1996.35900609],
        [2716.71781337, 1998.17950304],
        [2471.88252471, 1999.08975152],
        [2349.46488038, 1999.54487576],
        [2288.25605821, 1505.58050472],
        [2257.65164713, 1258.5983192 ],
        [2242.34944159, 1135.10722644],
        [2234.69833882, 1073.36168006],
        [2230.87278743, 1042.48890688],
        [2228.96001174, 1027.05252028],
        [2228.00362389, 1019.33432698],
        [2464.00181195, 1280.63707775],
        [2582.00090597, 1640.31853888],
        [2641.00045299, 1820.15926944],
        [2670.50022649, 1910.07963472],
        [2685.25011325, 1955.03981736],
    ]
)

turbine_powers_base_yaw_angles_homogeneous = np.array(
    [
        [2335.98047657, 2059.42246609],
        [2590.80525787, 2574.86743458],
        [3242.52740902, 3403.91136399],
        [3568.3884846 , 3818.4333287 ],
        [3731.31902239, 4025.69431105],
        [3288.47453077, 3558.00335705],
        [2637.59268534, 2860.90423594],
        [2424.40579909, 2536.03899796],
        [2294.10545696, 1783.49319743],
        [2228.9552859 , 1407.22029717],
        [2196.38020036, 1219.08384704],
        [2180.0926576 , 1125.01562197],
        [2171.94888621, 1077.98150944],
        [2167.87700052, 1054.46445317],
        [2165.84105768, 1042.70592504],
        [2628.07673037, 1247.57278028],
        [3430.51601189, 1602.60703819],
        [3831.73565265, 1780.12416715],
        [4032.34547303, 1868.88273163],
        [4132.65038322, 1913.26201387],
    ]
)

turbine_powers_base_heterogeneous = np.array(
    [
        [ 820.33683601,  887.78598555],
        [1263.80810427, 1357.88344268],
        [1519.68950035, 1619.58041186],
        [1682.64119091, 1777.52992947],
        [1800.02639185, 1884.28469783],
        [1895.53278979, 1965.89494567],
        [1981.00726841, 2035.59669284],
        [2063.02099291, 2100.24980586],
        [2145.03411448, 2163.64852095],
        [2158.40380337, 2174.62022696],
        [2138.47380898, 2159.82748835],
        [2102.47777801, 2132.56296419],
        [2059.17748519, 2099.5224182 ],
        [2012.7611023 , 2064.02547125],
        [1965.08634754, 2027.53246872],
        [1917.15908259, 1990.76516954],
        [1869.63410465, 1954.08862578],
        [1822.60250053, 1917.68300341],
        [1776.18774836, 1881.63832002],
        [1730.56396809, 1846.00324647],
    ]
)

turbine_powers_base_power_setpoints_heterogeneous = np.array(
    [
        [1685.61882005, 1810.78760878],
        [1696.44909629, 1819.3842543 ],
        [1736.00999636, 1850.33081767],
        [1790.80143892, 1892.90513238],
        [1854.10651585, 1941.97229928],
        [1922.57285179, 1970.98614964],
        [1994.52729941, 1985.49307482],
        [2069.78100841, 1992.74653741],
        [2148.41412223, 1996.37326871],
        [2160.09380725, 1998.18663435],
        [2139.31881092, 1999.09331718],
        [2102.90027897, 1999.54665859],
        [2059.38873567, 1999.77332929],
        [2012.86672755, 1999.88666465],
        [1965.13916016, 1995.46306542],
        [1917.1854889 , 1974.73046789],
        [1869.64730781, 1946.07127496],
        [1822.60910211, 1913.674328  ],
        [1776.19104915, 1879.63398232],
        [1730.56561848, 1845.00107762],
    ]
)

turbine_powers_base_yaw_angles_heterogeneous = np.array(
    [
        [1663.17906022, 1715.82635006],
        [1661.87408022, 1674.73352102],
        [1694.45420923, 1678.05878102],
        [1744.79920624, 1703.97077085],
        [1804.88502549, 1741.70324262],
        [1870.7300592 , 1785.81343333],
        [1940.34124914, 1833.50592582],
        [2012.73792847, 1883.41728464],
        [2088.27152165, 1935.06406227],
        [2099.80031841, 1943.07460297],
        [2079.93709709, 1929.5132482 ],
        [2044.94476809, 1905.35583325],
        [2002.98928215, 1876.10948106],
        [1957.83996805, 1844.54680438],
        [1911.4054064 , 1811.99125939],
        [1864.90457958, 1779.19583133],
        [1818.64979731, 1746.40380111],
        [1772.84206777, 1713.89392106],
        [1727.76853787, 1681.61624573],
        [1683.33525441, 1649.77953408],
    ]
)

def test_FlorisStandin_regression_homogeneous_inflow():
    floris_standin = FlorisStandin(
        CONFIG,
        AMR_INPUT,
        AMR_EXTERNAL_DATA
    )

    test_times = np.arange(0.0, CONFIG["stoptime"], CONFIG["helics"]["deltat"])

    # Initialize storage
    turbine_powers = np.zeros((len(test_times), 2))

    # Step through the test times
    for i, t in enumerate(test_times):
        turbine_powers[i,:] = floris_standin.get_step(t)[2]

    if PRINT_VALUES:
        print("Turbine powers (base): ", turbine_powers)

    # Compare to recorded values
    assert np.allclose(turbine_powers, turbine_powers_base_homogeneous)

    # Run again with specified power setpoints
    power_setpoints = np.array([2700.0, 2000.0])
    turbine_powers = np.zeros((len(test_times), 2))
    for i, t in enumerate(test_times):
        turbine_powers[i,:] = floris_standin.get_step(t, power_setpoints=power_setpoints)[2]

    if PRINT_VALUES:
        print("Turbine powers (power_setpoints): ", turbine_powers)
    
    assert np.allclose(turbine_powers, turbine_powers_base_power_setpoints_homogeneous)


    # Run again with specified yaw angles (and remove previous power setpoints by setting high)
    yaw_angles = np.array([260.0, 250.0])
    turbine_powers = np.zeros((len(test_times), 2))
    for i, t in enumerate(test_times):
        turbine_powers[i,:] = floris_standin.get_step(
            t,
            yaw_angles=yaw_angles,
            power_setpoints=1e9 * np.ones(2)
        )[2]

    if PRINT_VALUES:
        print("Turbine powers (yaw_angles): ", turbine_powers)
    
    assert np.allclose(turbine_powers, turbine_powers_base_yaw_angles_homogeneous)


def test_FlorisStandin_regression_heterogeneous_inflow():
    floris_standin = FlorisStandin(
        CONFIG,
        AMR_INPUT,
        AMR_EXTERNAL_DATA_HET
    )

    test_times = np.arange(0.0, CONFIG["stoptime"], CONFIG["helics"]["deltat"])

    # Initialize storage
    turbine_powers = np.zeros((len(test_times), 2))

    # Step through the test times
    for i, t in enumerate(test_times):
        turbine_powers[i,:] = floris_standin.get_step(t)[2]

    if PRINT_VALUES:
        print("Turbine powers (base): ", turbine_powers)

    # Compare to recorded values
    assert np.allclose(turbine_powers, turbine_powers_base_heterogeneous)

    # Run again with specified power setpoints
    power_setpoints = np.array([2700.0, 2000.0])
    turbine_powers = np.zeros((len(test_times), 2))
    for i, t in enumerate(test_times):
        turbine_powers[i,:] = floris_standin.get_step(t, power_setpoints=power_setpoints)[2]

    if PRINT_VALUES:
        print("Turbine powers (power_setpoints): ", turbine_powers)
    
    assert np.allclose(turbine_powers, turbine_powers_base_power_setpoints_heterogeneous)


    # Run again with specified yaw angles (and remove previous power setpoints by setting high)
    yaw_angles = np.array([10.0, 20.0])
    turbine_powers = np.zeros((len(test_times), 2))
    for i, t in enumerate(test_times):
        turbine_powers[i,:] = floris_standin.get_step(
            t,
            yaw_angles=yaw_angles,
            power_setpoints=1e9 * np.ones(2)
        )[2]

    if PRINT_VALUES:
        print("Turbine powers (yaw_angles): ", turbine_powers)
    
    assert np.allclose(turbine_powers, turbine_powers_base_yaw_angles_heterogeneous)

