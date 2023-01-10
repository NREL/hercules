import pandas as pd
from dav_kafka_python.producer import PythonProducer
from dav_kafka_python.configuration import Configuration
import sys
import os
import json

import argparse
parser = argparse.ArgumentParser()


topic = "EmupyV0.1"
print("KAFKA topic", topic)
config = Configuration(env_path='./.env')
python_producer = PythonProducer(config)
python_producer.connect()


parser.add_argument("-l", "--logfile", dest = "lfile", help="point to logfile to reproduce kafka stream", type=str)
args = parser.parse_args()

print( "Using logfile : {} ".format(
        args.lfile
        ))

LFILE = args.lfile

df = pd.read_csv(LFILE)

for i,x in df.iterrows():
    print(x)
    key = json.dumps({"key": "wind_tower"})
    value = {"helics_time": x['helics_time'] , "bucket": "wind_tower", "AMRWind_speed": x["AMRWind_speed"] ,
                    "AMRWind_direction": x["AMRWind_direction"], "AMRWind_time": x["AMRwind_time"]}
    python_producer.write(key=key, value=json.dumps(value),
                        topic=topic, token='test-token')
    power_keys = [xx for xx in x.keys() if "power_" in xx]
    for yy in power_keys:
        idx = yy.split("_")[-1]
        key_power = json.dumps({"key": f"wind_turbine_{idx}"})
        val_power = dict(value)
        val_power.update({"power" : x[yy]})
        python_producer.write(key=key_power, value=json.dumps(val_power),
                    topic=topic, token='test-token')
        