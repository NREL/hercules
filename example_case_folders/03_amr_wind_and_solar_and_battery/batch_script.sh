#!/bin/bash
#SBATCH --job-name=hercules
#SBATCH --time=1:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=36
#SBATCH --account=ssc
# #SBATCH --qos=high

# A lot of modules and conda stuff
source /nopt/nrel/apps/anaconda/5.3/etc/profile.d/conda.sh
module use /not/nrel/apps/modules/default/modulefiles
module purge
module load conda
export PREFIX=~/.conda-envs/hercules
export PATH=$PREFIX/bin:$PATH
export FI_PROVIDER_PATH=$PREFIX/lib/libfabric/prov
export LD_LIBRARY_PATH=$PREFIX/lib/libfabric:$PREFIX/lib/release_mt:$LD_LIBRARY_PATH
source activate hercules
module load helics/helics-3.1.0_openmpi
module load netcdf-c/4.7.3/gcc-mpi

export HELICS_PORT=32000

# Set up the helics broker
helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 

# Need to set this to your hercules folder
# cd /home/pfleming/hercules/hercules
python hercules_runscript.py hercules_input_000.yaml >> loghercules 2>&1  & # Start the controller center and pass in input file

# Now go back to scratch folder and launch the job
# cd /scratch/pfleming/c2c/example_sim_02
mpirun -n 72 /home/pfleming/amr-wind/build/amr_wind amr_input.inp >> logamr 2>&1 