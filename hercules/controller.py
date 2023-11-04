


class Controller():

    def __init__(self, input_dict):
        self.controller_dict = {}

    def step(self, main_dict):
        available_power = main_dict['py_sims']['inputs']['available_power']
        self.controller_dict['signal'] = available_power

    def get_controller_dict(self):

        return self.controller_dict

