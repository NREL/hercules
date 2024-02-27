# Local installation instructions


# Installation
Create a new conda environment for hercules:
```
conda create --name hercules python=3.11
conda activate hercules
```

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


SEAS is also required for hercules. To install 
SEAS, use

``` pip install https://github.com/NREL/SEAS/blob/main/SEAS.tar.gz?raw=true ```

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

NREL's PySAM software is also required for hercules. To install, use 
```
pip install nrel-pysam==4.2.0
```

You may also want to run the FLORIS standin for AMR-Wind for a steady-state representation 
of wind farm flows. In this case, run
```
pip install git+https://github.com/NREL/floris.git@v4
```
to get the correct branch of FLORIS installed.

If you run hercules and get an error that `pyyaml` is missing, you may also need to install it using
```
conda install -c conda-forge pyyaml
```

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
<!--
# Other steps for era 5
Now need to add a file called APIKEY which contains the API Key you'll find in your data.planetos account

The instructions said to place it in the folder
OpenOA/operational_analysis/toolkits

But I found I also had to copy it down to here:
/Users/pfleming/opt/anaconda3/envs/hercules/lib/python3.8/site-packages/operational_analysis/toolkits/

Col
-->

# Running [Local]

To run locally using a standin for AMR-Wind, launch 3 separate 
terminals. In each, `conda activate` your hercules environment (`conda 
activate hercules`). 

In the first terminal, run
```
helics_broker -f 2 --consoleloglevel=trace --loglevel=debug --local_port=$HELICS_PORT &
```
from any directory.

In the second and third terminals, navigate to 
hercules/example_case_folders/example_sim_05 (you'll need to be on the 
develop branch of hercules). Then, in one of these 
terminals, run 
```
python hercules_runscript_dummy_amr.py amr_input.inp
```
and in the other, run
```
python hercules_runscript.py hercules_input_000.yaml
```

The first of these launches the dummy stand-in for AMR-wind, and the second 
launches the hercules emulator. These will connect to the helics_broker and 
run the co-simulation. You should see printout from both the dummy AMR-wind 
process and the hercules emulator printed to your screen.


Alternatively, the bash files in each example are set up to be run from the terminal using 
```
./bash_script.sh
```
However, if the simulation hangs, be sure to check if there are multiple processes running with 
```
ps
```
which will tell you all of the processes currently working.  You can kill processes that you do not want by using the kill command, paired with the process ID (filled into the blank in the command below).
```
kill <PID>
```

<!--
In 4 different terminals with location set to hercules/, type the following commands
(This is more and more out of date)

- Terminal 1: `python control_center.py`
- Terminal 2: `python testclient.py`
- Terminal 3: `python vis_client.py`
- Terminal 4: `python front_end_dash.py`
-->

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