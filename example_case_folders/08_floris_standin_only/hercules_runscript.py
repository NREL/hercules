import sys

from hercules.controller_standin import ControllerStandin
from hercules.emulator import Emulator
from hercules.py_sims import PySims
from hercules.utilities import load_yaml

# Check that command line arguments are provided
if len(sys.argv) != 3:
    raise Exception("Usage: python hercules_runscript.py <hercules_input_file> <helics_port>")

input_dict = load_yaml(sys.argv[1])

# Set the helics port
helics_port = int(sys.argv[2])
input_dict["hercules_comms"]["helics"]["config"]["helics"]["helicsport"] = helics_port
print(f"Running Hercules with helics_port {helics_port}")


controller = ControllerStandin(input_dict)
py_sims = PySims(input_dict)


emulator = Emulator(controller, py_sims, input_dict)
emulator.run_helics_setup()
emulator.enter_execution(function_targets=[], function_arguments=[[]])
