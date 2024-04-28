import numpy as np
from atmospkg.calculation import saturation_mixingratio, wswd_to_uv
from datetime import datetime as dd
import os 

class RS41reader:
    def __init__(self, RS41path = None):
        if not RS41path is None:
            self.getfilelist(RS41path)

    def readEDT(self, filepath):
        varnamedict = {"time":0, "height":1, "P":2, "T":3, "RH":4, "WS":5, "WD":6}
        vardict = {}
        tempname = "temptxt"
        try:
            asc = np.loadtxt(filepath, delimiter=',', skiprows=4)[:,-1]
        except:
            f  = open(filepath)
            fo = open(tempname,"w")
            lines = f.readlines()
            newlines = []
            for i_line, line in enumerate(lines):
                if "//" in line:
                    print("row {:d} is invalid".format(i_line))
                    continue
                newlines.append(line)
            fo.writelines(newlines)
            fo.close()
            filepath = tempname
            asc = np.loadtxt(filepath, delimiter=',', skiprows=4)[:,-1]
        
        mask = asc >= 0
        for key, value in varnamedict.items():
            vardict[key] = np.loadtxt(filepath, skiprows=4, unpack=True, usecols=(value))[mask]
        vardict["qvs"] = saturation_mixingratio(vardict["T"], vardict["P"], Tunit="degC", Punit="hPa")
        vardict["qv"] = vardict["qvs"] * vardict["RH"]
        vardict["U"], vardict["V"] = wswd_to_uv(vardict["ws"], vardict["wd"])
        
        f = open(filepath)
        line = f.readline()
        timestr = lines[0].split(":", 1)[1].strip()
        f.close()
        fmt = "%d/%m/%Y %H:%M:%S%z"
        zerotime = dd.strptime(timestr+"+0000", fmt).timestamp()
        vardict["timestamp"] = zerotime + vardict["time"]
        
        if os.path.isfile(tempname):  
            os.remove(tempname)

    def getfilelist(self, RS41path):
        self.RS41path = RS41path
        filelist = list(RS41path.glob("*"))
        self.filelist = filelist
        return filelist