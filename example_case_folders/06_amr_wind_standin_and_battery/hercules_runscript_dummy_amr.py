import sys
from hercules.dummy_amr_wind import launch_dummy_amr_wind

# Check that two or fewer command line arguments were given
if len(sys.argv) > 3:
    raise Exception("Usage: python hercules_runscript_dummy_amr.py <amr_input_file>")

# # Get the first command line argument
# This is the name of the file to read
else:
    if len(sys.argv) > 1:
        amr_input_file = sys.argv[1]
        print(f"Running AMR-Wind dummy with input file: {amr_input_file}")
    if len(sys.argv) > 2:
        amr_standin_file = sys.argv[2]
        print(f"Using standin data for AMR-Wind from file: {amr_standin_file}")

launch_dummy_amr_wind(amr_input_file, amr_standin_file)

