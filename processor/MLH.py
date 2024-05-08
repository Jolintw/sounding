import numpy as np

def find_MLH(P, PT, qv):
    
    dP = -(P[1:] - P[:-1])
    dP[dP==0] = np.nan
    dPT = PT[1:] - PT[:-1]
    dqv = qv[1:] - qv[:-1]
    P_diff_to_sfc = -(P[1:] - P[0])
    PT_diff_to_sfc = PT[1:] - PT[0]
    qv_diff_to_sfc = qv[1:] - qv[0]
    mask1 = np.logical_and(dPT/dP > 0.1, dqv/dP < -0.1)
    mask2 = np.logical_and(PT_diff_to_sfc > 0.2, qv_diff_to_sfc < -0.5)
    mask3 = dPT/dP > PT_diff_to_sfc/P_diff_to_sfc
    mask3 = np.logical_and(mask3, dqv/dP < qv_diff_to_sfc/P_diff_to_sfc)
    total_mask = np.logical_and(mask1, mask2)
    total_mask = np.logical_and(mask3, total_mask)
    ind = np.arange(dP.shape[0], dtype=int)
    ind = np.min(ind[total_mask])
    return ind