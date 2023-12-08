from abc import abstractmethod

class ControllerStandin():
    """
    This class is a pass-through stand-in for a plant-level controller.
    Actual controllers should be implemented in WHOC
    (https://github.com/NREL/wind-hybrid-open-controller). However, this
    has been left in to allow users to run Hercules without plant-level
    control, if desired.
    """

    def __init__(self, input_dict):
        pass

    @abstractmethod
    def step(self, main_dict):

        # TODO: does there need to be a seperate "controller" dict?
        # Might make understanding the log easier?
        return main_dict

