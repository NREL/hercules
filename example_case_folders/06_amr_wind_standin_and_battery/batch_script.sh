#!/bin/bash

# Ensure hercules conda or venv is activated before running this script

# Run this script via the command: 
#    bash batch_script.sh
#    source batch_script.sh
#    ./batch_script.sh

# Generate the stand-in data uses a script within hercules/tools
echo "Generating stand-in data"
cd ../../

# Make a temp folder to hold the outputs
mkdir -p outputs
python hercules/tools/generate_amr_standin_data.py

# Delete the temp output folder
rm -r outputs/

# Go back to the 06 directory
cd example_case_folders/06_amr_wind_standin_and_battery
echo "Finished generating stand-in data"

# Set the helics port to use
#make sure you use the same port number in the amr_input.inp and hercules_input_000.yaml files
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

# Start the amr_standin
echo "Starting amr stand-in"
python hercules_runscript_amr_standin.py amr_input.inp amr_standin_data.csv >> outputs/logstandin.log 2>&1 &

# Start the controller center and pass in input file
echo "Starting hercules"
python hercules_runscript.py hercules_input_000.yaml >> outputs/loghercules.log 2>&1

# If everything is successful
echo "Finished running hercules"
exit 0