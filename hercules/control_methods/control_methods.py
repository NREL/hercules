

class ControlMethodBase():
    def __init__(self):
        self.controller_dict = {}
        self.main_dict = {}

    def step(self, main_dict):
        pass

    def get_controller_dict(self):
        return self.controller_dict
    

class ControllerExample06(ControlMethodBase):
    
    def step(self, main_dict):
        available_power = main_dict["py_sims"]["inputs"]["available_power"]

        if available_power < 1e3:
            self.controller_dict["signal"] = 1 * available_power
        else:
            self.controller_dict["signal"] = -2e3




