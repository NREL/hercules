# Example 05: FLORIS Wind Standin and Electrolyzer

## Description

This example demonstrates how to use the FLORIS as the wind standin model combined with and electrolyzer plant in a simple case.  This example also uses a WHOC controller to allow the user to give set points to the wind farm to control the wind farm power output, set in the 'wind_power_reference_data.csv' file. The wind speed and wind directions inputs are given in 'floris_standin_data.csv' and can be changed to vary the conditions of the wind simulation. The 'plot_outputs.py' file contains a python script that allows the user to plot the wind turbine and farm power outputs and the electrolyzer plant hydrogen output.

## Running

To run the example, execute the following command in the terminal from within the Example 05 folder:

```bash
bash run_script.sh
```

## Checking outputs

To check the outputs, execute the following command in the terminal:

```bash
python plot_outputs.py
```
