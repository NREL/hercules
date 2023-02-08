from wfc_framework.yaw_controller import yaw_controller

class IndirectControlYawSystem:
    """
    Wrapper for wfc_framework's yaw_controller to align with emu_python's 
    syntax.

    IndirectControlYawSystem uses target offsets applied to the turbine's 
    wind vane signal to implement misalignments.
    """

    def __init__(self, input_dict):

        if input_dict["wd_init"] == "from_wind_sim":
            input_dict["wd_init"] = 0.0 # TODO: get initial value from AMR-Wind
        if input_dict["yaw_init"] == "use_wd_init":
            input_dict["yaw_init"] == input_dict["wd_init"]

        self.closed_loop_yaw_controller = yaw_controller(
            options_dict = {k: input_dict[k] for k in \
                ("yaw_init", "wd_init", "time_const", "deadband", "yaw_rate")
            }
        )

    def step(self, inputs):

        self.closed_loop_yaw_controller.compute(
            wd=inputs["wind_direction"],
            target_vane_offset=inputs["offset_target"]
        )

        outputs = {
            "yaw_position":self.closed_loop_yaw_controller.yaw_position,
            "yaw_state":self.closed_loop_yaw_controller.yaw_state
        }

        return outputs

class DirectControlYawSystem:
    """
    DirectControlYawSystem initiates yaw actions directly.

    Not yet implemented.
    """

    def __init__(self, input_dict):

        raise NotImplementedError("DirectControlYawSystem not implemented.")

    def step(self, inputs):
        
        outputs = None

        return outputs