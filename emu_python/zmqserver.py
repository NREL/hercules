# Copyright 2022 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# This file defines ZmqServer class and is re-used from code provided here:
# https://github.com/TUDelft-DataDrivenControl/SOWFA/blob/master/exampleCases/example.12.piso.NREL5MW.ADM.zmqSSC.python/ssc/zmqserver.py


import numpy as np
import zmq
from io import StringIO
import logging
logger = logging.getLogger("zmq_server")


class ZmqServer:
    def __init__(self, port, timeout=3600):
        self._port = port
        self._timeoutBufferSeconds = timeout

        self._last_message_sent_string = ""
        self._last_message_sent_data = []
        self._last_message_received_string = ""
        self._last_message_received_data = []

        self._status = "initialised"

        self._context = None
        self._socket = None
        self.connect()

    def connect(self):
        address = "tcp://*:{}".format(self._port)
        logger.info("Connecting to {}".format(address))
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.setsockopt(zmq.RCVTIMEO, self._timeoutBufferSeconds * 1000)
        self._socket.bind(address)
        self._status = "connected"
        logger.info("Connected.")

    def disconnect(self):
        logger.info("Disconnecting from tcp://*:{}".format(self._port))
        self._socket.close()
        logger.info("Disconnected.")

    def receive_initial(self):
        try:
            message = self._socket.recv()
        except zmq.Again as e:
            logger.error("Did not receive message - Timed out in {} seconds.".format(self._timeoutBufferSeconds))
            logger.error(e.strerror, exc_out=1)
            self.disconnect()
            raise TimeoutError

        # raw message contains a long useless tail with b'\x00' characters
        # split off the tail before decoding into a Python unicode string
        json_data = message.split(b'\x00', 1)[0].decode()
        received_data = np.loadtxt(StringIO(json_data), delimiter=' ')
        logger.debug("Received measurements: {}".format(received_data))

        self._last_message_received_string = json_data
        self._last_message_received_data = received_data

        # Split things up
        initial_code = received_data[0]


        return initial_code

    def receive(self):
        try:
            message = self._socket.recv()
        except zmq.Again as e:
            logger.error("Did not receive message - Timed out in {} seconds.".format(self._timeoutBufferSeconds))
            logger.error(e.strerror, exc_out=1)
            self.disconnect()
            raise TimeoutError

        # raw message contains a long useless tail with b'\x00' characters
        # split off the tail before decoding into a Python unicode string
        json_data = message.split(b'\x00', 1)[0].decode()
        received_data = np.loadtxt(StringIO(json_data), delimiter=' ')
        logger.debug("Received measurements: {}".format(received_data))

        self._last_message_received_string = json_data
        self._last_message_received_data = received_data

        # Split things up
        sim_time_s_amr_wind = received_data[0]
        wind_speed_amr_wind = received_data[1]
        wind_direction_amr_wind = received_data[2]
        # measurement_array = received_data[3:]

        return sim_time_s_amr_wind, wind_speed_amr_wind, wind_direction_amr_wind#, measurement_array




    def send(self, data_array):

        # Confirm data array is a 1d np array
        data_array = np.array(data_array)

        # Construct control signal array as expected by SOWFA
        print(data_array)
        string_data = ["{:.6f}".format(d) for d in data_array]
        string_send = " ".join(string_data)

        message = string_send.encode()
        self._socket.send(message, 0)
        logger.debug("Sent controls: {}".format(data_array))

        self._last_message_sent_string = string_send
        self._last_message_sent_data = data_array