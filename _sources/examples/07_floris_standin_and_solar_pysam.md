# Example 07: FLORIS Standin and Solar PySAM

## Description

This example demonstrates how to use the FLORIS Standin and a solar model using pysam.

## Running

To run the example, execute the following command in the terminal:

```bash
bash batch_script.sh
```


To run `hercules` using the PV plant controller, which provides power setpoints and adjusts the PV power output accordingly, ensure the following line is uncommented in `batch_script.sh`:

```
python3 hercules_runscript.py hercules_controller_input_000.yaml >> outputs/loghercules.log 2>&1 &
```

To run `hercules` without the PV plant controller, ensure the folling line is uncommented `batch_script.sh`:

```
python3 hercules_runscript.py hercules_input_000.yaml >> outputs/loghercules.log 2>&1 &
```

## Notes

Make sure hercules conda or venv is activated before running the example.