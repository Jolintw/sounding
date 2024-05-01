import numpy as np
from atmospkg.calculation import saturation_mixingratio, potential_temperature
from datetime import datetime as dd

release_height = 6 # the height of the place to release balloon (meter)

class STreader:
    def __init__(self, STpath = None):
        if not STpath is None:
            self.getdirlist(STpath)

    def readL4(self, filepath):
        varnamedict = {"time":0, "P":4, "T":5, "Td":6, "RH":7, "U":8, "V":9, "WS":10, "WD":11, "Lon":14, "lat":15, "height":13}
        vardict = {}
        P = np.loadtxt(filepath, skiprows=14, unpack=True, usecols=(4))
        if np.nanmin(P) > 950:
            print("bad launch")
            return vardict
        time = np.loadtxt(filepath, skiprows=14, unpack=True, usecols=(0))
        launch_index = self._findlaunchindex(time)
        for key, value in varnamedict.items():
            vardict[key] = np.loadtxt(filepath, skiprows=14+launch_index, unpack=True, usecols=(value))
        vardict["qv"]  = saturation_mixingratio(vardict["Td"], vardict["P"], Tunit="degC", Punit="hPa")
        #vardict["qvs"] = saturation_mixingratio(vardict["T"], vardict["P"], Tunit="degC", Punit="hPa")
        vardict["PT"] = potential_temperature(vardict["T"], vardict["P"], Tunit="degC", Punit="hPa")
        vardict["height"] = self._height_modify(vardict["height"], release_height)
        f = open(filepath)
        lines = f.readlines()
        f.close()
        timestr = lines[5].split(":", 1)[1].strip()
        fmt = "%Y, %m, %d, %H:%M:%S%z"
        zerotime = dd.strptime(timestr+"+0000", fmt).timestamp()
        vardict["timestamp"] = zerotime + vardict["time"]
        return vardict
    
    def getfirsttime(self, vardict):
        return dd.fromtimestamp(vardict["timestamp"][0])
    
    def getL4p_PBLlist(self, STpath = None):
        filename = "L4p_PBL.eol"
        return self.getfilelist(filename, STpath)

    def getfilelist(self, filename, STpath = None):
        if STpath is None:
            STlist = self.STlist
        else:
            STlist = self.getdirlist(STpath)
        return [ST / filename for ST in STlist]
    
    def getdirlist(self, STpath):
        if list(STpath.glob("*"))[0].parts[-1] == "ST":
            STpath = STpath / "ST"
        self.STpath = STpath
        STlist = list(STpath.glob("*"))
        self.STlist = STlist
        return STlist
    
    def _findlaunchindex(self, time):
        dts = time[1:] - time[:-1]
        for i_dt, dt in enumerate(dts):
            if dt < 1200:
                if np.mean(dts[i_dt+1:i_dt+11]) < 10:
                    return i_dt

    def _height_modify(self, height, release_height):
        bias = height[0] - release_height
        return height - bias
