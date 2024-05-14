import numpy as np
from variable.pathconfig import EDT, ST1, ST2
from reader.ST   import STreader
from reader.RS41 import RS41reader 

from processor.cloudlayer import find_cloud_layer
from processor.MLH import find_MLH
from processor.smooth5hPa import smooth_5hPa
from processor.inversion import find_inversion_layer


def readall(datatype):
    """
    read all data of specified datatype
    datatype: RS41_EDT, ST_L4p, ST_L4, ST_L1
    """
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
    print("find cloud ...")
    datadict["cloud_layer"] = [find_cloud_layer(RH=vars["RH"]/100, H=vars["height"]) for vars in datadict["vars"]]
    print("find inversion ...")
    tempzip = zip(datadict["vars"], datadict["cloud_layer"])
    datadict["inversion_layer"] = [find_inversion_layer(PT=vars["PT"], H=vars["height"], cloud_mask=cloud.get_mask_of_layer(vars["PT"])) for vars, cloud in tempzip]
    print("find MLH ...")
    datadict["MLH_ind"] = [find_MLH(P=vars["P"], PT=vars["PT"], qv=vars["qv"]*1000) for vars in datadict["vars"]]
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