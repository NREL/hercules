#!/bin/bash
#SBATCH --job-name=emu
#SBATCH --partition=standard
#SBATCH --time=48:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=36
#SBATCH --account=seas


module load helics/helics-3.1.0_openmpi
module load conda
module load netcdf-c/4.7.3/gcc-mpi


conda activate /projects/aumc/dvaidhyn/aumcuc/auc

cd /projects/aumc/dvaidhyn/transmissionemulator/dev/emu_python/emu_python/


helics_broker -t zmq  -f 2 --loglevel="debug" & 

python control_center.py & 


cd runamr004/

mpirun -n 64 /projects/aumc/dvaidhyn/transmissionemulator/dev/amr-wind/build/amr_wind input_restart.i >> logamr 




