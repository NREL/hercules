import sys

from hercules.amr_wind_standin import launch_amr_wind_standin

amr_input_file = sys.argv[1]
print(f"Running AMR-Wind standin with input file: {amr_input_file}")
amr_standin_file = sys.argv[2]
print(f"Using standin data for AMR-Wind from file: {amr_standin_file}")

launch_amr_wind_standin(amr_input_file, amr_standin_file)
