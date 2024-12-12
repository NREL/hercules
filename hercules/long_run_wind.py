# Implements the long run wind model for Hercules

import logging
import sys

# Set up the logger
# Useful for when running on eagle
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    filename="outputs/log_long_run_wind.log",
    filemode="w",
)
logger = logging.getLogger("long_run_wind")

# Perhaps a small hack to also send log to the terminal outout
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

#  Make an announcement
logger.info("Long-run Wind connecting to server")
