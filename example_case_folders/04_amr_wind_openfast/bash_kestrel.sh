#!/bin/bash
#SBATCH --job-name=hercules
#SBATCH --time=4:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=52
#SBATCH --account=ssc
# #SBATCH --qos=high

rm log*

module purge
export SPACK_MANAGER="/home/gstarke/spack-manager"
export MPICH_SHARED_MEM_COLL_OPT=mpi_bcast,mpi_barrier
export MPICH_COLL_OPT_OFF=mpi_allreduce
source $SPACK_MANAGER/start.sh
spack-start

quick-activate /home/gstarke/environment_amrwind_helics_2

spack load amr-wind+helics+openfast
module load anaconda3

source activate hercules2

export HELICS_PORT=32000

# Set up the helics broker
helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 

# Need to set this to your hercules folder
# cd /home/pfleming/hercules/hercules
python hercules_runscript.py hercules_input_000.yaml >> loghercules 2>&1  & # Start the controller center and pass in input file

# Now go back to scratch folder and launch the job
# cd /scratch/pfleming/c2c/example_sim_02
srun -n 104 /home/gstarke/environment_amrwind_helics_2/amr-wind/spack-build-7zmoxfz/amr_wind amr_input.inp >> logamr 2>&1 
