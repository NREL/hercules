# Copyright 2022 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# Demonstrate how to get 1 day of data from a particular lat/lon
# Using OpenOA/ERA5 toolkit

""""
Some reference material
https://github.com/NREL/OpenOA/blob/10b94083669f1f9f833b446faf535bec049cd1ed/operational_analysis/toolkits/reanalysis_downloading.py#L276

On ERA 5 data set
https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5
Quality-assured monthly updates of ERA5 (1979 to present) are published within 3 months of real time. Preliminary daily updates of the dataset are available to users within 5 days of real time.
"""



import numpy as np
import pandas as pd

import logging
import sys

# import operational_analysis
from operational_analysis.toolkits import reanalysis_downloading as rd



# Set up the logger
# Useful for when running on eagle
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    filename='openoa.log',
                    filemode='w')
logger = logging.getLogger("openoa")

# Perhaps a small hack to also send log to the terminal outout 
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# # Parameters
# Use wind site lat/long
# Possible locations (dictionary of lat/lons)
location_dict = {}
location_dict['nwtc'] = [39.913983392103724, -105.216498756354]
location_dict['lower_nrel'] = [39.74075233380317, -105.17441789623074]
location_dict['fairbanks_ak'] = [64.8346263574352, -147.72427842852724]
location_dict['los_angeles_ca'] = [34.03495715051263, -118.28129769272738]
location_dict['florence_sc'] = [34.18470458138022, -79.78721899451124]
location_dict['lincoln_ne'] = [40.82761101917516, -96.69038655801518]
location_dict['cohoes_ny'] = [42.77827885367245, -73.7179724561432]

# Pick a lat lon
lat, lon = location_dict['lower_nrel']

# Make up a start stop to be about one day?
start_time = pd.to_datetime('2019-07-29 00:00:00')
end_time = pd.to_datetime('2019-07-30 00:00:00')
logger.info("ERA5 Get Data {}, {}, {}, {}".format(lat, lon, start_time, end_time))

df_era5 = rd.download_reanalysis_data_planetos('era5', lat, lon, start_time, end_time, calc_derived_vars=True)

print(df_era5)
