from variable.pathconfig import MIDAS_EXT_NTU
from reader.MIDAS_extracted_reader import read_extracted_MIDAS_metbridge, read_extracted_MIDAS_metntu
from datetime import datetime as dd
import numpy as np

data_resolution = 60 # second
least_sample_number = 10

def takemean(var, time):
    averaged_var = []
    starttime = time[0] - dd.fromtimestamp(time[0]).second + 60
    endtime   = time[-1] - dd.fromtimestamp(time[-1]).second - 60
    newtime = np.arange(starttime, endtime+1, data_resolution)
    for t in newtime:
        mask = (time >= t) & (time < t + data_resolution)
        if np.sum(mask) > least_sample_number:
            averaged_var.append(np.mean(var[mask]))
        else:
            averaged_var.append(np.nan)
    return averaged_var, newtime

bridge_datas, bridge_times = read_extracted_MIDAS_metbridge()
# ntu_datas    = read_extracted_MIDAS_metntu()
bridge_datas["P"] = bridge_datas["P"] * 1000 # bar to mbar (hPa)
averaged_bridge_datas = {}
new_bridge_times = {}

for key in bridge_datas:
    print(key)
    var  = bridge_datas[key]
    time = bridge_times[key]
    averaged_bridge_datas[key], new_bridge_times[key] = takemean(var, time)

# cut var to same length
time0 = [value[0] for value in new_bridge_times.values()]
timelast = [value[-1] for value in new_bridge_times.values()]
for key in bridge_datas:
    timemask = (new_bridge_times[key] > max(time0)) & (new_bridge_times[key] < min(timelast))
    averaged_bridge_datas[key] = averaged_bridge_datas[key][timemask]
    new_bridge_times[key]      = new_bridge_times[key][timemask]
