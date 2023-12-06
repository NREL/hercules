from abc import abstractmethod

class Controller():

    def __init__(self, input_dict):
        
        # Get wind farm information (assumes only one wind farm!)
        self.wf_name = list(input_dict["hercules_comms"]["amr_wind"].keys())[0]

        pass

    @abstractmethod
    def step(self, input_dict):

        num_turbines = input_dict["hercules_comms"]\
                                 ["amr_wind"]\
                                 [self.wf_name]\
                                 ["num_turbines"]

        # Set turbine yaw angles based on current AMR-Wind wind direction
        wd = input_dict["hercules_comms"]\
                       ["amr_wind"]\
                       [self.wf_name]\
                       ["wind_direction"]
        input_dict["hercules_comms"]\
                  ["amr_wind"]\
                  [self.wf_name]\
                  ["turbine_yaw_angles"] = num_turbines*[wd]

        return input_dict

    @abstractmethod
    def get_controller_dict(self):
        # This method may not be needed, if the controller sets the inputs
        # to amr-wind and the py_sims directly. Still, could be used for 
        # recording the controllers internal state for logging purposes.

        return {}