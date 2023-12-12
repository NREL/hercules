from abc import abstractmethod

class ControllerStandin():
    """
    This class is a pass-through stand-in for a plant-level controller.
    Actual controllers should be implemented in WHOC
    (https://github.com/NREL/wind-hybrid-open-controller). However, this
    has been left in to allow users to run Hercules without plant-level
    control, if desired.

    This assumes Hercules is running with actuator disk turbine models, and
    will be updated (to be simply a pass-through) when the ROSCO/FAST turbine
    models are incorporated.
    """

    def __init__(self, input_dict):

        # Get wind farm information (assumes exactly one wind farm)
        self.wf_name = list(input_dict["hercules_comms"]["amr_wind"].keys())[0]

    @abstractmethod
    def step(self, main_dict):

        num_turbines = main_dict["hercules_comms"]\
                                ["amr_wind"]\
                                [self.wf_name]\
                                ["num_turbines"]
        
        # Set turbine yaw angles based on current AMR-Wind wind direction
        wd = main_dict["hercules_comms"]\
                      ["amr_wind"]\
                      [self.wf_name]\
                      ["wind_direction"]
        main_dict["hercules_comms"]\
                 ["amr_wind"]\
                 [self.wf_name]\
                 ["turbine_yaw_angles"] = num_turbines*[wd]

        # TODO: does there need to be a seperate "controller" dict?
        # Might make understanding the log easier?
        return main_dict

