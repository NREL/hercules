from emu_python.emulator import Emulator
from emu_python.controller import Controller
# from emu_python.emu_comms import EmuComms
from emu_python.py_sims import PySims
from emu_python.utilities import load_yaml

import sys



input_dict = load_yaml(sys.argv[1])

#print(input_dict)

controller = Controller(input_dict)
# emu_comms = EmuComms(input_dict)
py_sims = PySims(input_dict)


emulator = Emulator(controller, py_sims, input_dict)
emulator.run_helics_setup()
emulator.enter_execution(function_targets=[],
                    function_arguments=[[]])

print("runscript complete.")

