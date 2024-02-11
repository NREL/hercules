# Example bash for running things locally
# I just run these one at a t time

# A lot of modules and conda stuff
conda activate hercules

# Delete old log files
rm hercules_output.csv log_test_client.log loghercules logfloris

# Set the helics port to use: 
export HELICS_PORT=32000

#make sure you use the same port number in the amr_input.inp and hercules_input_000.yaml files. 
# Set up the helics broker
helics_broker -f 2 --consoleloglevel=trace --loglevel=debug --local_port=$HELICS_PORT &

# Need to set this to your hercules folder
# cd /home/pfleming/hercules/hercules
python3 hercules_runscript.py hercules_input_000.yaml >> loghercules 2>&1 & # Start the controller center and pass in input file


python3 floris_runscript.py amr_input.inp >> logfloris 2>&1

