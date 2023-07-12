# Example bash for running things locally
# I just run these one at a t time

# A lot of modules and conda stuff
conda activate emupy

# Set the helics port to use: 
export HELICS_PORT=23405

#make sure you use the same port number in the amr_input.inp and emu_input_000.yaml files. 

# Set up the helics broker
helics_broker -f 2 --consoleloglevel=trace --loglevel=debug --local_port=$HELICS_PORT &

# Need to set this to your hercules folder
# cd /home/pfleming/hercules/hercules
python3 emu_runscript.py emu_input_000.yaml >> logemu 2>&1 & # Start the controller center and pass in input file


python3 emu_runscript_dummy_amr.py amr_input.inp >> logdummy 2>&1
# Now go back to scratch folder and launch the job

# cd /scratch/pfleming/c2c/example_sim_02
# mpirun -n 72 /home/pfleming/amr-wind/build/amr_wind amr_input.inp >> logamr 
