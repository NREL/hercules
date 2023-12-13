import sys
from hercules.dummy_amr_wind import launch_dummy_amr_wind


amr_input_file = sys.argv[1]
print(f"Running AMR-Wind dummy with input file: {amr_input_file}")
amr_standin_file = sys.argv[2]
print(f"Using standin data for AMR-Wind from file: {amr_standin_file}")

launch_dummy_amr_wind(amr_input_file, amr_standin_file)
