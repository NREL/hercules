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


It is recommended to run primarily using the run scripts as they will handle the launching of the various components of the hercules platform. However, if you wish to run manually, referring to the sequence of commands in the run_script.sh file will be helpful to see how to execute various configurations of the platform.





