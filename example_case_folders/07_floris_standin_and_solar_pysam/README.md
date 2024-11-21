# Example 07: FLORIS Standin and Solar PySAM

## Description

This example demonstrates how to use the FLORIS Standin and a solar model using pysam.

## Files

#Todo: Explain all the input files

## Running

To run the example, execute the following command in the terminal:

```bash
bash run_script.sh
```


To run `hercules` using the PV plant controller, which provides power setpoints and adjusts the PV power output accordingly, ensure the following line is uncommented in `run_script.sh`:

```
python3 hercules_runscript.py hercules_controller_input_000.yaml >> outputs/loghercules.log 2>&1 &
```

To run `hercules` without the PV plant controller, ensure the folling line is uncommented `run_script.sh`:

```
python3 hercules_runscript.py hercules_input_000.yaml >> outputs/loghercules.log 2>&1 &
```

