source activate base
conda activate hercules

# Clean up existing outputs
if [ -f hercules_output_control.csv ]; then rm hercules_output_control.csv; fi
if [ -f outputs/log_test_client.log ]; then rm log_test_client.log; fi
if [ -f loghercules_cl ]; then rm loghercules_cl; fi
if [ -f logfloris_cl ]; then rm logfloris_cl; fi
if [ -d outputs ]; then rm -r outputs; fi

# Set the helics port to use: 
export HELICS_PORT=32000

helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 
python3 hercules_runscript_CLcontrol.py hercules_input_000.yaml >> loghercules_cl 2>&1 &
python3 floris_runscript.py amr_input.inp floris_standin_data.csv >> logfloris_cl 2>&1

