import numpy as np
from mypkgs.processor.numericalmethod import RightAngleInterpolater

def get_normalized_height(height, MLH_ind, inversion_layer):
    inversion_height = height[inversion_layer.PBL_ind]
    MLH              = height[MLH_ind]
    
    D = inversion_height - MLH
    zeta = np.zeros_like(height)
    if D <= 0:
        print("MLH higher than (or equal to) inversion")
        return zeta + np.nan
    zeta = height / MLH
    zeta[height > MLH] = 1 + (height[height > MLH] - MLH) / D
    return zeta

def equidistance_normalized_coordinate(vardict, normalized_height):
    new_vardict = {}
    if np.any(np.isnan(normalized_height)):
        for key in vardict:
            new_vardict[key] = np.zeros_like(vardict[key]) + np.nan
        return new_vardict
    new_zeta = np.linspace(0, 3, 601)
    RIA = RightAngleInterpolater(X=normalized_height, newX=new_zeta, equidistance=False, newX_out_of_X=True)
    for key in vardict:
        new_vardict[key] = RIA.interpolate(vardict[key])
    new_vardict["normalized_height"] = new_zeta
    return new_vardict
