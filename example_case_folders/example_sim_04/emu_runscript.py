from hercules.emulator import Emulator
from hercules.controller import Controller
# from hercules.emu_comms import EmuComms
from hercules.py_sims import PySims
from hercules.utilities import load_yaml

import sys



input_dict = load_yaml(sys.argv[1])

#print(input_dict)

controller = Controller(input_dict)
py_sims = PySims(input_dict)


emulator = Emulator(controller, py_sims, input_dict)
emulator.run_helics_setup()
emulator.enter_execution(function_targets=[],
                    function_arguments=[[]])

