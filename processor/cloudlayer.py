import numpy as np

Zhang2010RHtable = {}
Zhang2010RHtable["altitude"] = [0, 2e3, 6e3, 12e3]
Zhang2010RHtable["minRH"]  = [[0.92, 0.90], [0.90, 0.88], [0.88, 0.75], 0.75]
Zhang2010RHtable["maxRH"]  = [[0.95, 0.93], [0.93, 0.90], [0.90, 0.80], 0.80]
Zhang2010RHtable["interRH"] = [[0.84, 0.82], [0.80, 0.78], [0.78, 0.70], 0.70]
    
def find_cloud_layer(RH, H):
    """
    method from Zhang (2010) https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2010JD014030
    :param RH: relative humidity from sounding, range 0~1
    :param H: Height from sounding, unit: meter
    """
    moist_layer, RHthreshold = find_moist_layer(RH, H)
    cloud_layer = _cloud_layer_limitation(moist_layer, RHthreshold)
    cloud_layer = _combine_cloud_layers(cloud_layer, RHthreshold, RH)
    if not cloud_layer:
        return {"top_ind":[], "top_H":[], "bottom_ind":[], "bottom_H":[], "thickness":[]}
    return cloud_layer
    

def find_moist_layer(RH, H):
    """
    method from Zhang (2010) https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2010JD014030
    :param RH: relative humidity, range 0~1
    :param H: Height, unit: meter
    """
    RHTC = RHThresholdCalculator(Zhang2010RHtable)
    RHthreshold = RHTC.get_RH_threshold(H)
    moist_layer = _find_layers_exceed_RHthreshold(RH, RHthreshold, H)
    moist_layer = _moist_layers_limitation(moist_layer)
    return moist_layer, RHthreshold

def make_cloud_mask(cloud_layer, H):
    cloud_mask = np.zeros_like(H, dtype=bool)
    for cloud in range(len(cloud_layer["thickness"])):
        bi = cloud_layer["bottom_ind"][cloud]
        ti = cloud_layer["top_ind"][cloud]
        cloud_mask[bi:ti+1] = True
    return cloud_mask

def _find_layers_exceed_RHthreshold(RH, RHthreshold, H):
    RH_exceedminRH = RH > RHthreshold["minRH"]
    RH_exceedminRH[np.isnan(RH)] = np.nan
    RH_exceedminRH_int = RH_exceedminRH.astype(int)
    RH_exceedminRH_int = np.append([0], RH_exceedminRH_int) # pad a dry layer to the ground
    RH_exceedminRH_int = np.append(RH_exceedminRH_int, [0]) # pad a dry layer to the end of sounding
    diff = RH_exceedminRH_int[1:] - RH_exceedminRH_int[:-1] 
    # 1 in diff means next element is first element of Trues in RH_exceedminRH
    # -1 means the last element in Trues
    # but index n of diff corresponding to n+1 of sounding
    moist_layer = {}
    if np.all(diff == 0):
        return moist_layer
    
    full_ind = np.arange(len(RH)+1, dtype=int)
    moist_layer["bottom_ind"]   = full_ind[diff==1]
    moist_layer["top_ind"]      = full_ind[diff==-1] - 1
    moist_layer["RH_max"]       = np.array([np.nanmax(RH[bi:ti+1]) for bi, ti in zip(moist_layer["bottom_ind"], moist_layer["top_ind"])])
    moist_layer["bottom_H"]     = H[moist_layer["bottom_ind"]]
    moist_layer["top_H"]        = H[moist_layer["top_ind"]]
    moist_layer["thickness"]    = moist_layer["top_H"] - moist_layer["bottom_H"]
    return moist_layer

def _moist_layers_limitation(moist_layer):
    if not moist_layer: # empty
        return moist_layer
    thickness_limit = 400
    bottom_limit = 120
    valid_moist_layer_mask = moist_layer["thickness"] >= thickness_limit
    valid_moist_layer_mask = np.logical_and(moist_layer["bottom_H"] >= bottom_limit, valid_moist_layer_mask)
    for key in moist_layer:
        moist_layer[key] = moist_layer[key][valid_moist_layer_mask]
    return moist_layer

def _cloud_layer_limitation(moist_layer, RHthreshold):
    cloud_layer = {}
    if not moist_layer: # empty
        return cloud_layer
    if len(moist_layer["thickness"])==0:
        return cloud_layer
    top_limit = 280
    valid_cloud_layer_mask = moist_layer["RH_max"] > RHthreshold["maxRH"][moist_layer["bottom_ind"]]
    valid_cloud_layer_mask = np.logical_and(moist_layer["top_H"] >= top_limit, valid_cloud_layer_mask)
    for key in moist_layer:
        cloud_layer[key] = moist_layer[key][valid_cloud_layer_mask]
    return cloud_layer

def _combine_cloud_layers(cloud_layer, RHthreshold, RH):
    if not cloud_layer:
        return cloud_layer
    
    inter_layer = _create_inter_layer(cloud_layer, RHthreshold, RH)
    combine_mask = inter_layer["thickness"] < 300
    combine_mask = np.logical_or(inter_layer["RH_min"] > inter_layer["interRH_max"], combine_mask)
    combine_mask = np.append(combine_mask, [0]) # length of inter_layer is n-1
    
    new_cloud_layer = {key:[] for key in cloud_layer}
    temp_layer = {}
    for i_cloud, ifcombine in enumerate(combine_mask):
        now_layer = {key:cloud_layer[key][i_cloud] for key in cloud_layer}
        temp_layer = _add_layer(temp_layer, now_layer)
        if not ifcombine:
            for key in cloud_layer: 
                new_cloud_layer[key].append(temp_layer[key])
            temp_layer = {}
    return new_cloud_layer

def _create_inter_layer(cloud_layer, RHthreshold, RH):
    inter_layer = {"thickness":[], "RH_min":[], "interRH_max":[]}
    for i_layer in range(len(cloud_layer["thickness"]) - 1):
        inter_layer["thickness"].append(cloud_layer["bottom_H"][i_layer+1] - cloud_layer["top_H"][i_layer])
        bottom_ind = cloud_layer["top_ind"][i_layer] + 1 # bottom_ind of inter layer
        top_ind = cloud_layer["bottom_ind"][i_layer+1] - 1 # top_ind of inter layer
        inter_layer["RH_min"].append(np.nanmin(RH[bottom_ind:top_ind+1]))
        inter_layer["interRH_max"].append(RHthreshold["interRH"][bottom_ind])
    for key in inter_layer:
        inter_layer[key] = np.array(inter_layer[key])
    return inter_layer

def _add_layer(lower_layer, upper_layer):
    if not lower_layer:
        return upper_layer
    lower_layer["top_ind"] = upper_layer["top_ind"]
    lower_layer["top_H"] = upper_layer["top_H"]
    lower_layer["thickness"] = lower_layer["top_H"] - lower_layer["bottom_H"]
    return lower_layer


class RHThresholdCalculator:
    def __init__(self, RHtable):
        self.RHtable = RHtable

    def get_RH_threshold(self, H):
        if not isinstance(H, np.ndarray):
            H = np.array([H])
        result = np.zeros_like(H)
        self._create_ind_of_corresponding_altrange(H)
        self._create_linear_interpolation_ratio(H)
        result = {}
        for RHname in ["minRH", "maxRH", "interRH"]:
            result[RHname] = self._get_corresponding_RH(H, self.RHtable[RHname])
            if result[RHname].shape[0] == 1:
                result[RHname] = result[RHname][0]

        return result

    def _create_ind_of_corresponding_altrange(self, H):
        altitude = self.RHtable["altitude"]
        alt_ind = np.zeros_like(H, dtype=int)
        alt_ind[H >= altitude[-1]] = -1
        for i_alt in range(len(altitude)-1):
            temp_mask = np.logical_and(H <= altitude[i_alt+1], H >= altitude[i_alt])
            alt_ind[temp_mask] = i_alt
        self.alt_ind = alt_ind
        return alt_ind

    def _create_linear_interpolation_ratio(self, H):
        altitude = self.RHtable["altitude"]
        alt_ind  = self.alt_ind
        ratio_lower = np.zeros_like(H)
        ratio_upper = np.zeros_like(H)
        for i_alt in range(len(altitude)-1):
            H_now = H[alt_ind == i_alt]
            ratio_lower[alt_ind == i_alt] = (altitude[i_alt+1] - H_now) / (altitude[i_alt+1] - altitude[i_alt])
            ratio_upper[alt_ind == i_alt] = (H_now - altitude[i_alt]) / (altitude[i_alt+1] - altitude[i_alt])
        self.interpol_ratio = [ratio_lower, ratio_upper]
        return [ratio_lower, ratio_upper]

    def _get_corresponding_RH(self, H, RHref):
        alt_ind  = self.alt_ind
        ratio    = self.interpol_ratio
        RH = np.zeros_like(H)
        RH[alt_ind == -1] = RHref[-1]
        for i_alt, RHrefnow in enumerate(RHref[:-1]):
            altmask = alt_ind == i_alt
            RH[altmask] = ratio[0][altmask] * RHrefnow[0] + ratio[1][altmask] * RHrefnow[1]
        return RH