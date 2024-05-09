import numpy as np
from mypkgs.processor.numericalmethod import RightAngleInterpolater

def create_Parray_asnewX(intv, maxP, minP):
    Parray = np.flip(np.arange(int(2000/intv)) * intv)
    Parray = Parray[Parray <= maxP]
    Parray = Parray[Parray >= minP]
    return Parray

def interpolate_by(vardict, Xname, newX, newname_postfix = ""):
    RAI = RightAngleInterpolater(X=vardict[Xname], newX=newX, equidistance=False)
    newvardict = {Xname+newname_postfix: newX}
    keys = list(vardict.keys())
    keys.remove(Xname)
    for key in keys:
        newvardict[key+newname_postfix] = RAI.interpolate(var=vardict[key])
    return newvardict