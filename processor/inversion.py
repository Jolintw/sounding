import numpy as np
from mypkgs.processor.numericalmethod import central_diff
from processor.layerfunction import Layer

def find_inversion_layer(PT, H, cloud_mask):
    """
    PT: K
    H: meter
    """
    inversion_mask = central_diff(PT, H) > 0.005
    inversion_mask = np.logical_and(inversion_mask, ~cloud_mask)
    inversion_layer = Layer()
    inversion_layer.find_layers_from_1Dmask(inversion_mask)
    if inversion_layer.layer_number != 0:
        inversion_layer.bottom_H  = H[inversion_layer.bottom_ind]
        inversion_layer.top_H     = H[inversion_layer.top_ind]
        inversion_layer.bottom_PT = PT[inversion_layer.bottom_ind]
        inversion_layer.top_PT    = PT[inversion_layer.top_ind]
        inversion_layer.thickness = inversion_layer.top_H - inversion_layer.bottom_H
    else:
        return inversion_layer
    return inversion_layer

