import numpy as np
from datetime import datetime as dd
from variable.pathconfig import STATION

def read_stationlist():
    infile = STATION
    vars = {"lat":3, "lon":4}
    data = {}
    data["name"] = np.loadtxt(STATION, delimiter=",", skiprows=2, dtype=str, usecols=(0,), unpack=True)
    timefmt = "%Y%m%d%H%M%z"
    starttime = np.loadtxt(STATION, delimiter=",", skiprows=2, dtype=str, usecols=(1,), unpack=True)
    data["starttime"] = [dd.strptime(time+"+0000", timefmt) for time in starttime]
    data["starttimestamp"] = [time.timestamp() for time in data["starttime"]]
    endtime = np.loadtxt(STATION, delimiter=",", skiprows=2, dtype=str, usecols=(2,), unpack=True)
    data["endtime"] = [dd.strptime(time+"+0000", timefmt) for time in endtime]
    data["endtimestamp"] = [time.timestamp() for time in data["endtime"]]
    for var, value in vars.items():
        data[var] = np.loadtxt(STATION, delimiter=",", skiprows=2, usecols=(value,), unpack=True)
    return data
