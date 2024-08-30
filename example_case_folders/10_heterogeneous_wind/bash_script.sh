# Example bash for running things locally
# I just run these one at a t time

# A lot of modules and conda stuff
conda activate hercules

# Set the helics port to use: 
export HELICS_PORT=32000

#make sure you use the same port number in the amr_input.inp and hercules_input_000.yaml files. 

# Remove any existing outputs/ folder
if [ -d "outputs" ]; then
  rm -f outputs/*.log
fi

# Create the outputs/ folder
mkdir -p outputs

# Wait for the open-loop control simulation to finish and then run the closed-loop simulation
helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 
python3 hercules_runscript_CLcontrol.py hercules_input_000.yaml >> outputs/hercules.log 2>&1 &
python3 floris_runscript.py amr_input.inp floris_standin_data.csv >> outputs/floris.log 2>&1
