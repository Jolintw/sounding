import numpy as np
from processor.interpolate import interpolate_by,  create_Parray_asnewX


def calculate_x(ax, xposition):
    xlim = ax.get_xlim()
    x = xlim[0] + (xlim[1] - xlim[0]) * xposition
    return x

def plot_MLH_line(plotter, vardict, MLH_ind, subplot_n=0, xposition=0, color="indigo"):
    """
    xposition: position of text in x axis range 0~1
    """
    ax = plotter.axs[subplot_n][0]
    textx = calculate_x(ax, xposition)
    MLH_P = vardict["P"][MLH_ind]
    line_MLH = plotter.hline(MLH_P, color=color, axn=(0,0))
    ax.text(textx, MLH_P+5, "MLH", verticalalignment="top", color=line_MLH[0].get_color(), fontsize=plotter.fontsize)

def plot_inversion_line(plotter, vardict, inversion_layer, subplot_n=0, xposition=0, color="dimgrey"):
    """
    xposition: position of text in x axis range 0~1
    """
    ax = plotter.axs[subplot_n][0]
    textx = calculate_x(ax, xposition)
    inversion_ind = inversion_layer.PBL_ind
    # strongest_inversion = np.argmax(inversion_layer.top_PT - inversion_layer.bottom_PT)
    # bottom_P = vardict["P"][inversion_layer.bottom_ind[strongest_inversion]]
    # top_P = vardict["P"][inversion_layer.top_ind[strongest_inversion]]
    # strongest_inversion_P = (bottom_P + top_P) / 2
    inversion_P = vardict["P"][inversion_ind]
    line_inv = plotter.hline(inversion_P, color=color, linestyle="dashed", axn=(subplot_n,0))
    ax.text(textx, inversion_P+5, "inversion", verticalalignment="top", color=line_inv[0].get_color(), fontsize=plotter.fontsize)

def plot_cloud_layer_mark(plotter, paintbox_1D, vardict, cloud_layer, subplot_n=0, xposition=0.84):
    top_P    = vardict["P"][cloud_layer.top_ind]
    bottom_P = vardict["P"][cloud_layer.bottom_ind]
    P_5 = create_Parray_asnewX(intv=5, maxP=np.nanmax(vardict["P"]), minP=450)
    P_5_cloud = np.array([])
    for top_P, bottom_P in zip(top_P, bottom_P):
        P_5_cloud = np.append(P_5_cloud, P_5[(P_5>top_P) * (P_5<bottom_P)])
    p = paintbox_1D.plotmark_y(Y=P_5_cloud, xposition=xposition, ax=plotter.axs[subplot_n][0], color="tab:blue")
    return p

def set_yticks(plotter, vardict, subplot_n=0, ifhticks = True):
    maxP = np.nanmax(vardict["P"])
    if maxP > 1000:
        levels = [1000, 925, 850, 800, 700]
    else:
        levels = [925, 850, 800, 700]

    vardict_stdlevel = interpolate_by(vardict=vardict, Xname="P", newX=np.array(levels))
    yticks_p = [maxP] + levels
    yticklabels_p = ["{:.1f}".format(ytick) for ytick in yticks_p]
    yticklabels_h = ["{:.1f}".format(vardict["height"][0])] + ["{:.1f}".format(ytick) for ytick in vardict_stdlevel["height"]]
    if (maxP - 1000) < 10 and maxP > 1000:
        yticklabels_p[0] = ""
        yticklabels_h[0] = ""

    plotter.set_yticks(yticks_p, yticklabels_p, axn = (subplot_n,0))
    if ifhticks:
        plotter.twin(xy="x")
        plotter.set_ylim(plotter.axs[subplot_n][0].get_ylim(), axn=(subplot_n, -1))
        plotter.set_yticks(yticks_p, yticklabels_h, axn = (subplot_n, -1))
