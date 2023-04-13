from abc import abstractmethod

class Controller():

    def __init__(self, input_dict):
        pass

    @abstractmethod
    def step(self, input_dict):

        pass

    @abstractmethod
    def get_controller_dict(self):
        # This method may not be needed, if the controller sets the inputs
        # to amr-wind and the py_sims directly. Still, could be used for 
        # recording the controllers internal state for logging purposes.

        return {}