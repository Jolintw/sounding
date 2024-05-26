from datetime import datetime as dd
import numpy as np
from pathlib import Path
from mypkgs.plotter.plotter import Plotter
from mypkgs.plotter.paintbox import Paintbox_1D, Paintbox_2D
from mypkgs.processor.numericalmethod import RightAngleInterpolater
from processor.interpolate import interpolate_by, create_Parray_asnewX
from variable.pathconfig import TIMESERIES_2D, TIMESERIES_2D_SFC
from reader.read import readall
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.transforms import Bbox

datatype = "RS41_EDT" 
# datatype = "ST_L4p"
# datatype = "ST_L4"
# datatype = "ST_L1"

timefmt = "%Y%m%d%H%z"
timerange = [dd.strptime("2024032600+0000", timefmt), dd.strptime("2024040100+0000", timefmt)]
sfc_station = None #"bridge", None
data = readall(datatype, surface=sfc_station, timerange=timerange)
if sfc_station:
    picdir = TIMESERIES_2D_SFC / sfc_station / "1PT_EPT_qv_2wind_param"
else:
    picdir = TIMESERIES_2D / "1PT_EPT_qv_2wind_param"

for vars, cloud in zip(data["vars"], data["cloud_layer"]):
    vars["cloud_mask"] = cloud.get_mask_of_layer(vars["P"])

newPintv = 5
newX            = create_Parray_asnewX(intv=newPintv, maxP=1000, minP=500)
data["vars_P5"] = [interpolate_by(vardict=vardict, Xname="P", newX=newX) for vardict in data["vars"]]
data_to_plot = {}
data_to_plot["vars"] = {}
for varname in data["vars_P5"][0]:
    data_to_plot["vars"][varname] = [vars_P5[varname] for vars_P5 in data["vars_P5"]]
    data_to_plot["vars"][varname] = np.array(data_to_plot["vars"][varname]).transpose()
data_to_plot["vars"]["cloud_mask"] = np.floor(data_to_plot["vars"]["cloud_mask"])
data_to_plot["vars"]["cloud_mask"][data_to_plot["vars"]["cloud_mask"]<=0] = np.nan

data_to_plot["soundingtime"]      = [t for t in data["soundingtime"]]
data_to_plot["soundingtimestamp"] = np.array([t.timestamp() for t in data["soundingtime"]])
data_to_plot["MLH_P"]             = [vars["P"][ind] for ind, vars in zip(data["MLH_ind"], data["vars"])]
data_to_plot["inversion_P"]       =  [vars["P"][inversion.PBL_ind] for inversion, vars in zip(data["inversion_layer"], data["vars"])]
Hmean = np.mean(data_to_plot["vars"]["height"], axis=1)

plt.rcParams['figure.constrained_layout.use'] = True
PT  = Plotter(subfigsize_x=10, subfigsize_y=8, column=2)
Xarr, Yarr = np.meshgrid(data_to_plot["soundingtimestamp"], data_to_plot["vars"]["P"][:,0])
Pb2 = Paintbox_2D(field=data_to_plot["vars"], X=Xarr, Y=Yarr, fig=PT.fig, ax=PT.ax[0], ft=PT.fontsize)
Pb1 = Paintbox_1D(X=data_to_plot, Y=data_to_plot,  fig=PT.fig, ax=PT.axs[1], ft=PT.fontsize)

cf, cb = Pb2.contourf(varname="EPT", colorkey="EPT_sounding", orientation="horizontal", extend="max")
pos = cb.ax.get_position()
pos.y0 += 0.12; pos.y1 += 0.06
cb.ax.set_position(pos)
linewidths = 3
Pb2.contour(varname="PT", colors="violet", levels=np.arange(288, 354, 4), linewidths=linewidths, clabel=True)
CS, CStext = Pb2.contour(varname="qv", colors="k", levels=np.arange(0, 0.021, 0.003), linewidths=linewidths, clabel=True)
for text in CStext:
    oritext = text.get_text()
    newtext = f"{float(oritext)*1000:.0f}"
    text.set(text=newtext)

Pb2.ax = PT.axs[1]
qui = Pb2.quiver(Uname="U", Vname="V", scale_q=150, xintv=1, yintv=25//newPintv, broadXY=False, weight=False)
PT.quiverkey(qui, 0.85, 1.03, 10, label = "10 m/s", coordinates="axes", fontsize = None, axn = 1)
Pb1.plot(Xname="soundingtimestamp", Yname="MLH_P", color="indigo", linewidth=linewidths)
Pb1.plot(Xname="soundingtimestamp", Yname="inversion_P", color="dimgrey", linewidth=linewidths)
PT.axs[1].pcolormesh(Pb2.X, Pb2.Y, data_to_plot["vars"]["cloud_mask"], cmap="cool_r", alpha=0.7, vmin=0.5, vmax=1)

PT.set_xlim([t.timestamp() for t in timerange])
PT.set_timeticks(start=timerange[0].timestamp(), end=timerange[1].timestamp()+1, intv=3600*24, timefmt="%m/%d")
PT.title("$\\theta$, $\\theta_e$, q", axn=0)
PT.title("MLH, inversion, U/V-wind and cloud", axn=1, fontsize=20)
PT.set_ylim([1000, 500])
yticks = [1000, 925, 850, 800, 700, 600, 500]
PT.set_yticks(yticks, [f"{tick}" for tick in yticks])
twinax = PT.axs[1].twinx()
twinax.set_ylim([1000, 500])
twinax.set_yticks(yticks)
twinax.set_yticklabels([f"{Hmean[ind]:.1f}" for ind in [0, 15, 30, 40, 60, 80, 100]])
twinax.tick_params(labelsize=PT.fontsize)
# PT.fig.savefig("12atest", bbox_inches=Bbox([[0,1.5],[10.5,9.5]]))
# PT.fig.tight_layout(h_pad=0.0)
PT.savefig(picdir, datatype, tight_layout=False)
