# Copyright 2022 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# This file reads public data from NWTC site
# Files are 1 minute averages and the website updates every 1 minute

"""
Useful info about web data
The MIDC raw data API allows for automated extraction of daily data sets from any MIDC station. Extracted data is equivalent to data retrieved using the All Raw Data option from the MIDC daily data web interface, however URL structure has been simplified for API use.

Usage:

Public/External Use:    https://midcdmz.nrel.gov/apps/data_api.pl?site=SSSSSSSS&begin=YYYYMMDD&end=YYYYMMDD
NREL Internal Only:     http://midc.nrel.gov/apps/data_api.pl?site=SSSSSSSS&begin=YYYYMMDD&end=YYYYMMDD

Parameter   Value   Notes
site    SSSSSSSS (Station Identifier)   Required, identifiers are listed in table below with example link (in Station ID column) for most recent day
begin   4-digit year (YYYY), 2-digit month (MM), 2-digit day (DD) for date to begin extraction  Optional, most recent day returned if not included
end 4-digit year (YYYY), 2-digit month (MM), 2-digit day (DD) for date to end extraction    Optional, one day returned if not included

"""


import numpy as np
import pandas as pd

import logging
import sys


# Set up the logger
# Useful for when running on eagle
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    filename='nwtc.log',
                    filemode='w')
logger = logging.getLogger("nwtc")

# Perhaps a small hack to also send log to the terminal outout 
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# Parameter

# Website info
# INTERNAL VERSION
website_root = "http://midc.nrel.gov/apps/data_api.pl?site=NWTC"
# PUBLIC VERSION
# website_root = "https://midcdmz.nrel.gov/apps/data_api.pl?site=NWTC"

def get_latest_wind_data():
    """ Access the M2 Tower latest data and return wind_dir and wind_speed """

    # Read data directly into pandas
    df_nwtc = pd.read_csv(website_root)

    # Make a new timestamp column
    # Signals given are the year, day of year, MST (hour/minute code)
    df_nwtc['minute'] = df_nwtc['MST'] % 100 # Minute are last two digits
    df_nwtc['hour']  = np.floor(df_nwtc['MST'] / 100.) # hours are first two digits
    df_nwtc['timestamp_mst'] = pd.to_datetime(df_nwtc['Year'] * 10000000 + df_nwtc['DOY'] * 10000 + df_nwtc['hour']*100 + df_nwtc['minute'], format='%Y%j%H%M')

    # Grab the most recent values
    local_time = df_nwtc['timestamp_mst'].values[-1]
    wind_speed = df_nwtc['Avg Wind Speed @ 80m [m/s]'].values[-1]
    turbulence_intensity = df_nwtc['Turbulence Intensity @ 80m'].values[-1]
    wind_direction = df_nwtc['Avg Wind Direction @ 80m [deg]'].values[-1]
    irradiance = df_nwtc['Direct Normal [W/m^2]'].values[-1]

    #logger.info("NWTC data grab {}, {}, {}, {}, {}".format(local_time, wind_speed, turbulence_intensity, wind_direction, irradiance))
    # print(local_time, wind_speed, turbulence_intensity, wind_direction, irradiance)
    logger.info("NWTC wind speed: {}, direction: {}".format(wind_speed, wind_direction))
    return wind_speed, wind_direction

