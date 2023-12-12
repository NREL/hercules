from hercules.emulator import Emulator
from hercules.controller import Controller
from hercules.py_sims import PySims
from hercules.utilities import load_yaml
import time
import sys


from whoc.interfaces.hercules_wind_battery_interface import HerculesWindBatteryInterface
from whoc.controllers.hercules_wind_battery_controller import (
    HerculesWindBatteryController,
)


# if len(sys.argv) > 1:
input_dict = load_yaml(sys.argv[1])


interface = HerculesWindBatteryInterface(input_dict)
controller = HerculesWindBatteryController(interface, input_dict)


input_dict = load_yaml(sys.argv[1])

py_sims = PySims(input_dict)


emulator = Emulator(controller, py_sims, input_dict)
emulator.run_helics_setup()
emulator.enter_execution(function_targets=[], function_arguments=[[]])
