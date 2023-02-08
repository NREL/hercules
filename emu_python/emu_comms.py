
from emu_python.federateaccesspoint import federateagent

class EmuComms(federateagent):

    def __init__(self, input_dictionary):
        
        print('--')
        # print(input_dictionary)

        # Save timt step
        self.dt = input_dictionary['dt']

        # Grab py sim details
        self.emu_comms_dict = input_dictionary['emu_comms']
        self.emu_helics_dict = self.emu_comms_dict ['helics']
        self.helics_config_dict = self.emu_comms_dict['helics']['config']

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
        self.amr_wind_dict = self.emu_comms_dict['amr_wind']

        self.n_amr_wind = len(self.amr_wind_dict )
        self.amr_wind_names = self.amr_wind_dict.keys()

        # Save information about amr_wind simulations
        for amr_wind_name in self.amr_wind_names:
            self.amr_wind_dict[amr_wind_name].update(
                self.read_amr_wind_input(
                    self.amr_wind_dict[amr_wind_name]['amr_wind_input_file']
                )
            )

        #TODO Could set up logging here

        #TODO Set interface comms to either dash or kenny's front end

        #TODO Set comms to non-helics based things like http polling





    def step(self):

        # The first thing for now is to wait for connection from AMR Wind
        # Now pass the initial wind speed and wind direction for AMRWind to use in
        # 0th time step
        self.logger.info("... waiting for initial connection from AMRWind")
        list(self.pub.values())[0].publish(str("[-1,-1,-1]"))
        self.logger.info(" #### Entering main loop #### ")

        # Calls individual helics elements (eg amrwind, aries, front end?)

        outputs = None

        return outputs
    
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
            aa = [f"power_{i}" for i in range(num_turbines)]
            xyz = ",".join(aa)
            bb = [f"turbine_wd_direction_{i}" for i in range(
                num_turbines)]
            zyx = ",".join(bb)
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



