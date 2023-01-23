#from dav_kafka_python.producer import PythonProducer
#from dav_kafka_python.configuration import Configuration
import random
import json
import getopt
import ast
import datetime
import logging
import os
import pathlib
import pickle
import sqlite3
import sys
import time
from io import StringIO

import numpy as np
import pandas as pd

import datetime as dt
from federateaccesspoint import federateagent

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOGFILE = str(dt.datetime.now()).replace(
    ":", "_").replace(" ", "_").replace(".", "_")


# Control center intera
# cts with simulations, sqlite database, and front end app via sqlite

class ControlCenter(federateagent):
    """
    Control center class
    """

    def __init__(self, config_dict):
        super(ControlCenter, self).__init__(
            name=config_dict['name'], feeder_num=0, starttime=config_dict['starttime'], endtime=config_dict['stoptime'], agent_num=0, config_dict=config_dict)
        self.config_dict = config_dict
        self.use_dash_frontend = config_dict["use_dash_frontend"]
        # Parameters
        self.KAFKA = config_dict["KAFKA"]

        # Running on eagle
        # self.amr_wind_folder = '/scratch/pfleming/c2c/amr_wind_demo'
        if self.KAFKA:
            # Kafka topic :
            self.topic = config_dicf["KAFKA_TOPIC"]
            print("KAFKA topic", self.topic)
            config = Configuration(env_path='./.env')
            self.python_producer = PythonProducer(config)
            self.python_producer.connect()

        # Uncomment if running local
        self.amr_wind_folder = 'local_amr_wind_demo'
        if self.use_dash_frontend:
            self.get_signals_from_front_end = self.get_signals_from_front_end_dash
        else:
            self.get_signals_from_front_end = self.get_signals_from_front_end_none

        # self.num_turbines = 8
        self.time_delta = 1.

        # Initializations
        self.current_timestamp = datetime.datetime.now()
        self.sim_time_s = 0  # Initialize to 0
        self.time_rate_s = self.time_delta  # Initialize to expectation
        # self.power_button_val = False

        # Set up the logger
        # Useful for when running on eagle
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M',
                            filename='log_control_center.log',
                            filemode='w')
        logger = logging.getLogger("control_center")

        # Perhaps a small hack to also send log to the terminal outout
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        #  Make an announcement
        logger.info("Control Center Starting Up...")

        # Get the AMRWind info
        amr_wind_input = os.path.join(self.amr_wind_folder, 'input.i')
        with open(amr_wind_input) as fp:
            Lines = fp.readlines()

            # Find the actuators
            for line in Lines:
                if 'Actuator.labels' in line:
                    turbine_labels = line.split()[2:]
                    self.num_turbines = len(turbine_labels)

            self.num_turbines = 2
            aa = [f"power_{i}" for i in range(self.num_turbines)]
            xyz = ",".join(aa)
            bb = [f"turbine_wd_direction_{i}" for i in range(self.num_turbines)]
            zyx = ",".join(bb)
            with open(f'{LOGFILE}.csv', 'a') as filex:
                filex.write('helics_time' + ',' + 'AMRwind_time' + ',' +
                            'AMRWind_speed' + ',' + 'AMRWind_direction' + ',' + xyz+ ',' +zyx + os.linesep)

            # Find the diameter
            for line in Lines:
                if 'rotor_diameter' in line:
                    self.D = float(line.split()[-1])

            # Get the turbine locations
            turbine_locations = []
            for label in turbine_labels:
                for line in Lines:
                    if 'Actuator.%s.base_position' % label in line:
                        locations = tuple([float(f)
                                          for f in line.split()[-3:-1]])
                        turbine_locations.append(locations)
            self.turbine_locations = turbine_locations

        logger.info('There are %d turbines, with diameter %.1f' %
                    (self.num_turbines, self.D))

        # Set up the control_center database
        logger.info("Making the control_center database...")
        self.control_center_database_filename = pathlib.Path(
            __file__).parent / 'control_center.db'

        # Initialize the sqlite database file
        if os.path.exists(self.control_center_database_filename):
            logger.info("...Deleting previous database file")
            os.remove(self.control_center_database_filename)

        # Get a connection and cursor to create the data table
        with sqlite3.connect(self.control_center_database_filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con_cc:

            # Get a cursor and set up data table
            cur_cc = con_cc.cursor()

            # Create the main data table
            logger.info("...Initiating data_table")
            cur_cc.execute(
                "CREATE TABLE data_table (timestamp TIMESTAMP, sim_time_s REAL, time_rate_s REAL,source_system TEXT, data_type TEXT, data_label TEXT, value REAL)")

        # Set up the front_end database
        logger.info("Making the front_end database...")
        self.front_end_database_filename = pathlib.Path(
            __file__).parent / 'front_end.db'

        # Initialize the front_end sqlite database file
        if os.path.exists(self.front_end_database_filename):
            logger.info("...Deleting previous front end database file")
            os.remove(self.front_end_database_filename)

        # Get a connection and cursor to create the front_end data table
        with sqlite3.connect(self.front_end_database_filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con_front:

            # Get a cursor and set up data table
            cur_front = con_front.cursor()

            # Create the front_end_table
            logger.info("...Initiating front_end_table")
            cur_front.execute(
                "CREATE TABLE front_end_table (timestamp TIMESTAMP, data_type TEXT, data_label TEXT, value REAL)")
            # con_front.commit()

        # Save the logger
        self.logger = logger

        # Post the turbine locations
        #for t_idx, t in enumerate(self.turbine_locations):
            #self.insert_value(self.sim_time_s, self.time_rate_s,
                              #'control_center', 'x_loc', 't_%d' % t_idx, t[0])
            #self.insert_value(self.sim_time_s, self.time_rate_s,
                              #'control_center', 'y_loc', 't_%d' % t_idx, t[1])

    def get_signals_from_front_end_none(self):

            self.logger.info("Not using wind speed and direction from the front end")
            self.wind_speed_front_end = 8
            self.wind_direction_front_end = 250

            self.input_method = "precursor" 
    def get_signals_from_front_end_dash(self):

        self.logger.info(
            "...Getting input_method, wind speed and direction from front end")
        statement = f'SELECT * from front_end_table order by timestamp;'
        with sqlite3.connect(self.front_end_database_filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con_front:
            df_front_end = pd.read_sql_query(statement, con_front)
            num_rows_from_front_end = df_front_end.shape[0]

            # Loop until we have at least two records
            while num_rows_from_front_end < 2:
                df_front_end = pd.read_sql_query(statement, con_front)
                num_rows_from_front_end = df_front_end.shape[0]
                #time.sleep(0.5)

        # Get the most recent input method and save
        input_method = df_front_end[df_front_end.data_type ==
                                    'input_method']['data_label'].values[-1]
        self.logger.info("...Current Data Method: {}".format(input_method))

        # Pull out wind speed and direction (most recent)
        wind_speed_front_end = df_front_end[df_front_end.data_type ==
                                            'wind_speed']['value'].values[-1]
        wind_direction_front_end = df_front_end[df_front_end.data_type ==
                                                'wind_direction']['value'].values[-1]

        self.logger.info("...Wind speed and direction received: {}, {}".format(
            wind_speed_front_end, wind_direction_front_end))

        # Save these values
        self.input_method = input_method
        self.wind_speed_front_end = wind_speed_front_end
        self.wind_direction_front_end = wind_direction_front_end

    def set_wind_speed_direction(self):
        # Get the wind speed and direction, dependent on the input_method

        if self.input_method == 'dash':
            self.logger.info(
                "... Setting wind speed and direction based on manual inputs from dash")
            self.wind_speed = self.wind_speed_front_end
            self.wind_direction = self.wind_direction_front_end

        elif self.input_method == 'nwtc':
            self.logger.info(
                "... Setting wind speed and direction based on m2 tower at wind site")
            self.wind_speed, self.wind_direction = self.get_nwtc_wind_data()

    def get_nwtc_wind_data(self):
        """ Access the M2 Tower latest data and return wind_dir and wind_speed """

        # Website info
        # INTERNAL VERSION
        website_root = "http://midc.nrel.gov/apps/data_api.pl?site=NWTC"
        # PUBLIC VERSION
        # website_root = "https://midcdmz.nrel.gov/apps/data_api.pl?site=NWTC"

        # Read data directly into pandas
        df_nwtc = pd.read_csv(website_root)

        # Make a new timestamp column
        # Signals given are the year, day of year, MST (hour/minute code)
        df_nwtc['minute'] = df_nwtc['MST'] % 100  # Minute are last two digits
        # hours are first two digits
        df_nwtc['hour'] = np.floor(df_nwtc['MST'] / 100.)
        df_nwtc['timestamp_mst'] = pd.to_datetime(
            df_nwtc['Year'] * 10000000 + df_nwtc['DOY'] * 10000 + df_nwtc['hour']*100 + df_nwtc['minute'], format='%Y%j%H%M')

        # Grab the most recent values
        # local_time = df_nwtc['timestamp_mst'].values[-1]
        wind_speed = df_nwtc['Avg Wind Speed @ 80m [m/s]'].values[-1]
        # turbulence_intensity = df_nwtc['Turbulence Intensity @ 80m'].values[-1]
        wind_direction = df_nwtc['Avg Wind Direction @ 80m [deg]'].values[-1]
        # irradiance = df_nwtc['Direct Normal [W/m^2]'].values[-1]

        # Force the wind direction into certain limits
        lim_range = [240, 300]
        while ((wind_direction < lim_range[0]) or (wind_direction > lim_range[1])):

            if wind_direction < lim_range[0]:
                wind_direction = lim_range[0] + lim_range[0] - wind_direction
            if wind_direction > lim_range[1]:
                wind_direction = lim_range[1] - (wind_direction - lim_range[1])

        #logger.info("NWTC data grab {}, {}, {}, {}, {}".format(local_time, wind_speed, turbulence_intensity, wind_direction, irradiance))
        # print(local_time, wind_speed, turbulence_intensity, wind_direction, irradiance)
        self.logger.info("NWTC wind speed: {}, direction: {}".format(
            wind_speed, wind_direction))
        return wind_speed, wind_direction

    def insert_value(self, sim_time_s, time_rate_s, source_system, data_type, data_label, value):

        # Define the insert query
        insertQuery = "INSERT INTO data_table VALUES (?, ?, ?, ?, ?, ?, ?);"

        # Build the tupe of values to add
        tuple_to_add = (self.current_timestamp, sim_time_s,
                        time_rate_s, source_system, data_type, data_label, value)

        timeout = 10
        for x in range(0, timeout):
            try:
                with sqlite3.connect(self.control_center_database_filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con_cc:

                    # Get a cursor to con_cc database
                    cur = con_cc.cursor()
                    cur.execute(insertQuery, tuple_to_add)
            except:
                #time.sleep(0.1)  # Wait 100ms
                continue
            break
        else:
            with sqlite3.connect(self.control_center_database_filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con_cc:
                # Get a cursor to con_cc database
                cur = con_cc.cursor()
                cur.execute(insertQuery, tuple_to_add)

    # def main_loop(self):
    def run(self):

        # Before entering main loop make initial connection to AMR-Wind and front end
        # and send the wind speed and direction

        # Get wind speed and direction from front end
        self.logger.info(
            "Waiting for intial wind speed and wind direction from front end")
        self.get_signals_from_front_end()

        # Set the wind speed and direction based on input mode
        self.set_wind_speed_direction()

        # Now pass the initial wind speed and wind direction for AMRWind to use in
        # 0th time step
        self.logger.info("... waiting for initial connection from AMRWind")
        # self.zmq_server.send(np.array([self.wind_speed, self.wind_direction]))
        list(self.pub.values())[0].publish(str("[-1,-1,-1]"))
        self.logger.info(" #### Entering main loop #### ")

        # Initialize the turbine power array
        turbine_power_array = np.zeros(self.num_turbines)

        # Inside a while loop # TODO ADD STOP CONDITION
        # while True:
        while self.currenttime < (self.endtime - self.starttime + 1):

            # Recieve the time step turbine powers and echoed wind speed and direction
            # (Note on first call this will be mostly uninitialized information to be ignored)
            # sim_time_s_amr_wind, wind_speed_amr_wind, wind_direction_amr_wind, turbine_power_array = self.zmq_server.receive()
            # sim_time_s_amr_wind, wind_speed_amr_wind, wind_direction_amr_wind = self.zmq_server.receive()
            # sim_time_s_amr_wind, wind_speed_amr_wind, wind_direction_amr_wind = self.zmq_server.receive()
            # print("CURRENTTIME ",self.get_currenttime())
            tmp = self.helics_get_all()
            if tmp != {}:
                subscription_value = self.process_subscription_event(tmp)
                sim_time_s_amr_wind, wind_speed_amr_wind, wind_direction_amr_wind = subscription_value[
                    :3]
                turbine_power_array = subscription_value[3:3+self.num_turbines]
                turbine_wd_array = subscription_value[3+self.num_turbines:]
                self.wind_speed = wind_speed_amr_wind
                self.wind_direction = wind_direction_amr_wind 


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

            # self.zmq_server.send(np.array([self.wind_speed, self.wind_direction]))
            self.process_periodic_publication()
            if self.KAFKA:
                key = json.dumps({"key": "wind_tower"})
                value = json.dumps({"helics_time": self.currenttime, "bucket": "wind_tower", "AMRWind_speed": wind_speed_amr_wind,
                                    "AMRWind_direction": wind_direction_amr_wind, "AMRWind_time": sim_time_s_amr_wind})
                self.python_producer.write(key=key, value=value,
                                           topic=self.topic, token='test-token')

            # Update the time rate using a sort of lazy filtering
            self.time_rate_s = 0.5 * self.time_rate_s + 0.5 * \
                (datetime.datetime.now() - self.current_timestamp).total_seconds()

            # Update the timestamp
            self.current_timestamp = datetime.datetime.now()
            # self.logger.info("Current timestamp: {}".format(self.current_timestamp) )

            # For now the simulation time is whatever amr_wind says it is
            self.sim_time_s = sim_time_s_amr_wind
            # self.logger.info("Simulation time is now: %.1f" % self.sim_time_s)

            # Insert into database recevied wind speed and direction values to control_center_table
            #self.insert_value(self.sim_time_s, self.time_rate_s,
                              #'control_center', 'wind_speed', 'wind_speed', self.wind_speed)
            #self.insert_value(self.sim_time_s, self.time_rate_s, 'control_center',
                              #'wind_direction', 'wind_direction', self.wind_direction)

            # Insert values from AMRWind
            #self.insert_value(sim_time_s_amr_wind, self.time_rate_s,
                              #'amr_wind', 'wind_speed', 'wind_speed', wind_speed_amr_wind)
            #self.insert_value(sim_time_s_amr_wind, self.time_rate_s, 'amr_wind',
                              #'wind_direction', 'wind_direction', wind_direction_amr_wind)

            # Turbine powers
            if len(turbine_power_array) == 0:
                turbine_power_array = np.ones(self.num_turbines)*-1.0
            for t in range(self.num_turbines):
                print("T, power array: ", t, turbine_power_array,
                      " num turbines ", self.num_turbines)
                #self.insert_value(sim_time_s_amr_wind, self.time_rate_s, 'amr_wind',
                               #   'turbine_power', 't%d' % t, turbine_power_array[t])
                if self.KAFKA:
                    keyname = f"wind_turbine_{t}"
                    key = json.dumps({"key": keyname})
                    value = json.dumps({"helics_time": self.currenttime, "bucket":  keyname, "turbine_wd_direction" : turbine_wd_array[t]	 ,"power": turbine_power_array[
                        t], "AMRWind_speed": wind_speed_amr_wind, "AMRWind_direction": wind_direction_amr_wind, "AMRWind_time": sim_time_s_amr_wind})
                    self.python_producer.write(
                        key=key, value=value, topic=self.topic, token='test-token')

            aa = [str(xx) for xx in turbine_power_array]
            xyz = ",".join(aa)
            bb = [str(xx) for xx in turbine_wd_array]
            zyx = ",".join(bb)
            with open(f'{LOGFILE}.csv', 'a') as filex:
                filex.write(str(self.currenttime) + ',' + str(sim_time_s_amr_wind) + ',' + str(
                    wind_speed_amr_wind) + ',' + str(wind_direction_amr_wind) + ',' + xyz + ','+ zyx +  os.linesep)
            # Just as a test read the database
            with sqlite3.connect(self.control_center_database_filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con_cc:
                statement = f'SELECT * from data_table order by timestamp;'
                df_test = pd.read_sql_query(statement, con_cc)

            self.sync_time_helics(self.deltat)

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


def launch_control_center():
    config = {
        "name": "controlcenter",
        "use_dash_frontend": False,
        "KAFKA": False,
        "KAFKA_topics": "EMUV1py",
        "amrwindmodel": {
        },
        "helics": {
            "deltat": 1,
            "subscription_topic": [
                "status"

            ],
            "publication_topic": [
                "control"

            ],
            "endpoints": [
            ]
        },

        "publication_interval": 1,
        "endpoint_interval": 1,
        "starttime": 0,
        "stoptime": 36000,
        "Agent": "ControlCenter"

    }
    obj = ControlCenter(config)
    obj.run_helics_setup()
    obj.enter_execution(function_targets=[],
                        function_arguments=[[]])


launch_control_center()

