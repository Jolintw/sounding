from mypkgs.processor.numericalmethod import NonEquidistanceSmoother_1D

def smooth_5hPa(vardict, varnamelist = ["T", "U", "V", "qv", "RH", "qv"]):
    NES = NonEquidistanceSmoother_1D(vardict["P"], 5)
    newvardict = {}
    for var in varnamelist:
        newvardict[var] = NES.smooth(vardict[var])
    for var in ["P", "height", "timestamp"]:
        newvardict[var] = vardict[var]
    return newvardict