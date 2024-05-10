import numpy as np
from mypkgs.processor.numericalmethod import central_diff
from processor.layerfunction import Layer

def find_inversion_layer(PT, H, cloud_mask):
    """
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
        inversion_layer.thickness = inversion_layer.top_H - inversion_layer.bottom_H
    return inversion_layer

