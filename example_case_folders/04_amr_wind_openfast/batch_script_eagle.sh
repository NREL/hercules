#!/bin/bash
#SBATCH --job-name=hercules
#SBATCH --time=4:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=36
#SBATCH --account=ssc
# #SBATCH --qos=high

rm log*

module purge
export SPACK_MANAGER="/home/jfrederi/projects/spack-manager"
source $SPACK_MANAGER/start.sh
spack-start

quick-activate /home/jfrederi/projects/environment_hercules

spack load amr-wind+helics+openfast
module load anaconda3

source activate hercules

export OMP_PROC_BIND=spread
export KMP_AFFINITY=balanced

export HELICS_PORT=32000

# Set up the helics broker
helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 

# Need to set this to your hercules folder
# cd /home/pfleming/hercules/hercules
python hercules_runscript.py hercules_input_000.yaml >> loghercules 2>&1  & # Start the controller center and pass in input file

# Now go back to scratch folder and launch the job
# cd /scratch/pfleming/c2c/example_sim_02
mpirun -n 72 /home/jfrederi/projects/environment_hercules/amr-wind/spack-build-sg3hqfg/amr_wind amr_input.inp >> logamr 2>&1 
