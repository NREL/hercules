#!/bin/bash
#SBATCH --job-name=emu
#SBATCH --time=4:00:00
#SBATCH --nodes=29
#SBATCH --ntasks-per-node=36
#SBATCH --account=ssc
#SBATCH --qos=high

source /nopt/nrel/apps/anaconda/5.3/etc/profile.d/conda.sh


module use /nopt/nrel/apps/modules/centos74/modulefiles
module purge
module load conda/5.3
module load intel-mpi/2018.0.3
module load helics/helics-3.1.0_openmpi

module load netcdf-c/4.7.3/gcc-mpi


# export PREFIX=~/.conda-envs/nowrdc
# export PATH=$PREFIX/bin:$PATH
# export FI_PROVIDER_PATH=$PREFIX/lib/libfabric/prov
# export LD_LIBRARY_PATH=$PREFIX/lib/libfabric:$PREFIX/lib/release_mt:$LD_LIBRARY_PATH


conda activate emupy

helics_broker -t zmq  -f 2 --loglevel="debug" & 

python control_center.py & # 

cd example_sim/
cd /scratch/pfleming/c2c/example_sim


mpirun -n 1024 /home/pfleming/amr-wind/build/amr_wind emu_run_004.inp >> logamr 

