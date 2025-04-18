# Example: AMR Wind Only

## Description

This first example runs AMR Wind, using Hercules, but without any additional generation simulated.

Most examples will have the pattern of having an sbatch_script.sh file which calls a run_script.sh file.  The paradigm is that the run_script.sh can be run on a local machine, while the sbatch_script.sh is used to submit the job to a cluster.  However, in this case since AMR-Wind can only be run on a cluster, the sbatch_script.sh is the only script provided.

## Running

To run the example, execute the following command in the terminal:

```bash
sbatch sbatch_script.sh
```
## Outputs

To plot the outputs run the following command in the terminal:

```bash
python plot_outputs.py
```

