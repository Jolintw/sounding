import numpy as np
from atmospkg.calculation import saturation_mixingratio, wswd_to_uv, potential_temperature
from datetime import datetime as dd
from mypkgs.processor.timetools import timestamp_to_datetime
import os 

class RS41reader:
    """
    timestamp: second
    P: hPa
    T: degC
    PT: K
    qv: kg/kg
    RH: %
    height: m
    U, V: m/s
    """
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
            filepath = self._create_tempfile_without_nonnumericstr()
            asc = np.loadtxt(filepath, delimiter=',', skiprows=4)[:,-1]
        
        mask = (asc >= 0)
        for key, value in varnamedict.items():
            vardict[key] = np.loadtxt(filepath, delimiter=',', skiprows=4, unpack=True, usecols=(value))[mask]
        vardict["qvs"] = saturation_mixingratio(vardict["T"], vardict["P"], Tunit="degC", Punit="hPa")
        vardict["qv"]  = vardict["qvs"] * vardict["RH"] / 100
        vardict["PT"]  = potential_temperature(vardict["T"], vardict["P"], Tunit="degC", Punit="hPa")
        vardict["U"], vardict["V"] = wswd_to_uv(vardict["WS"], vardict["WD"], wdunit="deg")
        vardict["timestamp"] = vardict["time"] + self.getzerotimefromfile(filepath)
        
        if os.path.isfile(tempname):  
            os.remove(tempname)
        
        return vardict

    def getfilelist(self, RS41path):
        self.RS41path = RS41path
        filelist = list(RS41path.glob("*"))
        self.filelist = filelist
        return filelist
    
    def getfirsttime(self, vardict):
        return timestamp_to_datetime(vardict["timestamp"][0])
    
    def _create_tempfile_without_nonnumericstr(self, filepath, tempfilename):
        f  = open(filepath)
        fo = open(tempfilename,"w")
        lines = f.readlines()
        newlines = []
        for i_line, line in enumerate(lines):
            if "//" in line:
                print("row {:d} is invalid".format(i_line))
                continue
            newlines.append(line)
        fo.writelines(newlines)
        fo.close()
        f.close()
        return tempfilename
    
    def getzerotimefromfile(self, filepath):
        f = open(filepath)
        line = f.readline()
        timestr = line.split(":", 1)[1].strip()
        f.close()
        fmt = "%d/%m/%Y %H:%M:%S%z"
        zerotime = dd.strptime(timestr+"+0000", fmt).timestamp()
        return zerotime
    
    def get_nearest_hour(self, vardict, hour_intv=3):
        firsttime = self.getfirsttime(vardict).timestamp()
        second_intv = hour_intv*3600
        newtime = np.round(firsttime / second_intv) * second_intv
        nearest_hour = timestamp_to_datetime(newtime)
        return nearest_hour 
