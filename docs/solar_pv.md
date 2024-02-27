# Solar PV

The `SolarPySAM` module uses [PySAM](https://nrel-pysam.readthedocs.io/en/main/overview.html) package for the National Renewable Energy Laboratory's System Advisor Model (SAM) to predict the power output of the solar PV plant. This module uses the [Detailed Photovoltaic model](https://sam.nrel.gov/photovoltaic.html) in [`pvsamv1`](https://nrel-pysam.readthedocs.io/en/main/modules/Pvsamv1.html) to calculate PV electrical output using separate module and inverter models.

### Inputs

`SolarPySAM` requires two input files:
1. A CSV file that specifies the weather conditions (e.g. NonAnnualSimulation-sample_data-interpolated-daytime.csv). This file should include: 
    - timestamp
    - direct normal irradiance (DNI)
    - diffuse horizontal irradiance (DHI)
    - global horizontal irradiance (GHI)
    - wind speed
    - air temperature (dry bulb temperature)
2.  A JSON file that specifies the PV plant system design (e.g. 100MW_1axis_pvsamv1.json).
The system location (latitude, longitude, and elevation) is specified in the input `yaml` file.

The example folder `07_amr_wind_standin_and_solar_pysam` specifies:
- weather conditions on May 10, 2018 (from [this PySAM example](https://github.com/NREL/pysam/blob/main/Examples/NonAnnualSimulation.ipynb))
- latitude, longitude, and elevation of Golden, CO
- system design information for a 100 MW single-axis PV tracking system generated using the SAM GUI
These inputs can be changed in the `.yaml`, `.json`, and `.csv` files.

### Outputs

The `SolarPySAM` module outputs the AC power (`power_mw`) and the net DC power (`dc_power_mw`) in MW of the PV plant at each timestep, as well as the angle of incidence (`aoi`).

### References
PySAM. National Renewable Energy Laboratory. Golden, CO. https://github.com/nrel/pysam