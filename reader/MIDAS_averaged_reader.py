import netCDF4 as nc
import numpy as np
from atmospkg.calculation import saturation_mixingratio, potential_temperature
from variable.pathconfig import MIDAS_MIN_MEAN_BRIDGE


def read_minute_met_data_bridge():
    data = {}
    DS = nc.Dataset(MIDAS_MIN_MEAN_BRIDGE)
    for key in DS.variables:
        data[key] = DS[key][...]
    data["qvs"] = saturation_mixingratio(T=data["T"], P=data["P"], Tunit="degC", Punit="hPa")
    data["qv"] = data["qvs"] * data["RH"] / 100.0
    data["PT"] = potential_temperature(T=data["T"], P=data["P"], Tunit="degC", Punit="hPa")
    return data

def time_average(data: dict, time_of_data, time_to_average: float, average_range):
    """
    return average of data in (time_to_average - average_range/2 ~ time_to_average + average_range/2)
    average_range: same unit as time_of_data and time_to_average
    """
    if not data:
        return {}
    newdata = {}
    average_mask = (time_of_data >= time_to_average - average_range/2)
    average_mask = np.logical_and(average_mask, time_of_data <= time_to_average + average_range/2)
    for key in data:
        newdata[key] = np.nanmean(np.array(data[key][average_mask]))
    return newdata