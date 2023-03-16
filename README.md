# Initial README

# emu_python
Python (python >=3.6) front-end to emulator

# Recommended install
set up emupy (eum_python) conda environment and pip install me into it
OR
use pyenv

# New recommended install to work with era 5
conda create --name emupy python=3.8
conda activate emupy
git clone https://github.com/NREL/OpenOA.git
pip install ./OpenOA
pip install -e emu_python

# Please install SEAS as follows: 

``` pip install git+https://github.nrel.gov/SEAS/SEAS.git@dv/emuwind ```

Note from PF:
Had trouble doing it this way on local machine so instead:
# (Activate conda environment first)
git clone git@github.nrel.gov:SEAS/SEAS.git
cd SEAS
git fetch --all
git checkout dv/emuwind
cd ..
pip install -e SEAS

# Other steps for era 5
Now need to add a file called APIKEY which contains the API Key you'll find in your data.planetos account

The instructions said to place it in the folder
OpenOA/operational_analysis/toolkits

But I found I also had to copy it down to here:
/Users/pfleming/opt/anaconda3/envs/emupy/lib/python3.8/site-packages/operational_analysis/toolkits/

Col

# Running [Local]

In 4 different terminals with location set to emu_python/, type the following commands
(This is more and more out of date)

- Terminal 1: `python control_center.py`
- Terminal 2: `python testclient.py`
- Terminal 3: `python vis_client.py`
- Terminal 4: `python front_end_dash.py`

# Running [Eagle]

### Setting up AMR-WIND

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
    emu_go

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

# Order of operations

### Initialization

1. Instantiate the py_sim modules, which sets the intial conditions

2. Run get_outputs, which sets the initial outputs
    
3. Establish the helics connection to AMRwind (?)


### Main run: for $k = 0, 1, 2, 3, \dots$

1. Compute control actions in controller, [i.e. $u_k = h(y_k, d_k)$]

2. Record all signals for time step $k$.

3. Update state in py_sim [$x_{k+1} = f(x_k, u_k, d_k)$] and output in py_sim [$y_{k+1} = g(x_{k+1})$]

4. Update state and output in helics/AMRwind, possibly using components from py_sim (TODO: what ordering should be used there?)
    [$x_{k+1} = f(x_k, u_k, d_k)$, $y_{k+1} = g(x_{k+1})$]

<!--5. Time step code [$x_{k} \leftarrow x_{k+1}$, $y_k \leftarrow y_{k+1}$]-->
### Postprocessing

1. Write outputs to files
 
2. Shut down communication?



# TODO
1. include dash license and copyright
2.  make connection objects more robust
3.  install SEAS as part of emu_python install

# Questions

1. what if the speed/dir don't change: still need to send them to receive data?
1. 
