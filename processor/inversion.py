import numpy as np
from mypkgs.processor.numericalmethod import central_diff
from processor.layerfunction import Layer

def find_inversion_layer(PT, H, cloud_mask):
    """
    Heffter method (Heffter 1980; Sivaraman et al. 2013)
    PT: K
    H: meter
    """
    dPTdH = central_diff(PT, H)
    inversion_mask = dPTdH > 0.005
    inversion_mask = np.logical_and(inversion_mask, ~cloud_mask)
    inversion_layer = Layer()
    inversion_layer.find_layers_from_1Dmask(inversion_mask)
    if inversion_layer.layer_number != 0:
        inversion_layer.get_bottom_top_value(H, postfix="H")
        inversion_layer.get_bottom_top_value(PT, postfix="PT")
        inversion_layer.get_max_value_in_layer(dPTdH, prefix="dPTdH")
        inversion_layer.get_max_ind_in_layer(dPTdH, prefix="dPTdH")
        inversion_layer.thickness  = inversion_layer.top_H - inversion_layer.bottom_H
        inversion_layer.PBL_ind    = Heffter_PBL_index(PT, H, inversion_layer)
        inversion_layer.PBL_height = H[inversion_layer.PBL_ind]
    return inversion_layer

def Heffter_PBL_index(PT, H, inversion_layer):
    for i_layer in range(inversion_layer.layer_number):
        ti = inversion_layer.top_ind[i_layer] + 1
        bi = inversion_layer.bottom_ind[i_layer] - 1
        diff = PT[ti] - PT[bi]
        if diff < 2:
            continue
        PT_now = PT[bi:ti+1]
        PT_difftobottom = PT_now - PT_now[0]
        ind = np.arange(PT_now.shape[0], dtype=int)
        ind = np.min(ind[PT_difftobottom >= 2]) + bi
        if H[ind] > 4000:
            break
        return ind
    print("no inversion layer PT diff > 2 K")
    dPTdH = central_diff(PT, H)
    mask = inversion_layer.get_mask_of_layer(PT)
    dPTdH_inlayer = dPTdH.copy()
    dPTdH_inlayer[np.logical_not(mask)] = np.nan
    dPTdH_inlayer[H > 4000] = np.nan
    ind = np.nanargmax(dPTdH_inlayer)
    return ind
