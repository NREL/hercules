# Steps to Hercules
## Hercules Input file
Contains
- Simulation name: Just a name
- dt: delta t for sim (does the wind have to be in the same dt)
- starttime: Start of the sim
- endtime: End of the sim

### Py-sim
I think this is python simulators
- wind_farm_0: Name of the wind farm
    - py_sim_type: Which simulator to use (WindSimLongTerm)
    - num_turbine: 3
    - verbose: True
    - floris_input_file: Floris input for the farm
    - wind_input_filename: file containing wind inputs (without wakes) on the file location
    - turbine_file_name: model used and properties

## Controller_standing_no_helics
Creates a controller for a particular farm.
Only has a step method that derates a turbine increasingly over time.

## Create PySims object
PySims object has dt from the input_dict.
Then and a property called 'object' that gets instantiation by the type of pysim object (like battery, electrolyzer, windsimlongterm) etc.

### windsimlongterm pysim
For this 'object', process the wind input file, floris files and then add in 'turbine_array' property, the filter model (or 1dof model).

The details of the windsimlongterm model is as follows:
- needed_input:=empty
- Set dt to input_dict['dt'] ()
- num_floris_calcs:=0 (tracks the number of floric calc)
- Start_time_s has to be 0, not implmented yet.
- Load all three file: floris_input, wind_input, turbine_file
- Load wind from wind_input file
- dt_wi is the time step from the wind_file
- Check if dt and dt_wi can work well together
- Now focus on floris model
- Set floris operation_model to simple-derating to use a simple derating configuration (value to be set later)
- St floris_wd_threshold, floris_ws_threshold, floris_ti_threshold, floris_derating_threshold (I think these are minimum changes needed in these values before floris updates.)
- Variable derating_buffer to hold previous derating commands
- Use mean values of wind_direction, wind_speeds, TI and derating to use in floris (I assume) later
- Run self.update_wake_deficits() If floris needs to updated then update it and run floris model again.
- Calculate floris_wake_deficits (This calculation doesn't make sense to me yet, recheck)
- Increase self.num_floris_calcs by 1
- Back to the WindSimLongTerm, read turbine yaml and if filter_model is used then create a model based in floris data and the current waked valocities, add the model in self.turbine_array.
- Set as the current power, the previous power from the turbine_array object
- Next return_outputs method of WindSimLongTerm is called which returns the wind data and waked velocities etc from floris
- Now back to the very main code create EmulatorNoHelics by passing the controller, py_sims object and input_dict.
- Call Enter_execution method of the emulator. This is the main execution loop
- Run controller.step() which just changes the derating value in the main_dict.
- Then call Py_sim's (in our case WindSimLongTerm's) step method.
- Run the step method of the turbine model in turbine_array which retruns the power based in the current waked velocity and current derating (why use derating)
- 