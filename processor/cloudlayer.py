import numpy as np

Zhang2010RHtable = {}
Zhang2010RHtable["altitude"] = [0, 2e3, 6e3, 12e3]
Zhang2010RHtable["minRH"]  = [[0.92, 0.90], [0.90, 0.88], [0.88, 0.75], 0.75]
Zhang2010RHtable["maxRH"]  = [[0.95, 0.93], [0.93, 0.90], [0.90, 0.80], 0.80]
Zhang2010RHtable["interRH"] = [[0.84, 0.82], [0.80, 0.78], [0.78, 0.70], 0.70]
    

def find_moist_layer(RH, H):
    """
    method from Zhang (2010) https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2010JD014030
    :param RH: relative humidity, range 0~1
    :param H: Height, unit: meter
    """

def find_cloud_layer():
    """
    method from Zhang (2010) https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2010JD014030
    :param RH: relative humidity from sounding, range 0~1
    :param H: Height from sounding, unit: meter
    """

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