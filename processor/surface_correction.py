import numpy as np
release_height = 6

def correct_Psfc(vardict, var_sfc):
    sfc_P = var_sfc["P"]
    if np.isnan(sfc_P):
        return vardict
    P = vardict["P"]
    mask = P < sfc_P
    for key in vardict:
        vardict[key] = vardict[key][mask]
    bias = vardict["height"][0] - release_height
    vardict["height"] = vardict["height"] - bias
    return vardict