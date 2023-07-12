
import numpy as np
import json

from hercules.federateaccesspoint import federateagent

class EmuComms(federateagent):

    def __init__(self, input_dictionary):
        
        print('--')
        # print(input_dictionary)

        # Save timt step
        self.dt = input_dictionary['dt']

        # Grab py sim details
        self.hercules_comms_dict = input_dictionary['hercules_comms']
        self.hercules_helics_dict = self.hercules_comms_dict ['helics']
        self.helics_config_dict = self.hercules_comms_dict['helics']['config']

        # Write the time step into helics config dict
        self.helics_config_dict['helics']['deltat'] = self.dt

        # TODO: Make sure to understand what this does
        super(EmuComms, self).__init__(
            name=self.helics_config_dict['name'], 
            feeder_num=0, 
            starttime=self.helics_config_dict['starttime'],
            endtime=self.helics_config_dict['stoptime'], 
            agent_num=0, 
            config_dict=self.helics_config_dict
        )

        # TODO: Store other things
        self.use_dash_frontend = self.helics_config_dict["use_dash_frontend"]
        self.KAFKA = self.helics_config_dict["KAFKA"]

        # TODO Copied direct from control_center.py but not actually ready yet
        # if self.KAFKA:
        #     # Kafka topic :
        #     self.topic = self.helics_config_dict["KAFKA_TOPIC"]
        #     print("KAFKA topic", self.topic)
        #     config = Configuration(env_path='./.env')
        #     self.python_producer = PythonProducer(config)
        #     self.python_producer.connect()

        # AMR wind files
        # Grab py sim details
        self.amr_wind_dict = self.hercules_comms_dict['amr_wind']

        self.n_amr_wind = len(self.amr_wind_dict )
        self.amr_wind_names = list(self.amr_wind_dict.keys())

        # Save information about amr_wind simulations
        for amr_wind_name in self.amr_wind_names:
            self.amr_wind_dict[amr_wind_name].update(
                self.read_amr_wind_input(
                    self.amr_wind_dict[amr_wind_name]['amr_wind_input_file']
                )
            )

        #TODO For now, need to assume for simplicity there is one and only
        # one AMR_Wind simualtion
        self.num_turbines = self.amr_wind_dict[self.amr_wind_names[0]]['num_turbines']
        self.rotor_diameter = self.amr_wind_dict[self.amr_wind_names[0]]['rotor_diameter']
        self.turbine_locations = self.amr_wind_dict[self.amr_wind_names[0]]['turbine_locations']
        self.turbine_labels = self.amr_wind_dict[self.amr_wind_names[0]]['turbine_labels']

        # TODO In fugure could cover multiple farms
        # Initialize the turbine power array
        self.turbine_power_array = np.zeros(self.num_turbines)
        self.amr_wind_dict[self.amr_wind_names[0]]['turbine_powers'] = np.zeros(self.num_turbines)

        #TODO Could set up logging here

        #TODO Set interface comms to either dash or kenny's front end

        #TODO Set comms to non-helics based things like http polling

        # TODO not positive if this is the right place but I think it is
        # Hold here and wait for AMR Wind to respond
        # Note we're passing a few intiial wind speed and direction things
        # but we can come back to all that

        # FORMER CODE
        # self.logger.info("... waiting for initial connection from AMRWind")
        # list(self.pub.values())[0].publish(str("[-1,-1,-1]"))
        # self.logger.info(" #### Entering main loop #### ")

        

        #TODO In future code that doesnt insist on AMRWInd can make this optional
        print("... waiting for initial connection from AMRWind")
        list(self.pub.values())[0].publish(str("[-1,-1,-1]"))
        print(" #### Entering main loop #### ")


    def get_hercules_comms_dict(self):

        return self.hercules_comms_dict

    def step(self, input_dict):

        # 

        # Calls individual helics elements (eg amrwind, aries, front end?)
        # Recieve the time step turbine powers and echoed wind speed and direction
        # (Note on first call this will be mostly uninitialized information to be ignored)
        
        #TODO: What exactly does this do?  
        tmp = self.helics_get_all()
        if tmp != {}:

            #TODO Describe this line
            subscription_value = self.process_subscription_event(tmp)

            #TODO Parse returns from AMRWind
            sim_time_s_amr_wind, wind_speed_amr_wind, wind_direction_amr_wind = subscription_value[
                :3]
            turbine_power_array = subscription_value[3:3+self.num_turbines]
            turbine_wd_array = subscription_value[3+self.num_turbines:]
            self.wind_speed = wind_speed_amr_wind
            self.wind_direction = wind_direction_amr_wind

            #TODO F-Strings
            print("=======================================")
            print("AMRWindTime:", sim_time_s_amr_wind)
            print("AMRWindSpeed:", wind_speed_amr_wind)
            print("AMRWindDirection:", wind_direction_amr_wind)
            print("AMRWindTurbinePowers:", turbine_power_array)
            print(" AMRWIND number of turbines here: ", self.num_turbines)
            print("AMRWindTurbineWD:", turbine_wd_array)
            print("=======================================")
        else:
            print("Did not get any subs!! ", tmp)
            sim_time_s_amr_wind, wind_speed_amr_wind, wind_direction_amr_wind = [
                0, 0, 0]
            turbine_power_array = np.zeros(self.num_turbines).tolist()
            turbine_wd_array = np.zeros(self.num_turbines).tolist()
            self.wind_speed = wind_speed_amr_wind
            self.wind_direction = wind_direction_amr_wind

        #TODO Comment what this does
        self.process_periodic_publication() 

        if self.KAFKA:
            key = json.dumps({"key": "wind_tower"})
            value = json.dumps({"helics_time": self.currenttime, "bucket": "wind_tower", "AMRWind_speed": wind_speed_amr_wind,
                                "AMRWind_direction": wind_direction_amr_wind, "AMRWind_time": sim_time_s_amr_wind})
            self.python_producer.write(key=key, value=value,
                                        topic=self.topic, token='test-token')


        # Store turbine powers back to the dict
        #TODO hard-coded for now assuming only one AMR-WIND
        self.amr_wind_dict[self.amr_wind_names[0]]['turbine_powers'] = turbine_power_array
        self.turbine_power_array = turbine_power_array

        self.sync_time_helics(self.dt)

    def process_subscription_event(self, msg):
        # process data from subscription
        print(
            f"{self.name}, {self.get_currenttime()} subscribed to message {msg}", flush=True)

        try:
            return list(ast.literal_eval(msg))

        except Exception as e:
            print("SUBSCRIPTIION ERROR !!! ", e, flush=True)
            return [0, 0, 0] + [0 for t in range(self.num_turbines)] + [0 for t in range(self.num_turbines)]

    def process_periodic_publication(self):
        # Periodically publish data to the surrpogate

        self.get_signals_from_front_end()
        self.set_wind_speed_direction()

        #yaw_angles = [270 for t in range(self.num_turbines)]
        yaw_angles = [240 for t in range(self.num_turbines)]
        # log these in kafka

        #yaw_angles[1] = 260

        tmp = np.array([self.get_currenttime(), self.wind_speed,
                       self.wind_direction] + yaw_angles).tolist()

        print("publishing  ", tmp)

        list(self.pub.values())[0].publish(str(tmp))

    def process_endpoint_event(self, msg):
        pass

    def process_periodic_endpoint(self):
        pass

    def read_amr_wind_input(self, amr_wind_input):

        # TODO this function is ugly and uncommented

        #TODO Initialize to empty in case doesn't run
        # Probably want a file not found error instead
        return_dict = {}

        with open(amr_wind_input) as fp:
            Lines = fp.readlines()

            # Find the actuators
            for line in Lines:
                if 'Actuator.labels' in line:
                    turbine_labels = line.split()[2:]
                    num_turbines = len(turbine_labels)

            # self.num_turbines = 2
            # print("Numer of turbine isn marwind: ", self.num_turbines)
            # aa = [f"power_{i}" for i in range(num_turbines)]
            # xyz = ",".join(aa)
            # bb = [f"turbine_wd_direction_{i}" for i in range(
            #     num_turbines)]
            # zyx = ",".join(bb)
            # with open(f'{LOGFILE}.csv', 'a') as filex:
            #     filex.write('helics_time' + ',' + 'AMRwind_time' + ',' +
            #                 'AMRWind_speed' + ',' + 'AMRWind_direction' + ',' + xyz + ',' + zyx + os.linesep)

            # Find the diameter
            for line in Lines:
                if 'rotor_diameter' in line:
                    D = float(line.split()[-1])

            # Get the turbine locations
            turbine_locations = []
            for label in turbine_labels:
                for line in Lines:
                    if 'Actuator.%s.base_position' % label in line:
                        locations = tuple([float(f)
                                          for f in line.split()[-3:-1]])
                        turbine_locations.append(locations)
        
            return_dict = {
                'num_turbines':num_turbines,
                'turbine_labels':turbine_labels,
                'rotor_diameter':D,
                'turbine_locations':turbine_locations
            }

            # print(return_dict)
        return return_dict

