#!/bin/bash

# Example bash for running things locally
# I just run these one at a t time

# A lot of modules and conda stuff
conda activate hercules

# Set the helics port to use: 
export HELICS_PORT=32000

#make sure you use the same port number in the amr_input.inp and hercules_input_000.yaml files. 

# Set up the helics broker
helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 


python3 hercules_runscript.py hercules_input_000.yaml >> loghercules 2>&1 & # Start the controller center and pass in input file


python3 hercules_runscript_dummy_amr.py amr_input.inp >> logdummy 2>&1


