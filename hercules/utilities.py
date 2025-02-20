import os
import numpy as np
from scipy.interpolate import interp1d, RegularGridInterpolator
import yaml

class Loader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]

        super().__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))

        with open(filename, "r") as f:
            return yaml.load(f, self.__class__)


Loader.add_constructor("!include", Loader.include)


def load_yaml(filename, loader=Loader):
    if isinstance(filename, dict):
        return filename  # filename already yaml dict
    with open(filename) as fid:
        return yaml.load(fid, loader)

def load_perffile(perffile):
    perffuncs = {}
    
    with open(perffile) as pfile:
        for line in pfile:
            # Read Blade Pitch Angles (degrees)
            if "Pitch angle" in line:
                pitch_initial = np.array(
                    [float(x) for x in pfile.readline().strip().split()]
                )
                pitch_initial_rad = (
                    pitch_initial * np.deg2rad(1)
                )  # degrees to rad            -- should this be conditional?

            # Read Tip Speed Ratios (rad)
            if "TSR" in line:
                TSR_initial = np.array(
                    [float(x) for x in pfile.readline().strip().split()]
                )

            # Read Power Coefficients
            if "Power" in line:
                pfile.readline()
                Cp = np.empty((len(TSR_initial), len(pitch_initial)))
                for tsr_i in range(len(TSR_initial)):
                    Cp[tsr_i] = np.array(
                        [float(x) for x in pfile.readline().strip().split()]
                    )
                perffuncs["Cp"] = RegularGridInterpolator((TSR_initial, pitch_initial_rad),
                Cp, bounds_error=False, fill_value=None)

            # Read Thrust Coefficients
            if "Thrust" in line:
                pfile.readline()
                Ct = np.empty((len(TSR_initial), len(pitch_initial)))
                for tsr_i in range(len(TSR_initial)):
                    Ct[tsr_i] = np.array(
                        [float(x) for x in pfile.readline().strip().split()]
                    )
                perffuncs["Ct"] = RegularGridInterpolator((TSR_initial, pitch_initial_rad),
                Ct, bounds_error=False, fill_value=None)

            # Read Torque Coefficients
            if "Torque" in line:
                pfile.readline()
                Cq = np.empty((len(TSR_initial), len(pitch_initial)))
                for tsr_i in range(len(TSR_initial)):
                    Cq[tsr_i] = np.array(
                        [float(x) for x in pfile.readline().strip().split()]
                    )
                perffuncs["Cq"] = RegularGridInterpolator((TSR_initial, pitch_initial_rad),
                Cq, bounds_error=False, fill_value=None)

    return perffuncs
