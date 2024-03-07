# Battery

Energy counting type battery model 

Example for battery use in: `example/battery`

### Parameters

Battery parameters are defined in the hercules input yaml file used to initialize `emulator`.

- `py_sim_type`
- `size`
- `energy_capacity`
- `charge_rate`
- `max_SOC`
- `min_SOC`
- `initial_conditions`
  - `SOC`

Once initialized, the battery is only interacted with using the `step` method.


### Inputs
inputs are passed to `step` as a dict, `inputs` with 
- `inputs["setpoints"]["battery"]["signal"]`
- `inputs["py_sims"]["inputs"]["available_power"]`


### Outputs

- power
- reject
- soc

### References
