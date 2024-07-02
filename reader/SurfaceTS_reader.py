import numpy as np
from datetime import datetime as dd
# from variable.pathconfig import SFCTS
from variable.pathconfig import SFCTS_NC
import netCDF4 as nc


def readsct(filepath):
    varcolumndict = {"lat":3, "lon":4, "T90":5, "Salinity":6, "T":12}
    # T90 is new standard 
    timefmt = "%Y/%m/%d%H:%M:%S%z"
    time = np.loadtxt(filepath, dtype=str, skiprows=1, usecols=(1, 2))
    timelist = np.array([dd.strptime(t_day+t_sec+"+0000", timefmt).timestamp() for t_day, t_sec in zip(time[:,0], time[:,1])])
    data = {}
    for var, var_cn in varcolumndict.items():
        data[var] = np.loadtxt(filepath, skiprows=1, usecols=(var_cn,))
    print(dd.fromtimestamp(timelist[0]))
    data["timestamp"] = timelist
    return data

def read_Surfacewater_nc():
    ds = nc.Dataset(SFCTS_NC)
    data = {}
    for var in ds.variables:
        data[var] = ds[var][:]
    return data
