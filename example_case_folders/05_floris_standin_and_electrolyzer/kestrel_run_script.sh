#!/bin/bash
#SBATCH --job-name=hercules
#SBATCH --time=1:00:00
#SBATCH --nodes=1
#SBATCH --account=ssc
# #SBATCH --qos=high  # Uncomment for higher prioirty

# Kill any active helics jobs
source ../find_and_kill_helics

# Source the Conda initialization script
module purge
module load conda
conda activate hercules

    #  Versions:
    #     helics/3.1.0-cray-mpich-intel
    #     helics/3.4.0-cray-mpich-intel
    #     helics/3.4.0-gcc10.1.0-open-mpi

# Set up helics and netcdf
module load helics/3.4.0-cray-mpich-intel
# module load netcdf-c/4.9.2-openmpi-gcc

# Clean up existing outputs
if [ -d outputs ]; then rm -r outputs; fi
mkdir -p outputs

# Generate floris standin data
python ../../hercules/tools/generate_amr_standin_data.py floris_standin_data.csv

# Set the helics port to use: 
export HELICS_PORT=32000

helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 
python hercules_runscript_CLcontrol.py hercules_input_000.yaml >> outputs/loghercules_cl 2>&1 &
python floris_runscript.py amr_input.inp floris_standin_data.csv >> outputs/logfloris_cl 2>&1

# Clean up helics output if there
# Search for a file that begins with the current year
# And ends with csv
# If the file exists, move to outputs folder
current_year=$(date +"%Y")
for file in ${current_year}*.csv; do
    if [ -f "$file" ]; then
        mv "$file" outputs/
    fi
done

# If everything is successful
echo "Finished running hercules"
exit 0

