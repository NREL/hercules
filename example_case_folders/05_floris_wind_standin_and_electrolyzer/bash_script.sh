# Example bash for running things locally
# I just run these one at a t time

# A lot of modules and conda stuff
conda activate hercules

# Delete old log files
rm hercules_output_control.csv log_test_client.log loghercules_cl logfloris_cl

# Set the helics port to use: 
export HELICS_PORT=32000

#make sure you use the same port number in the amr_input.inp and hercules_input_000.yaml files. 
# Set up the helics broker

helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 
python3 hercules_runscript_CLcontrol.py hercules_input_000.yaml >> loghercules_cl 2>&1 &
python3 floris_runscript.py amr_input.inp amr_standin_data-higher.csv >> logfloris_cl 2>&1

