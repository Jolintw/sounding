import numpy as np
from datetime import datetime as dd

use_time = "INZDA" #"GPZDA"
met_ntu = "PORWIA"
met_bridge = "WIXDR"
def get_interest_lines(filepath, interest_list):
    f = open(filepath)
    lines = f.readlines()
    f.close()
    interest_lines = {key:[] for key in interest_list}
    line_indexs = {key:[] for key in interest_list}
    for i_lines, line in enumerate(lines):
        line_split = line.split(",")
        if len(line_split) < 3:
            continue
        key = line_split[2][1:]
        if key in interest_list:
            interest_lines[key].append(line.split(",", maxsplit=3)[-1])
            line_indexs[key].append(i_lines)
    return interest_lines, line_indexs

def readMIDAS(filepath, need_var= None):
    """
    need_var: met_bridge, met_ntu, met_cwb(not working)
    """
    if need_var is None:
        need_var = ["met_bridge", "met_ntu"]
    vars = {}
    print("readlines...")
    interest_lines, line_indexs = get_interest_lines(filepath, get_interest_list(need_var))
    print("get time...")
    timestamps = ZDA_to_timestamp(interest_lines[use_time])
    time_list_indexs = time_list_index(line_indexs)
    print("get data from lines...")
    if "met_bridge" in need_var:
        vars["met_bridge"] = read_met_bridge(interest_lines[met_bridge], time_list_indexs[met_bridge], timestamps)
    if "met_ntu" in need_var:
        vars["met_ntu"] = read_met_ntu(interest_lines[met_ntu], line_indexs, timestamps)
    return vars

def get_interest_list(need_var):
    interest_list = [use_time]
    if "met_bridge" in need_var:
        interest_list += [met_bridge]
    if "met_ntu" in need_var:
        interest_list += [met_ntu]
    return interest_list

def time_list_index(line_indexs, time_name=use_time):
    """
    line_indexs: index of lines
    time_list_indexs: index of time
    """
    time_index = np.array(line_indexs[time_name]) # index of lines
    keys = list(line_indexs.keys())
    keys.remove(time_name)
    keys.remove(met_ntu)

    time_list_indexs = {} # index of timelist
    for key in keys:
        time_list_indexs[key] = []
        i_time_list = 0
        time_ind_now = time_index[i_time_list]
        for line_ind in line_indexs[key]:
            while line_ind > time_ind_now:
                i_time_list += 1
                if i_time_list >= len(time_index):
                    i_time_list = len(time_index)
                    break
                time_ind_now = time_index[i_time_list]
            time_list_indexs[key].append(i_time_list - 1)
    return time_list_indexs

def ZDA_to_timestamp(time_lines):
    timestamps = []
    for line in time_lines:
        line_split = line.split(",")
        timestr = line_split[0][:6] + line_split[1] + line_split[2] + line_split[3] + "+0000"
        timestamps.append(dd.strptime(timestr, "%H%M%S%d%m%Y%z").timestamp())
    timestamps = np.array(timestamps)
    return timestamps

def read_met_bridge(varlines, index_of_timestamps, timestamps):
    data = {"P":[], "P_time":[], "H":[], "H_time":[], "G":[], "G_time":[]}
    # print(len(varlines))
    for i_line, line in enumerate(varlines):
        line_split = line.split(",")
        timestamp_ind = index_of_timestamps[i_line]
        varname = line_split[0]
        if timestamp_ind < 0:
            data[varname+"_time"].append(timestamps[0])
        else:
            data[varname+"_time"].append(timestamps[timestamp_ind])
        data[varname].append(float(line_split[1]))
    return data

def read_met_ntu(varlines, line_indexs, timestamps, time_name=use_time):
    data = {"RH":[], "T":[], "time":[]}

    zerotime_ntu = float(varlines[0].split(",")[1])
    zerotime_ZDA = _get_zerotime_ZDA(line_indexs, timestamps, time_name)

    for i_line, line in enumerate(varlines):
        line_split = line.split(",")
        data["time"].append(float(line_split[1]) - zerotime_ntu + zerotime_ZDA)
        # data["P"].append((float(line_split[3]) + 17589.98581) / 23.44782 ) # ?
        data["T"].append(-66.875 + 72.917 * float(line_split[4]) * 0.1 / 1000) # degC
        data["RH"].append(-12.5 + 41.667 * float(line_split[5]) * 0.1 / 1000) # %
    return data

def _get_zerotime_ZDA(line_indexs, timestamps, time_name):
    time_index = np.array(line_indexs[time_name])
    line_index_0 = line_indexs[met_ntu][0]
    zerotime_ZDAind = np.argmin(np.abs((time_index - line_index_0)))
    zerotime_ZDA = timestamps[zerotime_ZDAind]
    return zerotime_ZDA