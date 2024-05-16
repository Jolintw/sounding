from datetime import datetime as dd
import numpy as np
from mypkgs.processor.tools import sort_list_by_another_list
from variable.pathconfig import MIDAS_EXT_BRIDGE, MIDAS_EXT_NTU


def read_extracted_MIDAS_metbridge():
    datas = {}
    times = {}
    for key in MIDAS_EXT_BRIDGE:
        datas[key] = np.array([])
        times[key] = np.array([])
        pathnow = MIDAS_EXT_BRIDGE[key]
        filelist = list(pathnow.glob("*"))
        filelist_time = [dd.strptime(file.parts[-1], "%y%b%d%H%M%S") for file in filelist]
        filelist = sort_list_by_another_list(list_to_sort=filelist, ref_list=filelist_time)
        filelist_time = sorted(filelist_time)
        for file in filelist:
            var, time = np.loadtxt(file, delimiter=",", skiprows=3, unpack=True)
            datas[key] = np.append(datas[key], var)
            times[key] = np.append(times[key], time)
    return datas, times

def read_extracted_MIDAS_metntu():
    varlist = ["T", "RH", "time"] # this order is important
    datas = {key:np.array([]) for key in varlist}
    filelist = list(MIDAS_EXT_NTU.glob("*"))
    filelist_time = [dd.strptime(file.parts[-1], "%y%b%d%H%M%S") for file in filelist]
    filelist = sort_list_by_another_list(list_to_sort=filelist, ref_list=filelist_time)
    filelist_time = sorted(filelist_time)
    for file in filelist:
        var = np.loadtxt(file, delimiter=",", skiprows=3, unpack=True)
        for i_key, key in enumerate(varlist):
            datas[key] = np.append(datas[key], var[i_key])
    return datas