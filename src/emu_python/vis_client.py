from turtle import bgcolor, color
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as ncdf
import time
import datetime
import sys
import os
import shutil
# import pickle
import pandas as pd

import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)

# Demonstrate reading netcdf file within a loop
# Note, need a demo netcdf file copied into this foldecd r, 
# to big too commit to repo

# Parameters (LOCAL COMPUTER)
amr_wind_folder = 'local_amr_wind_demo' # Local demo version
amr_wind_folder = '/scratch/pfleming/c2c/amr_wind_demo/post_processing' # Or give actual amr wind folder

slice_file_name = 'sampling00000.nc'


# PARAMETERS
slice_file_amr_wind = os.path.join(amr_wind_folder,slice_file_name)
slice_file_copy = slice_file_name

# samplerName = 'z_plane'
samplerName = 'p_hub'



first_time_netcdf = True
timestep = 1 # time in s for the loop to hold to
slice_fig_folder = 'slices'
slice_for_dash = 'slice.png'

# Set the z-index
# In the current example there are 1/4 horizontal planes confirm
# We only plan to have one but for now this is necessary
z_index = 0 #Take this one for now

# Declare some colors
cmap_velocity = plt.get_cmap('RdBu_r')
cmap_theta = plt.get_cmap('bone')

# Set up the logger
# Useful for when running on eagle
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    filename='log_netcdf.log',
                    filemode='w')
logger = logging.getLogger('log_netcdf')

# Declare an image folder
if not os.path.exists(slice_fig_folder):
    os.makedirs(slice_fig_folder)

# Perhaps a small hack to also send log to the terminal output 
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# timestamp
current_timestamp = datetime.datetime.now()

# Last time the netcdf file has been modified
last_netcdf_mod_time = os.path.getmtime(slice_file_amr_wind) - 1 # Force the first read

step = 0

while True:

    logging.info("------- Loop Start (%d) -----------" % step)

    # Before continuing make sure timestep s has passed since last pass
    while datetime.datetime.now() < current_timestamp + datetime.timedelta(seconds=timestep):
        time.sleep(0.05)

    # Log the current time step
    current_timestamp = datetime.datetime.now()

    # In the real case, the file might not initialy exist so lets do something like this
    if not os.path.exists(slice_file_amr_wind):
        logging.info("NetCdf file not yet created")
        continue

    # Check if the netcdf file has been modified since the last read
    if os.path.getmtime(slice_file_amr_wind) <= last_netcdf_mod_time:
        logging.info("NetCdf file not recently modded")
        continue

    # Log the time as most recent mod
    last_netcdf_mod_time = os.path.getmtime(slice_file_amr_wind)

    # Copy the netcdf file
    logging.info("Copying the netcdf file")
    if os.path.exists(slice_file_copy):
        os.remove(slice_file_copy)
    shutil.copyfile(slice_file_amr_wind, slice_file_copy)

    # Read the netcdf data
    logging.info("Reading netcdf data")
    netcdf_data = ncdf.Dataset(slice_file_copy, 'r')

    # Extract time and say what is the most recent time step
    # With a static file this will not update, but in our version it will
    netcdf_time = netcdf_data.variables['time']
    netcdf_max_time = np.max(netcdf_time)
    logging.info("Most recent simulation time in netcdf: %.1f" % netcdf_max_time)

    # If this is the first time, need to get x,y,z, after that can reuse
    if first_time_netcdf:
        # Extract the coordinates.
        x = netcdf_data[samplerName]['coordinates'][:,0]
        y = netcdf_data[samplerName]['coordinates'][:,1]
        z = netcdf_data[samplerName]['coordinates'][:,2]

        # Get the shape of the plane.
        plane_shape = (netcdf_data[samplerName].ijk_dims[2], netcdf_data[samplerName].ijk_dims[0], netcdf_data[samplerName].ijk_dims[1])

        # Reshape the data to have the same dimensions as the planes
        x = x.reshape(plane_shape)
        y = y.reshape(plane_shape)
        z = z.reshape(plane_shape)

        # Get the data in plane
        x_plane = x[z_index,:,:].flatten()
        y_plane = y[z_index,:,:].flatten()

        # Mark we've done this already
        first_time_netcdf = False


    # Get latest u,v,w
    u = netcdf_data[samplerName]['velocityx'][-1] # Take the most recent value
    v = netcdf_data[samplerName]['velocityy'][-1]
    # w = netcdf_data[samplerName]['velocityz'][-1] # not currently using
    # theta = data[samplerName]['temperature'][-1] # not currently using

    # Reshape
    u = u.reshape(plane_shape)
    v = v.reshape(plane_shape)
    # w = w.reshape(plane_shape) # not currently using
    # theta = theta.reshape(plane_shape) # not currently using
    uh = np.sqrt(np.square(u) + np.square(v))
    # uh = u # hack to x velocity
    
    
    # uh_plane = u[z_index,:,:].flatten()
    uh_plane = uh[z_index,:,:].flatten()

    # # plot the velocity
    fig, ax = plt.subplots()
    p1 = ax.pcolormesh(x[z_index,:,:], y[z_index,:,:], uh[z_index,:,:], cmap=cmap_velocity, shading='nearest')
    # # c1 = plt.colorbar(p1,ax=ax1) # if we want color bar
    # # c1.set_label(r'$u_h$ (m/s)') # if we want color bar

    # # Make equal axis
    ax.set_aspect("equal")

    # Remove ticks
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Add some text
    ax.text(x[z_index,:,:].min(), y[z_index,:,:].max(),"Time step = %d, Step = %d" % (netcdf_max_time, step),color='k',backgroundcolor='w',verticalalignment='top')

    # # Add a title
    # ax.set_title("Time step = %d" % netcdf_max_time)

    # Save the figure (twice, once local and once into the dir)
    # fig.savefig(os.path.join(slice_fig_folder, 'fig_%04d.png' % step), transparent=True,dpi=200)


    # Save the underlying data
    df_flow = pd.DataFrame({
        'x':x_plane,
        'y':y_plane,
        'uh':uh_plane
    })
    df_flow = df_flow.set_index(['y','x']).unstack()
    df_flow.columns = [c[1] for c in df_flow.columns]
    df_flow.to_pickle('df_flow.p')
    # pickle.dump([x_plane, y_plane,uh_plane],open('flow_data.p','wb'))

    step = step + 1



plt.show()