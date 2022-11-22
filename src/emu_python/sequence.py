# Copyright 2022 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# An example simple sequence

import pandas as pd
import numpy as np

# Define two vectors
sim_time_s = np.arange(0,100,1.)
wind_speed_array = np.linspace(5,15,len(sim_time_s))

# Define a dataframe
df_seq = pd.DataFrame({
    'sim_time_s':sim_time_s,
    'wind_speed':wind_speed_array
})

# Show it
print(df_seq.head())