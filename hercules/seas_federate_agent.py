from abc import ABC
import ast
import helics
import json
import os

class FederateAgentBase(ABC):
    """Base class for the FederateAgent class.

    This class is intended to hold methods that are currently unused but may be
    needed in the future.
    """

    def listen_for_messages(self):
        while self.absolute_helics_time < (self.endtime - self.starttime  +1 ):
            self.sync_time_helics(self.deltat)
            tmp = self.helics_connector.get_all_waiting_messages()
            if tmp != []:
                self.process_subscription_messages(tmp)
            else:
                continue

    def listen_for_endpoints(self):
        while self.absolute_helics_time < (self.endtime):
            self.sync_time_helics(self.deltat)
            tmp = self.helics_connector.receive_from_endpoints()
            if tmp != []:
                self.process_endpoint_event(tmp)
            else:
                continue   
    
    def run_model(self):
        """ This must be implemented """
        raise NotImplementedError

        
    def periodic_publications(self):
        while self.absolute_helics_time < self.endtime:
            if self.absolute_helics_time % self.publication_interval == 0.0:
                self.process_periodic_publication()
            self.sync_time_helics(self.publication_interval)
    
    def periodic_endpoints(self):
        while self.absolute_helics_time < self.endtime:
            if self.absolute_helics_time % self.endpoint_interval == 0.0:
                self.send_periodic_endpoint_messages()
            self.sync_time_helics(self.helics['deltat'])


class HelicsConnectorBase(ABC):
    """Base class for the HelicsConnector class.

    This class is intended to hold methods that are currently unused but may be
    needed in the future.
    """

    def send_endpoint(self, message, name):
        helics.helicsEndpointSendBytesTo(self.en, message, name)

    def send_opendss(self,message):
        helics.helicsEndpointSendBytesTo(self.myendpoint, message,self.myopendss_endpoint)

    def helics_finalize(self):
        helics.helicsFederateFinalize(self.combo_federate)
        helics.helicsFederateFree(self.combo_federate)

def read_assign_config(obj, source, type="file"):
    """Assign the specified attributes to the target object.

    If the type is "file", source is treated as the path to a json file containing the attributes
    to be assigned.

    If the type is "dict", source is treated as a dictionary of the attributes.

    Args:
        obj: the target object
        source: the source of the attributes to be assigned
        type: the type of the source
    """
    if type == "file":
        f = open(source, "r")
        data = f.read()
        source_config = json.loads(data)
        obj.__dict__.update(source_config)
    elif type == "dict": 
        obj.__dict__.update(source)


class FederateAgent(FederateAgentBase):
    """Base class representing a single federate for use in helics.

    This class handles basic communication via helics as well as the mechanics of running 
    the simulation's time steps. For application-specific behavior, create a subclass
    containing the application-specific logic.
    """

    def __init__(self,name,feeder_num=0,starttime=0, endtime=0, agent_num=0, config_dict=None, config_file=None, **kwargs):
        """Create a new federateagent.

        The combination of name and feeder_num values must be unique within the simulation.

        Args:
            name: the name used to identify the agent
            feeder_num: ?
            starttime: ?
            endtime: the helics timestep at which the agent should stop running its simulation
            config_dict: the configuration values for the agent
        """

        self.name = name        
        self.feeder_num = feeder_num
        self.starttime =  starttime
        self.endtime = endtime

        if config_dict is not None and config_dict.get("helics", {}).get("deltat") is not None:
            self.deltat  = config_dict['helics']['deltat']
        else:
            self.deltat = 1.0

        if config_dict is not None:
            read_assign_config(self, config_dict, "dict")
        elif config_file is not None:
            read_assign_config(self, config_file, "file")

    def run_helics_setup(self, broker_params={}):
        """Create a new helics federate and initialize any necessary connections to the broker.

        Uses the agent's "helics" configuration to determine which topics and endpoints to attach to.

        Args:
            broker_params: a dict of keyword args to pass to the HelicsConector's connect() function
        """

        self.absolute_helics_time = 0.0
        self.name_helics = "{}_{}".format(self.feeder_num, self.name)

        broker_params['broker_port'] = os.getenv('HELICS_PORT', '32000')
        broker_params['broker_address'] = os.getenv('HELICS_HOST', '127.0.0.1')

        self.helics_connector = HelicsConnector(self.name_helics, self.deltat, **broker_params)
        self.helics_connector.connect(self.helics.get('publication_topics'), 
            self.helics.get('subscription_topics'), self.helics.get('endpoints'))
        
    def enter_execution(self,function_targets= [], function_arguments=[[]]):
        """Run the federate's full simulation.
        """

        self.helics_connector.enter_executing_mode()
        self.run()

    def run(self):
        """Run the federate's full simulation.

        Connects to the helics broker after each step in order to synchronize time.
        At each time step, takes any appropriate publish and subscribe actions via
        the helics broker.
        """

        self.publish_initial_helics_data()

        while self.absolute_helics_time < self.endtime:
            self.sync_time_helics(self.absolute_helics_time + self.deltat)

            if (self.absolute_helics_time < self.starttime):
                continue
    
            incoming_messages = self.helics_connector.get_all_waiting_messages()
            if incoming_messages != {}:
                self.process_subscription_messages(incoming_messages)

            tmp = self.helics_connector.receive_from_endpoints()
            if tmp != []:
                self.process_endpoint_event(tmp)
            if self.absolute_helics_time%self.publication_interval==0:
                self.process_periodic_publication()
            if self.absolute_helics_time%self.endpoint_interval==0:
                self.send_periodic_endpoint_messages()
                
    def send_via_helics(self, topic, message):
        """Send a message to a particular topic on the helics bus.
        
        Adds any necessary metadata that the receiving end may expect.

        Args:
            topic: the helics topic to send the message on
            message: a string representing the message to send
        """
        message = {
            'message': message, 
            'source' : self.name_helics,
            'timestamp': self.absolute_helics_time
        }
        self.helics_connector.helics_put(topic, message)     

    def publish_initial_helics_data(self):
        """Publish any data that should be available on the bus at the first timestep. 
        """
        pass

    def process_periodic_publication(self):
        """Publish data to the helics broker. Must be implemented by a subclass.

        This function is called every publication_interval.
        """
        raise NotImplementedError

    def send_periodic_endpoint_messages(self):
        """Send any necessary endpoint messages. Must be implemented by a subclass."""
        raise NotImplementedError    

    def process_subscription_messages(self, incoming_messages):
        """Take any necessary internal action on an incoming subscription event. Must be implemented by a subclass.
        
        Args:
            incoming_messages: a dictionary of topic name -> message received for the topic
        """
        raise NotImplementedError        

    def process_endpoint_event(self, msg):
        """Take any necessary internal action on an incoming endpoint event. Must be implemented by a subclass."""
        raise NotImplementedError 

    def sync_time_helics(self, next_timestep):
        """Retrieve and store the current timestep in the helics simulation.

        Args:
            next_timestep: the requested timestep from helics
        """
        self.absolute_helics_time = self.helics_connector.update_helics_time(next_timestep)


    def broadcast(self, topic, message):
        """Broadcast the specified topic and message to all helics destinations.

        Args:
            topic: the helics topic to publish to
            message: the message to send
        """
        self.send_via_helics(topic, message)

class HelicsConnector(HelicsConnectorBase):
    """Class used by the federate agent in order to encapsulate helics communication.

    This prevents the federate agent from needing to call helics functions directly.
    The goal is to make it easier to mock out helics communication for unit and
    integration testing. 
    """

    DEFAULT_BROKER_PORT = 32000

    def __init__(self, name_helics, deltat, comm_type="zmq", broker_address="127.0.0.1",
                 broker_port=DEFAULT_BROKER_PORT):
        """Create a new HelicsConnector.

        Args:
            name_helics: the name to use when connecting to helics. Must be unique within
                the simulation.
            deltat: the helics timestep for this agent to listen on
            comm_type: the protocol to use for communicating with the helics broker
            broker_address: the address of the helics broker
            broker_port: the port of the helics broker
        """

        self.name_helics = name_helics
        self.deltat = deltat
        self.comm_type = comm_type
        self.broker_address = broker_address
        self.broker_port = broker_port

        self.helics_pub_topics = {}
        self.helics_subscr_topics = {}
        self.helics_endpoints = {}

    def connect(self, pub_topics=None, subscr_topics=None, endpoints=None):
        """Connect to the helics broker and initialize any messaging topics.

        Args:
            pub_topics: list of helics topics to publish to
            subscr_topics: list of topics to subscribe to
            endpoints: list of helics endpoints to expose
        """
        federate_info = helics.helicsCreateFederateInfo()
        helics.helicsFederateInfoSetCoreName(federate_info, self.name_helics)
        helics.helicsFederateInfoSetCoreTypeFromString(
            federate_info, self.comm_type)

        federate_init_str = f"--federates=1 --broker_address={self.broker_address} --brokerport={self.broker_port}"
        # federate_init_str = f"--federates=1 --broker_address={self.broker_address} "
        helics.helicsFederateInfoSetCoreInitString(
            federate_info, federate_init_str)
        helics.helicsFederateInfoSetTimeProperty(federate_info,
                                                 helics.helics_property_time_delta, self.deltat)

        self.combo_federate = helics.helicsCreateCombinationFederate(
            self.name_helics, federate_info)

        for topic in pub_topics or []:
            self.helics_pub_topics[topic] = helics.helicsFederateRegisterGlobalTypePublication(
                self.combo_federate, topic, "string")

        for topic in subscr_topics or []:
            self.helics_subscr_topics[topic] = helics.helicsFederateRegisterSubscription(
                self.combo_federate, topic)

        for endpoint in endpoints or []:
            self.helics_endpoints[endpoint] = helics.helicsFederateRegisterGlobalEndpoint(
                self.combo_federate, endpoint)

    def enter_executing_mode(self):
        """Tell helics that the federate is ready to enter executing mode.
        """
        helics.helicsFederateEnterExecutingMode(self.combo_federate)

    def get_all_waiting_messages(self):
        """Ingest any waiting messages from the helics bus.

        Returns:
            a dict of the waiting messages, by subscription key 
        """

        messages = {}
        for subscription_key, helics_input in self.helics_subscr_topics.items():

            msg = ast.literal_eval(helics.helicsInputGetString(helics_input))
            if type(msg) == dict:
                messages[subscription_key] = msg
            else:  # This code is specific to AMRWind only
                messages[subscription_key] = {"message": msg}

        return messages

    def receive_from_source(self, source, retries_allowed=4):
        """Retrieve the waiting message from a specific helics source.

        Args:
            source: the subscription key of the source
            retries_allowed: the number of times to retry in case of an exception

        Returns:
            the message retrieved from the specified helics source
        """
        for i in range(retries_allowed):
            try:
                msg = helics.helicsInputGetString(
                    self.helics_subscr_topics[source])
                message = ast.literal_eval(msg)
                if message['destination'] == self.name_helics:
                    return (message)
                else:
                    return None
            except:
                pass

    def helics_put(self, topic, message):
        """Send a message to a particular topic over the helics bus.

        Args:
            topic: the topic to publish the message on
            message: the message to send
        """
        helics.helicsPublicationPublishString(
            self.helics_pub_topics[topic], str(message))

    def update_helics_time(self, next_timestep):
        """Retrieve the next timestep in the helics simulation.

        Args:
            next_timestep: the requested timestep from helics
        """
        return helics.helicsFederateRequestTime(self.combo_federate, next_timestep)

    def receive_from_endpoints(self):
        """Retrieve any waiting messages from the agent's helics endpoints.

        Returns:
            a list of any messages that were waiting 
        """
        all_msg = []

        for key, endpoint in self.helics_endpoints.items():
            if helics.helicsEndpointHasMessage(endpoint):
                while True:
                    msg = helics.helicsEndpointGetMessage(endpoint)
                    if msg.data == "":
                        break
                    all_msg.append(msg)
        return (all_msg)

    def send_endpoint_message(self, endpoint, message, destination):
        """Send the specified message to the specified endpoint.

        Args:
            endpoint: the name of the endpoint
            message: the message
            destination: the intended destination
        """
        helics.helicsEndpointSendBytesTo(
            self.helics_endpoints[endpoint], message, destination)
