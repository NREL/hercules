#!/bin/bash

conda activate hercules

export HELICS_PORT=32000 

helics_broker -f 2 --consoleloglevel=trace --loglevel=debug --local_port=$HELICS_PORT >>loghelics &

# helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 

# cd example_case_folders/06_amr_wind_standin_and_battery 

python hercules_runscript.py hercules_input_000.yaml >> loghercules 2>&1 &

python hercules_runscript_amr_standin.py amr_input.inp amr_standin_data.csv >> logstandin 2>&1 



