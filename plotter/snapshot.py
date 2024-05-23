import numpy as np
from processor.interpolate import interpolate_by,  create_Parray_asnewX


def plot_variable(plotter, paintbox, varname, sub_num = 0, xlim = None, Yname = "P", **plotpars):
    if xlim:
        plotter.set_xlim(xlim=xlim, axn=(sub_num,varname))
    line2D = paintbox.plot(Xname=varname, Yname=Yname, ax=plotter.axs[sub_num][varname], label=varname)
    line2D[0].set(**plotpars)
    plotter.axs[sub_num][varname].tick_params(axis='x', colors=line2D[0].get_color())
    return line2D

def plot_MLH_line(plotter, vardict, MLH_ind, subplot_n=0, xposition=0, color="indigo"):
    """
    xposition: position of text in x axis range 0~1
    """
    ax = plotter.axs[subplot_n][0]
    textx = calculate_x(ax, xposition)
    MLH_P = vardict["P"][MLH_ind]
    line = plotter.hline(MLH_P, color=color, axn=(0,0))
    ax.text(textx, MLH_P+5, "MLH", verticalalignment="top", color=line[0].get_color(), fontsize=plotter.fontsize)

def plot_inversion_line(plotter, vardict, inversion_layer, subplot_n=0, xposition=0, color="dimgrey"):
    """
    xposition: position of text in x axis range 0~1
    """
    ax = plotter.axs[subplot_n][0]
    textx = calculate_x(ax, xposition)
    inversion_ind = inversion_layer.PBL_ind
    inversion_P = vardict["P"][inversion_ind]
    line = plotter.hline(inversion_P, color=color, linestyle="dashed", axn=(subplot_n,0))
    ax.text(textx, inversion_P+5, "inversion", verticalalignment="top", color=line[0].get_color(), fontsize=plotter.fontsize)

def plot_cloud_layer_mark(plotter, paintbox_1D, vardict, cloud_layer, subplot_n=0, xposition=0.84):
    top_P    = vardict["P"][cloud_layer.top_ind]
    bottom_P = vardict["P"][cloud_layer.bottom_ind]
    P_5 = create_Parray_asnewX(intv=5, maxP=np.nanmax(vardict["P"]), minP=450)
    P_5_cloud = np.array([])
    for top_P, bottom_P in zip(top_P, bottom_P):
        P_5_cloud = np.append(P_5_cloud, P_5[(P_5>top_P) * (P_5<bottom_P)])
    p = paintbox_1D.plotmark_y(Y=P_5_cloud, xposition=xposition, ax=plotter.axs[subplot_n][0], color="tab:blue")
    return p

def plot_LCL_line(plotter, LCL_P, subplot_n=0, xposition=0, color="pink"):
    """
    xposition: position of text in x axis range 0~1
    """
    ax = plotter.axs[subplot_n][0]
    textx = calculate_x(ax, xposition)
    line = plotter.hline(LCL_P, color=color, linestyle="dashed", axn=(subplot_n,0))
    ylim = ax.get_ylim()
    textshift = (ylim[1] - ylim[0]) / 60
    ax.text(textx, LCL_P-textshift, "LCL", verticalalignment="top", color=line[0].get_color(), fontsize=plotter.fontsize)

def plot_CTH_CBH_line(plotter, CTH, CBH, subplot_n=0, xposition=0, color="black"):
    """
    xposition: position of text in x axis range 0~1
    """
    ax = plotter.axs[subplot_n][0]
    textx = calculate_x(ax, xposition)
    line_CTH = plotter.hline(CTH, color=color, linestyle="dashed", axn=(subplot_n,0))
    line_CBH = plotter.hline(CBH, color=color, linestyle="dashed", axn=(subplot_n,0))
    ylim = ax.get_ylim()
    textshift = (ylim[1] - ylim[0]) / 60
    ax.text(textx, CTH-textshift, "CTH", verticalalignment="top", color=line_CTH[0].get_color(), fontsize=plotter.fontsize)
    ax.text(textx, CBH-textshift, "CBH", verticalalignment="top", color=line_CBH[0].get_color(), fontsize=plotter.fontsize)

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

def calculate_x(ax, xposition):
    xlim = ax.get_xlim()
    x = xlim[0] + (xlim[1] - xlim[0]) * xposition
    return x