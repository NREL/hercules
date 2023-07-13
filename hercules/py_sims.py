from hercules.python_simulators.simple_solar import SimpleSolar
from hercules.python_simulators.simple_battery import SimpleBattery
from hercules.python_simulators.electrolyzer_plant import ElectrolyzerPlant

import numpy as np


class PySims():

    def __init__(self, input_dict):

        # Save timt step
        self.dt = input_dict['dt']

        # Grab py sim details
        self.py_sim_dict = input_dict['py_sims']

        # If None n_py_sim = 0
        if input_dict['py_sims'] is None:
             self.n_py_sim = 0
             self.py_sim_names = []

        else:

            self.n_py_sim = len(self.py_sim_dict )
            self.py_sim_names = np.copy(list(self.py_sim_dict.keys()))
            print(self.py_sim_names)
            self.py_sim_dict['inputs'] = {}
            self.py_sim_dict['inputs']['available_power'] = 0   # Always calculate available power for py_sims

            # Collect the py_sim objects, inputs and outputs
            for py_sim_name in self.py_sim_names:
                print((self.py_sim_dict[py_sim_name]))
                self.py_sim_dict[py_sim_name]['object'] = self.get_py_sim(self.py_sim_dict[py_sim_name])
                self.py_sim_dict[py_sim_name]['outputs'] =  self.py_sim_dict[py_sim_name]['object'].return_outputs()
                self.py_sim_dict[py_sim_name]['inputs'] = {}
                for needed_input in self.py_sim_dict[py_sim_name]['object'].needed_inputs.keys():
                    self.py_sim_dict['inputs'][needed_input] = self.py_sim_dict[py_sim_name]['object'].needed_inputs[needed_input]
            print(self.py_sim_dict['inputs'])
            # TODO: always add 'available_power' as input??
            # print(self.py_sim_dict['solar_farm_0']['object'])

    def get_py_sim(self, py_sim_obj_dict):

        if py_sim_obj_dict['py_sim_type'] == 'SimpleSolar':
            
            return SimpleSolar(py_sim_obj_dict, self.dt)

        if py_sim_obj_dict['py_sim_type'] == 'SimpleBattery':
            
            return SimpleBattery(py_sim_obj_dict, self.dt)

        if py_sim_obj_dict['py_sim_type'] == 'ElectrolyzerPlant':
            
            return ElectrolyzerPlant(py_sim_obj_dict, self.dt) 
        
    def get_py_sim_dict(self):
         return self.py_sim_dict


    def step(self, main_dict):

        # Collect the py_sim objects
        for py_sim_name in self.py_sim_names:
            print(self.py_sim_names)

            self.py_sim_dict[py_sim_name]['outputs'] = self.py_sim_dict[py_sim_name]['object'].step(main_dict)



