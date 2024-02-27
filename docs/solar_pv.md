# Solar PV

### Overview

The `SolarPySAM` module uses [PySAM](https://nrel-pysam.readthedocs.io/en/main/overview.html) package for the National Renewable Energy Laboratory's System Advisor Model (SAM) to predict the power output of the solar PV plant.

This module requires two input files:
1. A CSV file that specifies the weather conditions (e.g. NonAnnualSimulation-sample_data-interpolated-daytime.csv)
2.  A JSON file that specifies the PV plant system design (e.g. 100MW_1axis_pvsamv1.json).
The system location (latitude, longitude, and elevation) is specified in the input `yaml` file.

Specifically, we use [`pvsamv1`](https://nrel-pysam.readthedocs.io/en/main/modules/Pvsamv1.html) to specify the system design (i.e. location, size, configuration).

### Example Files Description


