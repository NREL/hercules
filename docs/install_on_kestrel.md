# Installation on Kestrel

This document outlines the process for install hercules onto NREL's kestrel
computer.  

## Initial Steps

  1. Log into kestrel
  2. Establish a root folder such as /home/{user-name}/herc_root
  3. Enter that root folder


## Install openfast

(Note this approach mainly follows the instruction set for "CMake with Make for Linux/macOS")
https://openfast.readthedocs.io/en/dev/source/install/index.html#cmake-with-make-for-linux-macos


Then to install the relevent branch:

```
git clone https://github.com/OpenFAST/OpenFAST.git
cd OpenFAST
git checkout tags/v3.4.1
git switch -c v3.4.1
mkdir build
cd build 
```

Now run the following set of commands:

```
module purge
module load craype-x86-spr
module load intel-oneapi-mkl/2023.2.0-intel
module load intel-oneapi-mpi/2021.10.0-intel
module load intel-oneapi-compilers/2023.2.0

export OMP_PROC_BIND=spread
export KMP_AFFINITY=balanced

cmake .. -DBUILD_SHARED_LIBS=ON -DDOUBLE_PRECISION:BOOL=OFF -DCMAKE_INSTALL_PREFIX:PATH=./install

make -j 36
make install
```



## Install ROSCO

With the same shell which has the above mentioned modules already loaded

(Now following the instructions in the full ROSCO installation)
https://rosco.readthedocs.io/en/latest/source/install.html#full-rosco-installation

Starting from the ''herc_root'' folder:

```
git clone https://github.com/NREL/ROSCO.git
cd ROSCO
git checkout develop

cd ROSCO #Note entering 2nd level ROSCO
mkdir build
cd build
cmake ..
make
```

## Install AMR-Wind

TODO: This is not yet succesfull

```
git clone git@github.com:Exawind/amr-wind.git
cd amr-wind
git checkout d917dca2

git submodule update --init --recursive

git switch -c hercules-build
```

Next you are going to paste the following code into a file ''build_script'' in the top-level folder of amr_wind.  

**It is important that before running the script you edit the locaiton of openfast to match your location**

```
#!/bin/bash -l

rm -rf build
mkdir build
cd build

module purge
module load craype-x86-spr
module load intel-oneapi-mpi/2021.10.0-intel
module load intel-oneapi-compilers/2023.2.0
module load netcdf-c/4.9.2-intel-oneapi-mpi-intel
module load git/2.40.0
module use /nopt/nrel/apps/modules/test/application
module load helics/3.4.0-cray-mpich-intel


module load cmake

cmake -DAMR_WIND_ENABLE_CUDA:BOOL=OFF \
      -DAMR_WIND_ENABLE_MPI:BOOL=ON \
      -DAMR_WIND_ENABLE_OPENMP:BOOL=OFF \
      -DAMR_WIND_TEST_WITH_FCOMPARE:BOOL=OFF \
      -DCMAKE_BUILD_TYPE=Release \
      -DAMR_WIND_ENABLE_NETCDF:BOOL=ON \
      -DNETCDF_DIR:PATH=/nopt/nrel/ecom/hpacf/software/2020-07/spack/opt/spack/linux-centos7-skylake_avx512/gcc-8.4.0/netcdf-c-4.7.3-533s5vfhvbbvpgxambbzk66vtlcce2u6  \
      -DnetCDF_DIR:PATH=/nopt/nrel/ecom/hpacf/software/2020-07/spack/opt/spack/linux-centos7-skylake_avx512/gcc-8.4.0/netcdf-c-4.7.3-533s5vfhvbbvpgxambbzk66vtlcce2u6  \
      -DAMR_WIND_ENABLE_OPENFAST:BOOL=ON \
      -DOpenFAST_ROOT:PATH=/home/pfleming/herc_root/OpenFAST/build/install/ \
      -DAMR_WIND_ENABLE_HYPRE:BOOL=OFF \
      -DAMR_WIND_ENABLE_MASA:BOOL=OFF \
      -DAMR_WIND_ENABLE_HELICS:BOOL=ON \
      -DAMR_WIND_ENABLE_TESTS:BOOL=ON \
      -DAMR_WIND_ENABLE_FORTRAN:BOOL=OFF \
      -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=ON \
      -DAMR_WIND_ENABLE_ALL_WARNINGS:BOOL=ON \
      -DBUILD_SHARED_LIBS:BOOL=ON \
      ..

nice make -j32
      -DAMR_WIND_ENABLE_TESTS:BOOL=ON \
      -DAMR_WIND_ENABLE_FORTRAN:BOOL=OFF \
      -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=ON \
      -DAMR_WIND_ENABLE_ALL_WARNINGS:BOOL=ON \
      -DBUILD_SHARED_LIBS:BOOL=ON \
      ..

nice make -j32
```

Run via:

```
bash build_script
```

## Set up a hercules conda environment

This will be needed for the remaining installations

```
module load anaconda3
conda create --name hercules python
conda activate hercules
```

Edit your ~/.bashrc file to include a helpful shortcut function based on this:

```
env_hercules()
{
        module purge
        module load craype-x86-spr
        module load intel-oneapi-mpi/2021.10.0-intel
        module load intel-oneapi-compilers/2023.2.0
        module load netcdf-c/4.9.2-intel-oneapi-mpi-intel
        module load git/2.40.0
        # module use /nopt/nrel/apps/modules/test/application
        # module load helics/3.4.0-cray-mpich-intel
        module load anaconda3

        conda activate hercules
}
```

## Install SEAS

Go back to herc_root

```
git clone https://github.nrel.gov/SEAS/SEAS

cd SEAS
git fetch --all
git switch dv/emuwind
cd ..
pip install -e SEAS
```

## Install Hercules

Go back to herc_root

```
git clone https://github.com/NREL/hercules
pip install -e hercules
```

## Install electrolyzer module

Go back to herc_root

```
git clone git@github.com:NREL/electrolyzer.git
cd electrolyzer
git fetch --all
git switch develop
```

## Try an example!

Look at 
herc_root/hercules/example_case_folders/02_amr_wind_dummy_only

(May need to edit the port from 32000 to 32001 in bash_script.sh)

```
source bash_script.h
```