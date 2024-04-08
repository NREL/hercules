#!/bin/bash

# Ensure hercules conda or venv is activated before running this script

# Run this script via the command: 
#    bash batch_script.sh
#    ./batch_script.sh

# Set the helics port to use: 
#make sure you use the same port number in the amr_input.inp and hercules_input_000.yaml files. 
export HELICS_PORT=32000

# Delete the logs within the outputs folder (it the output folder exists)
if [ -d "outputs" ]; then
  rm -f outputs/*.log
fi

# Create the outputs folder
mkdir -p outputs

# Set up the helics broker
helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 
# For debugging add --consoleloglevel=trace

# Start the controller center and pass in input file
echo "Starting hercules"
python3 hercules_runscript.py hercules_input_000.yaml >> outputs/loghercules.log 2>&1

# Start the amr_standin
# echo "Starting amr stand-in"
# python3 hercules_runscript_amr_standin.py amr_input.inp >> outputs/logstandin.log 2>&1 &
echo "Starting floris"
python3 floris_runscript.py amr_input.inp >> outputs/logfloris.log 2>&1


# If everything is successful
echo "Finished running hercules"
exit 0



