import numpy as np
from variable.pathconfig import EDT, ST1, ST2
from reader.ST   import STreader
from reader.RS41 import RS41reader 
from reader.MIDAS_averaged_reader import read_minute_met_data_bridge, time_average

from processor.cloudlayer import find_cloud_layer
from processor.MLH import find_MLH
from processor.smooth5hPa import smooth_5hPa
from processor.inversion import find_inversion_layer
from processor.surface_correction import correct_Psfc


surface_average_time_range = 600 # second
def readall(datatype, surface=None):
    """
    read all data of specified datatype
    datatype: RS41_EDT, ST_L4p, ST_L4, ST_L1
    surface: "bridge" default=None
    """
    if surface == "bridge":
        surface_data = read_minute_met_data_bridge()
    else:
        surface_data = None
    RD, filelist = get_reader_and_filelist(datatype)
    varslist = []
    soundingtimelist = []
    print("read file of {:s} ...".format(datatype))
    for file in filelist:
        # print(file)
        if not file.is_file():
            continue
        vardict = RD.read(file, datatype=datatype)
        if not vardict:
            continue
        if np.nanmin(vardict["P"]) > 500 or np.nanmax(vardict["P"]) < 950:
            print("under 500 hPa")
            continue
        varslist.append(vardict)
        soundingtimelist.append(RD.get_nearest_hour(varslist[-1]))
        # print(soundingtimelist[-1])
    datadict = {}
    inds = [ind for _,ind in sorted(zip(soundingtimelist, list(range(len(soundingtimelist)))))]
    print("smooth the sounding")
    datadict["vars"] = [smooth_5hPa(varslist[ind]) for ind in inds]
    
    datadict["soundingtime"] = sorted(soundingtimelist)
    datadict["release_time"] = [STreader.getfirsttime(vardict) for vardict in datadict["vars"]]
    if surface_data:
        datadict["vars_sfc"] = [time_average(surface_data, surface_data["time"], time.timestamp(), surface_average_time_range) for time in datadict["release_time"]]
        datadict["vars"] = [correct_Psfc(vars, vars_sfc) for vars, vars_sfc in zip(datadict["vars"], datadict["vars_sfc"])]
    else:
        datadict["vars_sfc"] = []
    
    print("find cloud ...")
    datadict["cloud_layer"] = [find_cloud_layer(RH=vars["RH"]/100, H=vars["height"]) for vars in datadict["vars"]]
    print("find inversion ...")
    tempzip = zip(datadict["vars"], datadict["cloud_layer"])
    datadict["inversion_layer"] = [find_inversion_layer(PT=vars["PT"], H=vars["height"], cloud_mask=cloud.get_mask_of_layer(vars["PT"])) for vars, cloud in tempzip]
    print("find MLH ...")
    datadict["MLH_ind"] = [find_MLH(vars["P"], vars["PT"], vars["qv"]*1000) for vars in datadict["vars"]]
    # if datadict["vars_sfc"]:
    #     tempzip = zip(datadict["vars"], datadict["vars_sfc"])
    #     datadict["MLH_ind"] = [find_MLH(vars["P"], vars["PT"], vars["qv"]*1000, vsfc["P"], vsfc["PT"]) for vars, vsfc in tempzip]
    # else:
    #     datadict["MLH_ind"] = [find_MLH(vars["P"], vars["PT"], vars["qv"]*1000) for vars in datadict["vars"]]
    return datadict

def get_reader_and_filelist(datatype):
    if datatype == "RS41_EDT":
        RD = RS41reader(EDT)
        filelist = RD.filelist
    else:
        if datatype == "ST_L4p":
            RD = STreader(ST1)
            filelist = RD.getL4p_PBLlist()
            RD = STreader(ST2)
            filelist = filelist + RD.getL4p_PBLlist()
        elif datatype == "ST_L4":
            RD = STreader(ST1)
            filelist = RD.getfilelist("L4_PBL.eol")
            RD = STreader(ST2)
            filelist = filelist + RD.getfilelist("L4_PBL.eol")
        elif datatype == "ST_L1":
            RD = STreader(ST1)
            filelist = RD.getfilelist("L1.csv")
            RD = STreader(ST2)
            filelist = filelist + RD.getfilelist("L1.csv")
        else:
            raise Exception("datatype \"{:s}\" is not exist.".format(datatype))
    return RD, filelist

def get_cotime_datas(datas):
    cotime = []
    soundingtimestamp_0 = _get_shortest_time(datas)
    for t in soundingtimestamp_0:
        flag = True
        for data in datas.values():
            flag = flag and t_in_tlist(t, data["soundingtimestamp"])
            if not flag:
                break
        if flag:
            cotime.append(t)
    new_datas = {}
    for key, data in datas.items():
        new_datas[key] = {varkey:[] for varkey in data}
    for key, data in datas.items():
        new_data = new_datas[key]
        for t in cotime:
            tind = find_tind_in_tlist(t, data["soundingtimestamp"])
            for varkey in data:
                new_data[varkey].append(data[varkey][tind])
    for varkey in data:
        if isinstance(new_data[varkey][0], (int, float)):
            new_data[varkey] = np.array(new_data[varkey])
    return new_datas

def _get_shortest_time(datas):
    templen = np.inf
    for data in datas.values():
        if templen > len(data["soundingtimestamp"]):
            soundingtimestamp_0 = data["soundingtimestamp"]
            templen = len(soundingtimestamp_0)
    return soundingtimestamp_0

def t_in_tlist(t, tlist):
    tlist = np.array(tlist)
    return np.any(np.abs(t - tlist) < 600)

def find_tind_in_tlist(t, tlist):
    tlist = np.array(tlist)
    return np.argmin(np.abs(t - tlist))