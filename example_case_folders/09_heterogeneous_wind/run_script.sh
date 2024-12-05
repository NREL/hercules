#!/bin/bash

# Locate the scripts folder
SCRIPTS_DIR="../../scripts"

# Kill any active helics jobs by calling the find_and_kill_helics script
# within the scripts folder
source $SCRIPTS_DIR/find_and_kill_helics.sh

# Run the activate CONDA script within the scripts folder
# to ensure the Hercules environment is active
source $SCRIPTS_DIR/activate_conda.sh

# Identify an available port for the HELICS broker.  This should
# be the first in a sequence of 10 available ports
source $SCRIPTS_DIR/get_helics_port.sh

# Clean up existing outputs
if [ -d outputs ]; then rm -r outputs; fi
mkdir -p outputs

# # Set the helics port to use: 
# #make sure you use the same port number in the amr_input.inp and hercules_input_000.yaml files. 
# export HELICS_PORT=32010

# # Wait for the open-loop control simulation to finish and then run the closed-loop simulation
# helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 
# python hercules_runscript_CLcontrol.py hercules_input_000.yaml >> outputs/loghercules.log 2>&1 &
# python floris_runscript.py inputs/amr_input.inp inputs/floris_standin_data.csv >> outputs/logfloris.log 2>&1

# # Clean up helics output if there
# # Search for a file that begins with the current year
# # And ends with csv
# # If the file exists, move to outputs folder
# current_year=$(date +"%Y")
# for file in ${current_year}*.csv; do
#     if [ -f "$file" ]; then
#         mv "$file" outputs/
#     fi
# done

# # If everything is successful
# echo "Finished running hercules"
# exit 0
