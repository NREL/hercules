from emu_python.python_simulators.simple_solar_model import SimpleSolar


class PySims():

    def __init__(self, input_dictionary, dt):

        self.input_dict = input_dictionary['py_sims']

        available_modules = ['SimpleSolar']
        present_modules = {}

        # Find what technologies are in the input file
        component_names = list(self.input_dict.keys())
        for i in component_names:
            present_modules[i] = self.input_dict[i]['type'](self.input_dict[i], dt)
        

    def step(self, inputs):

        # Calls individual python simulations

        outputs = None

        return outputs

