import numpy as np
from pathlib import Path
from variable.pathconfig import PBL_PAR, BOXPIC
from mypkgs.plotter.plotter import Plotter
from mypkgs.plotter.paintbox import Paintbox_1D

datatype = "RS41_EDT"
# datatype = "ST_L4p"
dataarray = np.loadtxt(PBL_PAR / datatype, skiprows=1, delimiter=",")

data = {}
for i, name in enumerate(["soundingtimestamp", "inversion_height", "MLH", "cloud_top_height", "cloud_bottom_height"]):
    data[name] = dataarray[:, i]
cloud_mask = np.logical_and(data["cloud_bottom_height"] > -999, data["cloud_bottom_height"] <= 5000)
data["cloud_top_height"]    = data["cloud_top_height"][cloud_mask]
data["cloud_bottom_height"] = data["cloud_bottom_height"][cloud_mask]
Pt = Plotter(subfigsize_x=5)
Pb = Paintbox_1D(X=data, Y=data, fig=Pt.fig, ax=Pt.ax)
Pb.boxplot(Yname=["inversion_height", "MLH", "cloud_top_height", "cloud_bottom_height"], labels=["inversion", "MLH", "CTH", "CBH"])
Pt.set_ylabel("height (m)")
Pt.set_ylim([0, 5000])
Pt.savefig(BOXPIC, datatype)
