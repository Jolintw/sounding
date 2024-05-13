import numpy as np

from mypkgs.processor.timetools import timestamp_to_datetime

class Soundingreader:
    def getfirsttime(self, vardict):
        return timestamp_to_datetime(vardict["timestamp"][0])
    
    def get_nearest_hour(self, vardict, hour_intv=3):
        firsttime = self.getfirsttime(vardict).timestamp()
        second_intv = hour_intv*3600
        newtime = np.round(firsttime / second_intv) * second_intv
        nearest_hour = timestamp_to_datetime(newtime)
        return nearest_hour 