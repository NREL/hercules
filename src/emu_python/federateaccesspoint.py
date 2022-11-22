import time
import ast
import helics as h
import json
import threading as mt

def read_assign_config(obj,fname, type="file"):
    if type == "file":
        f = open(fname, "r")
        data = f.read()
        js = json.loads(data)
        obj.__dict__.update(js)
    elif type == "dict": 
        # js = json.loads(fname)
        obj.__dict__.update(fname) 


class federateagent:
    """
        Cosimulation federate 
    """
    def __init__(self,name,feeder_num=0,starttime=0, endtime=0,agent_num=0,config_dict=None):
        # self.env = env
        self.name = name        
        self.feeder_num = feeder_num
        self.starttime =  starttime
        self.endtime = endtime
        self.deltat  = config_dict['helics']['deltat']
        
        self.subscription_topic  = []
        # read_assign_config(self, f"Agent{agent_num}.json")
        read_assign_config(self, config_dict,"dict")
        # self.deltat = 1.0


    def run_helics_setup(self,comm_type="zmq",broker_ip="127.0.0.1", broker_num=0,broker_port=23405):
        """
            used to create the HELICS broker and federates.
            helicsSub: helics federates to subscribe for messages,
            comm_type: mpi or zmq for communication layer
            broker: specifiy if this agent needs to create a broker
            num_cells: total number of cells or helics federates, connected to this broker
        """
        self.currenttime = 0.0
        self.name_helics = "{}_{}".format(self.feeder_num,self.name)
        self.broker_num = broker_num
        print("All variables used in initialization : ", self.name_helics, comm_type, broker_ip, broker_port, flush=True)
        fedinfo =  h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetCoreName(fedinfo, self.name_helics )
        h.helicsFederateInfoSetCoreTypeFromString(fedinfo, comm_type)
        fedinitstring = "--federates=1"
        h.helicsFederateInfoSetCoreInitString(fedinfo, fedinitstring)
        h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_delta, self.deltat)
        self.cfed = h.helicsCreateCombinationFederate(self.name_helics ,fedinfo)
        
        self.pub = {}
        for x in self.helics['publication_topic']:
            self.pub[x] = h.helicsFederateRegisterGlobalTypePublication(self.cfed, x , "string", "")
        self.sub = {}
        for x in self.helics['subscription_topic']:
            self.sub[x] = h.helicsFederateRegisterSubscription(self.cfed,x ,"string")
        self.ends = {}
        for x in self.helics['endpoints']:
            self.ends[x] =h.helicsFederateRegisterGlobalEndpoint(fed=self.cfed, name=x)
        
    def enter_execution(self,function_targets= [], function_arguments=[[]]):
        print("TIME INFROMATION!!",self.currenttime,self.starttime,self.endtime)
        h.helicsFederateEnterExecutingMode(self.cfed)  
        # self.initialize_emt_sim(self)       
        self.run()


    def run(self):
        """ This must be implemented """

        # print("Inside run function!!", self.currenttime)
        # while self.currenttime < (self.endtime - self.starttime  +1 ):
        #     self.sync_time_helics(self.deltat)
        #     tmp = self.helics_get_all()
        #     if tmp != []:
        #         self.process_subscription_event(tmp)
        #     tmp = self.receive_endpoint()
        #     if tmp != []:
        #         self.process_endpoint_event(tmp)
        #     if self.currenttime%self.publication_interval==0:
        #         self.process_periodic_publication()
        #     if self.currenttime%self.endpoint_interval==0:
        #         self.process_periodic_endpoint()
                

    def listen_for_messages(self):
        while self.currenttime < (self.endtime - self.starttime  +1 ):
            self.sync_time_helics(self.deltat)
            tmp = self.helics_get_all()
            if tmp != []:
                self.process_subscription_event(tmp)
            else:
                continue

    def listen_for_endpoints(self):
        while self.currenttime < (self.endtime):
            self.sync_time_helics(self.deltat)
            tmp = self.receive_endpoint()
            if tmp != []:
                self.process_endpoint_event(tmp)
            else:
                continue        
            
    def process_periodic_publication(self):
        """ This must be implemented """
        raise NotImplementedError    

    def get_currenttime(self):
        return (self.currenttime + self.starttime)

    def process_periodic_endpoint(self):
        """ This must be implemented """
        raise NotImplementedError    

    def process_subscription_event(self, msg):
        """ This must be implemented """
        raise NotImplementedError        

    def process_endpoint_event(self, msg):
        """ This must be implemented """
        raise NotImplementedError        

    def helics_get_all(self):
        """
            Subscribe to messages from any federate on the HELICS bus
        """

        message = []

        for key in self.sub.keys():
            x = self.sub[key]
            # print("name: ", self.name)
            # print("Time ", self.currenttime)
            # print("Key : ",x)
            msg = h.helicsInputGetString(x)
            # print("MESSAGE as is: ", msg)
            # print("MESSAGE as is decoded : ", msg.decode())

            # if type(msg) == dict:
            #     pass
            # # else:
            # msg2 = ast.literal_eval(msg)
            # print("message ", msg2, msg, flush=True)
            # if type(msg2) == dict:
            message.append(msg)
            # else:
            #     pass
        if len(message) ==1 :
            message = message[0]
        return message

    def helics_get_source(self, source):
        """
            subscribe to a message from a HELICS federate

        """
        for i in range(4):
            try:
                msg = h.helicsInputGetString(self.sub[source])
                message = ast.literal_eval(msg)
                if message['destination'] == self.name_helics:
                    return (message)
                else:
                    return None
            except:
                pass

    def helics_put(self,destination, message):
        """
            Send a message to a particular destion over the HELICS bus
        """
        msg_dict = {'time': self.get_currenttime(),'destination': destination, 'message':message, 'source' : self.name_helics}
        h.helicsPublicationPublishString(self.pub, str(msg_dict))

    def helics_broadcast(self,topic,message):
        """
        Broadcast a message over the HELICS bus
        """
        # msg_dict = {'time': self.get_currenttime(),'destination': '', 'message':message,'source' : self.name_helics }
        msg_dict = message
        h.helicsPublicationPublishString(topic, str(msg_dict))

    def sync_time_helics(self,steps):
        # if self.currenttime < (self.starttime):
        #     print("Yes current time is slow!!",self.currenttime,self.starttime,self.stoptime)
        #     self.currenttime = h.helicsFederateRequestTime(self.cfed,(self.starttime-self.currenttime+1))
        # if self.currenttime < (self.endtime):
        self.currenttime = h.helicsFederateRequestTime(self.cfed,steps)

    # def run(self):
    #     """ This must be implemented """
    #     raise NotImplementedError

    def run_model(self):
        """ This must be implemented """
        raise NotImplementedError

    def finalize(self):
        h.helicsFederateFinalize(self.cfed)
        h.helicsFederateFree(self.cfed)

    def broadcast(self,topic, message):
        self.helics_broadcast(topic, message)
    
    def send(self,destination,message):
        self.helics_put(destination, message)
    
    def receive_all(self):
        self.helics_get_all()
    
    def receive_source(self,source):
        self.helics_get_source(source)

    def send_endpoint(self,message,name):
        h.helicsEndpointSendBytesTo(self.myendpoint, message, name)

    def send_opendss(self,message):
        h.helicsEndpointSendBytesTo(self.myendpoint, message,self.myopendss_endpoint)

    def receive_endpoint(self):
        all_msg = []
        for x in self.ends.keys():
            myendpoint = self.ends[x]
            if h.helicsEndpointHasMessage(myendpoint):
                while True:
                    msg = h.helicsEndpointGetMessage(myendpoint)
                    # print("ENDPOINT MSG ", msg)
                    if msg.data == "":
                        break
                    all_msg.append(msg)
        return (all_msg)
    
    def periodic_publications(self):
        while self.currenttime < self.endtime:
            if self.currenttime % self.publication_interval == 0.0:
                self.process_periodic_publication()
            self.sync_time_helics(self.publication_interval)
    
    def periodic_endpoints(self):
        while self.currenttime < self.endtime:
            if self.currenttime % self.endpoint_interval == 0.0:
                self.process_periodic_endpoint()
            self.sync_time_helics(self.helics['deltat'])
    

