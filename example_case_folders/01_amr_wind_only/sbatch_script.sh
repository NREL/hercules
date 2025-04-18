#!/bin/bash
#SBATCH --job-name=hercules
#SBATCH --time=1:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=36
#SBATCH --account=ssc
# #SBATCH --qos=high  # Uncomment for higher prioirty

# A lot of modules and conda stuff
# source /nopt/nrel/apps/anaconda/5.3/etc/profile.d/conda.sh
# module use /not/nrel/apps/modules/default/modulefiles
module purge
module load conda
# export PREFIX=~/.conda-envs/hercules
# export PATH=$PREFIX/bin:$PATH
# export FI_PROVIDER_PATH=$PREFIX/lib/libfabric/prov
# export LD_LIBRARY_PATH=$PREFIX/lib/libfabric:$PREFIX/lib/release_mt:$LD_LIBRARY_PATH
conda activate hercules
module load helics/3.4.0-gcc10.1.0-open-mpi  
module load netcdf-c/4.9.2-openmpi-gcc

export HELICS_PORT=32000

# Set up the helics broker
helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 
python hercules_runscript.py hercules_input_000.yaml >> loghercules 2>&1  & # Start the controller center and pass in input file
mpirun -n 72 /home/pfleming/amr-wind/build/amr_wind amr_input.inp >> logamr 2>&1 

