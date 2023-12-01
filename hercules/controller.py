class Controller:
    def __init__(self, input_dict):
        self.controller_dict = {}
        self.control_method = (
            self.control_example_06
        )  # this can be replaced with a different control logic method depending on the situation.

    def step(self, main_dict):
        self.control_method(main_dict)

    def get_controller_dict(self):
        return self.controller_dict

    def control_example_06(self, main_dict):
        available_power = main_dict["py_sims"]["inputs"]["available_power"]

        if available_power < 1e3:
            self.controller_dict["signal"] = 1 * available_power
        else:
            self.controller_dict["signal"] = -2e3


    