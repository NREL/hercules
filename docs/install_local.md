# Local installation instructions


# Installation

## Conda environment

Create a new conda environment for hercules:
```
conda create --name hercules python=3.11
conda activate hercules
```

## Hercules

If you haven't already cloned hercules:
```
git clone https://github.com/NREL/hercules
```
Then,
```
pip install -e hercules
```
Possibly, `cd` into hercules and switch to the 
develop branch.

## SEAS, Electrolyzer, PySAM, and WHOC

### SEAS

SEAS is also required for hercules. To install 
SEAS, use

``` pip install https://github.com/NREL/SEAS/blob/v1/SEAS.tar.gz?raw=true ```

If this fails, the following may work instead (but you need permissions):


```
git clone https://github.nrel.gov/SEAS/SEAS
cd SEAS
git fetch --all
git switch dv/emuwind
```
Older versions of git (e.g. the one on Eagle) don't have the `switch` feature; instead, use 
```
git checkout dv/emuwind
```
Then,
```
cd ..
pip install -e SEAS
```

### Electrolyzer

A python electrolyzer model is also required for hercules. To install 
the electrolyzer, use

```
git clone git@github.com:NREL/electrolyzer.git
cd electrolyzer
git fetch --all
git switch develop
```
Older versions of git (e.g. the one on Eagle) don't have the `switch` feature; instead, use 
```
git checkout develop
```
Then,
```
cd ..
pip install -e electrolyzer
```
### PyYAML

If you run hercules and get an error that `pyyaml` is missing, you may also need to install it using
```
conda install -c conda-forge pyyaml
```

### WHOC

NREL's Wind Hybrid Open Controller (WHOC) software is used to implement controllers in the Hercules platform. This package is not essential to run Hercules by itself, but is needed to implement any controls in the platform. Example 06 has an example of how this is used to control a battery based on wind farm power output.

To install:
Go back to herc_root

```
git clone git@github.com:NREL/wind-hybrid-open-controller.git
cd wind-hybrid-open-controller
git fetch --all
pip install -e .
```
Note: if you want the newest updates to the WHOC repository, you can checkout the develop branch instead of the main branch.


# Running [Local]

## Using the run scripts

The simplest way to run hercules is to use the provided run scripts via:
```
bash run_script.sh
```

## Running manually

To run locally without the included runscript using a standin for AMR-Wind, launch 3 separate 
terminals. These three terminals will be used to execute one of each of the three main run command lines in the run_script.sh file.

In each, `conda activate` your hercules environment (`conda 
activate hercules`). 

In the first terminal, run the helics launch command below, which does not change between runs:
```
helics_broker -f 2 --consoleloglevel=trace --loglevel=debug --local_port=$HELICS_PORT &
```
from any directory.

In the second terminal, navigate to the run directory and run the Hercules launch command. This comand will be different based on which wind simulator you are using, but has the form:

```
python <Hercules emulator python launch script>.py <Hercules input file>.inp $HELICS_PORT >> outputs/<Hercules log file>.log 2>&1
```
An example of this is the following, which uses the floris standin model:
```
python hercules_runscript_CLcontrol.py hercules_input_000.yaml $HELICS_PORT >> outputs/loghercules_cl.log 2>&1 &
```

In the third terminal, navigate to the run directory and run the wind simulator launch command. This command will be different based on which wind simulator you are using, but has the form:

```
python <wind simulator python launch script>.py <wind farm input file>.inp <wind input data file>.csv $HELICS_PORT >> outputs/<wind log file>.log 2>&1
```
An example of this is the following, which uses the floris standin model:
```
python floris_runscript.py amr_input.inp floris_standin_data.csv $HELICS_PORT >> outputs/logfloris_cl.log 2>&1
```

These will connect to the helics_broker and 
run the co-simulation. You should see printout from both the wind simulator and the hercules emulator printed to your screen.


However, if the simulation hangs, be sure to check if there are multiple processes running with 
```
ps
```
which will tell you all of the processes currently working.  You can kill processes that you do not want by using the kill command, paired with the process ID (filled into the blank in the command below).
```
kill <PID>
```


# Running [Kestrel]

Running hercules in full requires installing AMR-Wind (likely on Kestrel/HPC).
The steps are detailed in section **HPC Installation**.
<!--

below, and assume that you have already installed 
the other parts of hercules as described above under **Installation**. 
-->


<!--
```bash
    # After connecting to eagle, reconnect or start a new screen (helpful for disconnects)
    # To detach later while keeping session: ctrl+a d
    screen -r emulator # If already exists, otherwise: screen -S emulator

    # Next request nodes, in my case I use a saved alias from Matt C
    interactive_4node_high # Requesting 4 nodes

    # When you have the interactive node, note the name of the node in the command line, 
    # You will need this, it will be something like rXXXnXX or something

    # Once these are granted can run AMRWind, first need to call the setup function
    # Defined in your .bashrc or .bash_profile:
    # amr_env_emulator <- what I used to do
    module purge
    module load helics
    --or--
    module load helics/helics-3.1.0_openmpi
    
    module load netcdf-c/4.7.3/gcc-mpi

    # Go to the AMR-Wind case folder
    cd test_folder

    # When ready to run AMR wind, something like:
    # srun -n 144 amr_wind input.i # Where 144 comes from nodes=4 * 36
    mpirun -n 1 ~/c2c/amr-wind/build/amr_wind input.i
    --or--
    mpirun -n 1 /projects/aumc/mbrazell/amr-wind/build4/amr_wind input.i
    
```

### Setting up tunnel for serving the front end
```bash
    # Use the name of the node in the command, run locally from your machine
    # In a new terminal
    ssh -L 8050:rXXXnXX:8050 el1.hpc.nrel.gov
```

### Running the python codes
```bash
    # Will now need 4 additional terminals logged into eagle, in each case:

    # ssh all 4 into the same node
    ssh rXXXnXX

    # Probably you then need to setup your conda environment, in my case 
    # I call a function saved to my profile
    hercules_go

    # Launch the helics broker
    helics_broker -f 2

    # Finally launch one of these in each terminal
    python control_center.py
    # OR #
    python vis_client.py
    # OR #
    python front_end_dash.py
```

### Final setps
```bash
    # If not already running, run amr_wind

    # The terminal running front_end_dash.py will show a web address
    # Enter that address into a web browser on your local machine
```
-->