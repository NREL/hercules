# README

# hercules
Hybrid Energy and Control Using Large Eddy Simulations

# Documentation

For detailed instructions see the [online documentation](https://nrel.github.io/hercules/intro.html)

# Installation
Create a new conda environment for hercules:
```
conda create --name hercules python
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

``` pip install git+https://github.nrel.gov/SEAS/SEAS.git@dv/emuwind ```

If this fails, the following may work instead:


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

To run locally using a dummy placeholder for AMR-Wind, launch 3 separate 
terminals. In each, `conda activate` your hercules environment (`conda 
activate hercules`). 

In the first terminal, run
```
helics_broker -t zmq  -f 2 --loglevel="debug"
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

<!--
In 4 different terminals with location set to hercules/, type the following commands
(This is more and more out of date)

- Terminal 1: `python control_center.py`
- Terminal 2: `python testclient.py`
- Terminal 3: `python vis_client.py`
- Terminal 4: `python front_end_dash.py`
-->

# Running [Eagle]

Running hercules in full requires installing AMR-Wind (likely on eagle/HPC).
The steps are detailed below, and assume that you have already installed 
the other parts of hercules as described above under **Installation**. 

### Setting up AMR-WIND 

First, `deactive` your conda environment using 
```
conda deactivate
```

Then, clone AMR-Wind and install its required submodules. This can be done 
using

EITHER
```
git clone https://github.com/Exawind/amr-wind
cd amr-wind
git submodule update --init
cd ..
``` 
OR
``` 
git clone --recursive https://github.com/Exawind/amr-wind
```

Now, create a new directory `build` within the main AMR-Wind repository
```
mkdir amr-wind/build
```
and copy amr-wind_buildme.sh from hercules into it, naming the copied file 
buildme.sh
```
cp hercules/amr-wind_buildme.sh amr-wind/build/buildme.sh
```

`cd` into the build directory, set executable permissions for buildme.sh, and
run buildme.sh
```
cd amrwind/build
chmod +x buildme.sh
./buildme.sh
```

This will begin compiling an AMR-Wind executable. The process could take 
several minutes, during which progress updates will print to the terminal. 
Once complete, the build directory will contain an executable named amr_wind.

### Running a job

For an example of running hercules with AMR-Wind, `cd` to 
hercules/example_case_folders/example_sim_06/. 

Change the line beginning `mpirun` to point to your compiled amr-wind 
executable. This will appear something like:
```
mpirun -n 72 /path/to/amr-wind/build/amr_wind amr_input.inp >> logamr 2>&1
```
Make any other necessary changes to batch_script.sh, and submit it to the 
jobs queue using
```
sbatch batch_script.sh
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

