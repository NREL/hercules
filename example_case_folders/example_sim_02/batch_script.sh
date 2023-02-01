#!/bin/bash
#SBATCH --job-name=emu
#SBATCH --time=4:00:00
#SBATCH --nodes=29
#SBATCH --ntasks-per-node=36
#SBATCH --account=ssc
# UNCOMMENT IF WANT HIGH PRIORITY #SBATCH --qos=high

# A lot of modules and conda stuff
source /nopt/nrel/apps/anaconda/5.3/etc/profile.d/conda.sh
module use /nopt/nrel/apps/modules/centos74/modulefiles
module purge
module load conda/5.3
module load intel-mpi/2018.0.3
module load helics/helics-3.1.0_openmpi
module load netcdf-c/4.7.3/gcc-mpi
conda activate emupy

# Set up the helics broker
helics_broker -t zmq  -f 2 --loglevel="debug" & 

# Need to set this to your emu_python folder
cd /home/pfleming/emu_python/emu_python
python control_center.py & # Start the controller center

# Now go back to scratch folder and launch the job
cd /scratch/pfleming/c2c/example_sim_02
mpirun -n 1024 /home/pfleming/amr-wind/build/amr_wind emu_run_005.inp >> logamr 