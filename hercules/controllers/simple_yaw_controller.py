from abc import abstractmethod
from hercules.controllers.controller_base import Controller

class SimpleYawController(Controller):

    def __init__(self, input_dict):

                # Perhaps these should inherit from an abstract class that 
        # requires a certain input structure.

        self.dt = input_dict["dt"] # Won't be needed here, but generally good to have
        self.n_turbines = input_dict["controller"]["num_turbines"]
        self.turbines = range(self.n_turbines)
        
        # Set initial conditions
        yaw_IC = input_dict["controller"]["initial_conditions"]["yaw"]
        if hasattr(yaw_IC, '__len__'):
            if len(yaw_IC) == self.n_turbines:
                self.yaw_angles = yaw_IC
            else:
                raise TypeError("yaw initial condition should be a float or "+\
                    "a list of floats of length num_turbines.")
        else: 
            self.yaw_angles = [yaw_IC]*self.n_turbines

    def return_outputs(self, input_dict):

        return input_dict


    def step(self, input_dict):

        # In this case, the controller doesn't need memory (yaw instantaneously). 
        # Still, to demonstrate, we can save the current wind directions.

        # Grab name of wind farm (assumes there is only one!)
        wf_name = list(input_dict["hercules_comms"]["amr_wind"].keys())[0]

        # How would we do this part, if not saved in hercules_comms? might be though?
        self.wind_directions = input_dict["hercules_comms"]\
                                         ["amr_wind"]\
                                         [wf_name]\
                                         ["turbine_wind_directions"]

        # Now, set the amr-wind yaw angles
        yaw_angles = self.wind_directions # Yaws instantaneously
        input_dict["hercules_comms"]\
                  ["amr_wind"]\
                  [wf_name]\
                  ["turbine_yaw_angles"] = yaw_angles
        
        return self.return_outputs(input_dict)

    
    @abstractmethod
    def get_controller_dict(self):

        return {}