from emu_python.python_simulators.simple_solar import SimpleSolar


class PySims():

    def __init__(self, input_dictionary):

        # Save timt step
        self.dt = input_dictionary['dt']

        # Grab py sim details
        self.py_sim_dict = input_dictionary['py_sims']
        self.n_py_sim = len(self.py_sim_dict )
        self.py_sim_names = self.py_sim_dict.keys()

        # Collect the py_sim objects, inputs and outputs
        for py_sim_name in self.py_sim_names:
            
            self.py_sim_dict[py_sim_name]['object'] = self.get_py_sim(self.py_sim_dict[py_sim_name])
            self.py_sim_dict[py_sim_name]['outputs'] =  self.py_sim_dict[py_sim_name]['object'].return_outputs()
            self.py_sim_dict[py_sim_name]['inputs'] = {}

        # print(self.py_sim_dict['solar_farm_0']['object'])

    def get_py_sim(self, py_sim_obj_dict):

        if py_sim_obj_dict['py_sim_type'] == 'SimpleSolar':
            
            return SimpleSolar(py_sim_obj_dict, self.dt)


    def step(self):

        # Collect the py_sim objects
        for py_sim_name in self.py_sim_names:

                self.py_sim_dict[py_sim_name]['outputs'] = self.py_sim_dict[py_sim_name]['object'].step(self.py_sim_dict[py_sim_name]['inputs'])



