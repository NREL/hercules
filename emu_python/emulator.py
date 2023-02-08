import numpy as np
import pandas as pd

import datetime as dt



class Emulator():

    def __init__(self, controller, emu_comms, py_sims):
        #TODO we think will receive instantiated classes for the py sims

        # Initialize components
        self.controller = controller
        self.emu_comms = emu_comms
        self.py_sims = py_sims


    def run(self):
        
        pass
        # Run the code

        # Run controller

        # Run helics

        # Run pysims

    def parse_input_yaml(self, filename):

        pass