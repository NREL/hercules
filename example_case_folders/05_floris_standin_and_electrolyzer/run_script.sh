#!/bin/bash

# Determine the base path for Conda initialization
if [ -f "/home/$USER/anaconda3/etc/profile.d/conda.sh" ]; then
    # Common path for Anaconda on Linux
    CONDA_PATH="/home/$USER/anaconda3/etc/profile.d/conda.sh"
elif [ -f "/Users/$USER/anaconda3/etc/profile.d/conda.sh" ]; then
    # Common path for Anaconda on macOS
    CONDA_PATH="/Users/$USER/anaconda3/etc/profile.d/conda.sh"
elif [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
    # Alternative system-wide installation path
    CONDA_PATH="/opt/anaconda3/etc/profile.d/conda.sh"
elif [ -f "opt/miniconda3/etc/profile.d/conda.sh" ]; then
    # Alternative system-wide installation path
    CONDA_PATH="/opt/miniconda3/etc/profile.d/conda.sh"
elif command -v conda &> /dev/null; then
    # If conda is in PATH, use the which command to find conda location
    CONDA_PATH=$(dirname "$(which conda)")/../etc/profile.d/conda.sh
else
    echo "Conda installation not found. Please ensure Conda is installed and in your PATH."
    exit 1
fi

# Source the Conda initialization script
source "$CONDA_PATH"


conda activate hercules

# Clean up existing outputs
if [ -f hercules_output_control.csv ]; then rm hercules_output_control.csv; fi
if [ -d outputs ]; then rm -r outputs; fi

# Create the outputs folder
mkdir outputs

# Generate floris standin data
python ../../hercules/tools/generate_amr_standin_data.py floris_standin_data.csv

# Set the helics port to use: 
export HELICS_PORT=32000

helics_broker -t zmq  -f 2 --loglevel="debug" --local_port=$HELICS_PORT & 
python hercules_runscript_CLcontrol.py hercules_input_000.yaml >> outputs/loghercules_cl 2>&1 &
python floris_runscript.py amr_input.inp floris_standin_data.csv >> outputs/logfloris_cl 2>&1

