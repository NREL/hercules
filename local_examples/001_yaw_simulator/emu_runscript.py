from emu_python.emulator import Emulator
from emu_python.controller import Controller
from emu_python.emu_helics import EmuHelics
from emu_python.py_sims import PySims
from emu_python.utilities import load_yaml

import sys



input_dict = load_yaml(sys.argv[1])

print(input_dict)

# controller = Controller(input_dict)
# emu_helics = EmuHelics(input_dict)
# py_sims = PySims(input_dict)


# emulator = Emulator(controller, emu_helics, py_sims)

# emulator.run()
