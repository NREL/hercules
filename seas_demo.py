import sys
import ast
import numpy as np
from SEAS.federate_agent import FederateAgent
import logging    

class SenderAgent(FederateAgent):
    def __init__(self, config_dict):
        super(SenderAgent, self).__init__(
            name=config_dict["name"],
            feeder_num=0,
            starttime=config_dict["starttime"],
            endtime=config_dict["stoptime"],
            agent_num=0,
            config_dict=config_dict,
        )
        self.deltat = 1

    def run(self):
        print("SenderAgent time before loop: ", self.absolute_helics_time)
        i = 0
        while self.absolute_helics_time < (self.endtime - self.starttime + 1):
            print("+++++")
            print("SenderAgent time in loop: ", self.absolute_helics_time)
            incoming_messages = self.helics_connector.get_all_waiting_messages()
            try:
                message = list(
                        ast.literal_eval(incoming_messages["computer"]["message"])
                    )
            except Exception:
                print("bad message! setting false message")
                message = [-1, -1]
            print("timestamp received from computer: ", message[0])
            print("result received from computer: ", message[1])
            to_send = [self.absolute_helics_time, i]
            print("sending", to_send, "to computer")
            self.send_via_helics("sender", str(to_send))
            self.sync_time_helics(self.absolute_helics_time+self.deltat)
            i += 1
            print("-----")

class ComputerAgent(FederateAgent):
    def __init__(self, config_dict):
        super(ComputerAgent, self).__init__(
            name=config_dict["name"],
            feeder_num=0,
            starttime=config_dict["starttime"],
            endtime=config_dict["stoptime"],
            agent_num=0,
            config_dict=config_dict,
        )
        self.deltat = 1

    def run(self):
        print("ComputerAgent time before loop: ", self.absolute_helics_time)
        #self.sync_time_helics(self.absolute_helics_time) # or comment out
        while self.absolute_helics_time < (self.endtime - self.starttime + 1):
            print("+++++")
            print("ComputerAgent time in loop: ", self.absolute_helics_time)
            incoming_messages = self.helics_connector.get_all_waiting_messages()
            try:
                message = list(
                        ast.literal_eval(incoming_messages["sender"]["message"])
                    )
            except Exception:
                print("bad message! setting false message")
                message = [-1, -1]
            print("timestamp received from sender: ", message[0])
            i = message[1]
            to_send = [self.absolute_helics_time, i]#*10]
            print("sending", to_send, "to sender")
            self.send_via_helics("computer", str(to_send))
            self.sync_time_helics(self.absolute_helics_time+self.deltat)
            print("-----")

if __name__ == "__main__":
    a = int(sys.argv[1])
    
    config_dict = {
        "name": None,
        "use_dash_frontend": False,
        "KAFKA": False,
        "KAFKA_topics": "EMUV1py",
        "helics": {
            "subscription_topics": None,
            "publication_topics": None,
            "endpoints": [],
            "helicsport": 32000,
        },
        "publication_interval": 1,
        "endpoint_interval": 1,
        "starttime": 0,
        "stoptime": 5,
        "Agent": "ControlCenter",
    }

    if a == 0:
        config_dict["name"] = "sender"
        config_dict["helics"]["subscription_topics"] = ["computer"]
        config_dict["helics"]["publication_topics"] = ["sender"]
        agent = SenderAgent(config_dict)
    elif a == 1:
        config_dict["name"] = "computer"
        config_dict["helics"]["subscription_topics"] = ["sender"]
        config_dict["helics"]["publication_topics"] = ["computer"]
        agent = ComputerAgent(config_dict)
    else:
        raise ValueError("Invalid value received.")
    
    agent.run_helics_setup()
    agent.enter_execution(function_targets=[], function_arguments=[[]])

