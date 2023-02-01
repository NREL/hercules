import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as ncdf
import time
import sys
import os

import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)

# Demonstrate reading netcdf file within a loop
# Note, need a demo netcdf file copied into this folder, 
# to big too commit to repo

# Parameters
slice_file = 'sampling00000.nc'
samplerName = 'z_plane'
first_time_netcdf = True

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

# Perhaps a small hack to also send log to the terminal output 
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

for i in range(10): # just loop 10 times in this case

    # In the real case, the file might not initialy exist so lets do something like this
    if not os.path.exists(slice_file):
        logging.info("NetCdf file not yet created")

    else: # If the file does exists can do the operations
        # Read the netcdf data
        logging.info("Reading netcdf data")
        netcdf_data = ncdf.Dataset(slice_file, 'r')

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

            # Mark we've done this already
            first_time_netcdf = False

            # Get the z-index
            # In the current example there are 4 horizontal planes
            # We only plan to have one but for now this is necessary
            z_index = 0 #Take this one for now

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

        # print(x[z_index,:,:])

        # # plot the velocity
        fig, ax = plt.subplots()
        p1 = ax.pcolormesh(x[z_index,:,:], y[z_index,:,:], uh[z_index,:,:], cmap=cmap_velocity, shading='nearest')
        # # c1 = plt.colorbar(p1,ax=ax1) # if we want color bar
        # # c1.set_label(r'$u_h$ (m/s)') # if we want color bar

        # # Make equal axis
        # ax.set_aspect("equal")

        # # Add a title
        # ax.set_title("Time step = %d" % netcdf_max_time)

        break

plt.show()