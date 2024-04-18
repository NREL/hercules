# Example 09: AMR Wind with OpenFAST
## Description

This example demonstrates how to run AMR Wind while also using OpenFAST and ROSCO as the turbine model.  This example contains OpenFAST files for the NREL 5MW reference wind turbine.  The support for this example in documentation is for running on an NREL supercomputer (either Eagle or Kestrel, both with sample bash files in the example). To run this example, you will need your own compiled version of AMR Wind, following the instructions in Section [Install via spack](install_spack). 

## Running

To run the example, you will need to change some of the paths to match your own compilation of AMR Wind. You will need to follow the following steps to run this example:

1) First, you will need to change line 36 in 'bash_kestrel.sh' to match your own path to your AMR Wind executable.

2) Then, you will need to change line 77 in 'NRELOffshrBsline_5MW_Onshore_ServoDyn.dat' under the NREL-5MW folder to match your installation of the 'libdiscon.so' library in your ROSCO installation.

3) Finally, you can submit your job to run on Kestrel using the following command in the terminal:


```bash
sbatch bash_kestrel.sh
```
or run on Eagle using the following command in the terminal:

```bash
sbatch batch_script_eagle.sh
```

## Notes
This example uses precursor inflow files for AMR Wind from the SSC project on Kestrel and Eagle. Please let us know if you are interested in running this example and do not have access to these input files.