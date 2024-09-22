import numpy as np

def find_MLH(P, PT, qv, P_sfc=None, PT_sfc=None, qv_sfc=None):
    """
    ref: Wang (2024) https://journals.ametsoc.org/view/journals/mwre/152/9/MWR-D-23-0238.1.xml
    Note that Delta theta > 0.1 K (and Delta qv ...) in ref is difference between 2 data point but Delta is difference of 1 hPa (dtheta/dp) here
    P: hPa
    PT: K
    qv: g/kg
    """
    if P_sfc is None:
        P_sfc = P[0]
    if PT_sfc is None:
        PT_sfc = PT[0]
    if qv_sfc is None:
        qv_sfc = qv[0]
    Pmask = P < P_sfc
    cut_number = P.shape[0] - np.sum(Pmask)
    P = P[Pmask]
    PT = PT[Pmask]
    qv = qv[Pmask]
    dP = -(P[1:] - P[:-1])
    dP[dP==0] = np.nan
    dPT = PT[1:] - PT[:-1]
    dqv = qv[1:] - qv[:-1]
    P_diff_to_sfc = -(P[1:] - P_sfc)
    PT_diff_to_sfc = PT[1:] - PT_sfc
    qv_diff_to_sfc = qv[1:] - qv_sfc
    mask1 = np.logical_and(dPT/dP > 0.1, dqv/dP < -0.1)
    # mask1 = np.logical_and(dPT/dP > 0.05, dqv/dP < -0.05)
    mask2 = np.logical_and(PT_diff_to_sfc > 0.2, qv_diff_to_sfc < -0.5)
    mask3 = dPT/dP > PT_diff_to_sfc/P_diff_to_sfc
    mask3 = np.logical_and(mask3, dqv/dP < qv_diff_to_sfc/P_diff_to_sfc)
    total_mask = np.logical_and(mask1, mask2)
    total_mask = np.logical_and(mask3, total_mask)
    if not np.any(total_mask):
        raise Exception("can't find MLH")
    ind = np.arange(dP.shape[0], dtype=int)
    ind = np.min(ind[total_mask])
    return ind + cut_number