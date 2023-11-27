from hercules.emulator import Emulator
from hercules.controller import Controller
from hercules.py_sims import PySims
from hercules.utilities import load_yaml
import time
import sys


import os

# os.system("bash helics_amr.sh")

# time.sleep(5)

# abs_path = os.path.dirname(__file__)
# fname = "hercules_input_000.yaml"
# full_path = os.path.join(abs_path, fname)

# input_dict = load_yaml(full_path)

input_dict = load_yaml(sys.argv[1])

controller = Controller(input_dict)
py_sims = PySims(input_dict)


emulator = Emulator(controller, py_sims, input_dict)
emulator.run_helics_setup()
emulator.enter_execution(function_targets=[], function_arguments=[[]])
