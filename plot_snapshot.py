from pathlib import Path
import numpy as np
from mypkgs.plotter.plotter import TwinPlotter
from mypkgs.plotter.paintbox import Paintbox_1D
from variable.pathconfig import ST1, ST2, EDT
from reader.ST import STreader
from reader.RS41 import RS41reader
from processor.cloudlayer import find_cloud_layer
from processor.MLH import find_MLH
from processor.smooth5hPa import smooth_5hPa
from processor.inversion import find_inversion_layer
from processor.interpolate import interpolate_by, create_Parray_asnewX

RSR = RS41reader(EDT)
vardict = RSR.readEDT(RSR.filelist[5])
print(RSR.getfirsttime(vardict))
vardict = smooth_5hPa(vardict)
P = vardict["P"]
for key in vardict:
    vardict[key] = vardict[key][P>400]
newX=create_Parray_asnewX(intv=10, maxP=np.nanmax(vardict["P"]), minP=450)
vardict_P10 = interpolate_by(vardict=vardict, Xname="P", newX=newX)
cloud_layer = find_cloud_layer(vardict["RH"]/100, vardict["height"])
inversion_layer = find_inversion_layer(vardict["PT"], vardict["height"], cloud_layer.get_mask_of_layer(vardict["PT"]))

maxP = np.nanmax(vardict["P"])
if maxP > 1000:
    levels = [1000, 925, 850, 800, 700]
else:
    levels = [925, 850, 800, 700]

vardict_stdlevel = interpolate_by(vardict=vardict, Xname="P", newX=np.array(levels))
yticks_p = [maxP] + levels
yticklabels_p = ["{:.1f}".format(ytick) for ytick in yticks_p]
yticklabels_h = [vardict["height"][0]] + ["{:.1f}".format(ytick) for ytick in vardict_stdlevel["height"]]
if maxP - 1000 < 10 and maxP > 1000:
    yticklabels_p[0] == ""
    yticklabels_h[0] == ""


TP = TwinPlotter(subfigsize_x = 12, subfigsize_y = 12, fontsize=30)
TP.grid()
Pb1 = Paintbox_1D(X=vardict, Y=vardict, fig=TP.fig)
Pb1_2 = Paintbox_1D(X=vardict_P10, Y=vardict_P10, fig=TP.fig)
TP.twin(xy="y")
TP.twin(xy = "y")
TP.twin(xy="x")
TP.axs[0][2].spines.top.set_position(("axes", 1.1))
TP.set_ylim(ylim=[np.nanmax(vardict["P"]),700], axn=(0,0))
TP.set_ylim(ylim=[np.nanmax(vardict["P"]),700], axn=(0,3))
TP.set_xlim(xlim=[293,323], axn=(0,0))
TP.set_xlim(xlim=[0,0.018], axn=(0,1))
TP.set_xlim(xlim=[0,100], axn=(0,2))

p1 = Pb1.plot(Xname="PT", Yname="P", ax=TP.axs[0][0], color="r", label="potential temperature")
p2 = Pb1.plot(Xname="qv", Yname="P", ax=TP.axs[0][1], color="green", label="vapor mixing ratio")
p3 = Pb1.plot(Xname="RH", Yname="P", ax=TP.axs[0][2], color="dimgrey", label="relative humidity")

TP.axs[0][0].tick_params(axis='x', colors=p1[0].get_color())
TP.axs[0][1].tick_params(axis='x', colors=p2[0].get_color())
TP.axs[0][2].tick_params(axis='x', colors=p3[0].get_color())
xticks = np.arange(8)*2.5*1e-3
xticklabels = ["{:.1f}".format(xtick*1e3) for xtick in xticks]
TP.set_xticks(xticks, xticklabels, axn = (0,1))

qui = Pb1_2.quiver_y(Uname="U", Vname="V", Yname="P", position=0.8, ax = TP.axs[0][0], scale_q=150)
TP.quiverkey(qui, 0.8, 1.065, 10, label = "10 m/s", coordinates="axes", fontsize = None, axn = None)

TP.set_yticks(yticks_p, yticklabels_p, axn = (0,0))
TP.set_yticks(yticks_p, yticklabels_h, axn = (0,3))

TP.fig.set_tight_layout(True)
TP.savefig(Path("./"), "test")