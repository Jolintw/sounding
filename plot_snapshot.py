import numpy as np
from mypkgs.plotter.plotter import TwinPlotter
from mypkgs.plotter.paintbox import Paintbox_1D
from variable.pathconfig import SSPIC, SSPIC_SFC
from reader.read import readall
from reader.reader import Soundingreader
from processor.interpolate import interpolate_by, create_Parray_asnewX
from plotter.snapshot import plot_inversion_line, plot_MLH_line, set_yticks, plot_cloud_layer_mark, plot_LCL_line


datatype = "RS41_EDT" 
# datatype = "ST_L4p"
# datatype = "ST_L4"
# datatype = "ST_L1"

sfc_station = "bridge" #"bridge", None
data = readall(datatype, surface=sfc_station)

if sfc_station:
    picdir = SSPIC_SFC / sfc_station / datatype
else:
    picdir = SSPIC / datatype

for i_time, soundingtime in enumerate(data["soundingtime"]):
    vardict = data["vars"][i_time]
    if data["vars_sfc"]:
        vardict_sfc = data["vars_sfc"][i_time]
    else:
        vardict_sfc = {}
    print(soundingtime)
    firsttime = Soundingreader.getfirsttime(vardict)
    print(firsttime)

    cloud_layer     = data["cloud_layer"][i_time]
    inversion_layer = data["inversion_layer"][i_time]
    MLH_ind         = data["MLH_ind"][i_time]
    LCL_P           = data["LCL_P"][i_time]
    # print(LCL_P)
    newX            = create_Parray_asnewX(intv=10, maxP=np.nanmax(vardict["P"]), minP=700)
    vardict_P10     = interpolate_by(vardict=vardict, Xname="P", newX=newX)

    TP    = TwinPlotter(subfigsize_x = 12, subfigsize_y = 12, fontsize=30)
    Pb1   = Paintbox_1D(X=vardict, Y=vardict, fig=TP.fig)
    Pb1_2 = Paintbox_1D(X=vardict_P10, Y=vardict_P10, fig=TP.fig)
    Pb1_sfc = Paintbox_1D(X=vardict_sfc, Y=vardict_sfc, fig=TP.fig)
    TP.grid()
    TP.twin(xy="y")
    TP.twin(xy="y")
    TP.axs[0][2].spines.top.set_position(("axes", 1.09))
    ylim=[np.nanmax(vardict["P"]),700]
    TP.set_ylim(ylim=ylim, axn=(0,0))
    TP.set_xlim(xlim=[293,323], axn=(0,0))
    TP.set_xlim(xlim=[0,0.020], axn=(0,1))
    TP.set_xlim(xlim=[0,100], axn=(0,2))

    p1 = Pb1.plot(Xname="PT", Yname="P", ax=TP.axs[0][0], color="r", label="potential temperature")
    p2 = Pb1.plot(Xname="qv", Yname="P", ax=TP.axs[0][1], color="green", label="vapor mixing ratio")
    p3 = Pb1.plot(Xname="RH", Yname="P", ax=TP.axs[0][2], color="dimgrey", label="relative humidity")
    TP.axs[0][0].tick_params(axis='x', colors=p1[0].get_color())
    TP.axs[0][1].tick_params(axis='x', colors=p2[0].get_color())
    TP.axs[0][2].tick_params(axis='x', colors=p3[0].get_color())
    xticks      = np.arange(8)*2.5*1e-3
    xticklabels = ["{:.1f}".format(xtick*1e3) for xtick in xticks]
    TP.set_xticks(xticks, xticklabels, axn = (0,1))

    # if vardict_sfc:
    #     Pb1_sfc.plot(Xname="PT", Yname="P", ax=TP.axs[0][0], marker="^", markersize=20, color="k", label="potential temperature")
        # Pb1_sfc.plot(Xname="qv", Yname="P", ax=TP.axs[0][1], marker="^", markersize=20, color="green", label="vapor mixing ratio")
        # Pb1_sfc.plot(Xname="RH", Yname="P", ax=TP.axs[0][2], marker="^", markersize=20, color="dimgrey", label="relative humidity")

    qui = Pb1_2.quiver_y(Uname="U", Vname="V", Yname="P", xposition=0.93, ax = TP.axs[0][0], scale_q=200)
    TP.quiverkey(qui, 0.8, 1.065, 10, label = "10 m/s", coordinates="axes", fontsize = None, axn = None)

    plot_MLH_line(plotter=TP, vardict=vardict, MLH_ind=MLH_ind, subplot_n=0, xposition=0.04)
    plot_inversion_line(plotter=TP, vardict=vardict, inversion_layer=inversion_layer, subplot_n=0, xposition=0.04)
    plot_cloud_layer_mark(plotter=TP, paintbox_1D=Pb1, vardict=vardict, cloud_layer=cloud_layer, subplot_n=0, xposition=0.84)
    plot_LCL_line(plotter=TP, LCL_P=LCL_P, subplot_n=0, xposition=0.04)
    set_yticks(plotter=TP, vardict=vardict, ifhticks = True)

    nearest_hour = soundingtime
    titlestr = nearest_hour.strftime("%Y%m%d%H")
    TP.title(titlestr=titlestr, y=1.15)
    TP.fig.set_tight_layout(True)
    TP.savefig(picdir, nearest_hour.strftime("%Y%m%d%H"))