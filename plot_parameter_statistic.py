import numpy as np
from pathlib import Path
from variable.pathconfig import PBL_PAR, PBL_PAR_SFC, BOXPIC, BOXPIC_SFC
from reader.read import get_cotime_datas
from mypkgs.plotter.plotter import Plotter
from mypkgs.plotter.paintbox import Paintbox_1D
from datetime import datetime as dd

def plot_one_axis(data, plotter, axn=0, title = ""):
    ax = plotter.axs[axn]
    Pb = Paintbox_1D(X=data, Y=data, fig=plotter.fig, ax=ax)
    Pb.boxplot(Yname=["inversion_height", "MLH", "cloud_top_height", "cloud_bottom_height"], labels=["inversion", "MLH", "CTH", "CBH"])
    plotter.title(title, axn=axn)
    return Pb

datas = {}
datatypes = ["RS41_EDT", "ST_L4p", "ST_L4", "ST_L1"]

sfc_station = None #"bridge", None
if sfc_station == "bridge":
    datapath = PBL_PAR_SFC
    picpath  = BOXPIC_SFC
else:
    datapath = PBL_PAR
    picpath  = BOXPIC
picpath.mkdir(parents=True, exist_ok=True)


for datatype in datatypes:
    dataarray = np.loadtxt(datapath / datatype, skiprows=1, delimiter=",")
    data = {}
    for i, name in enumerate(["soundingtimestamp", "inversion_height", "MLH", "cloud_top_height", "cloud_bottom_height"]):
        data[name] = dataarray[:, i]
    
    cloud_mask = np.logical_or(data["cloud_bottom_height"] < 0, data["cloud_bottom_height"] >= 5000)
    data["cloud_top_height"][cloud_mask] = np.nan
    data["cloud_bottom_height"][cloud_mask] = np.nan
    datas[datatype] = data

newdatas = get_cotime_datas(datas)
print([dd.fromtimestamp(ts) for ts in newdatas["ST_L1"]["soundingtimestamp"]])
print(newdatas["ST_L1"]["inversion_height"])
Pt = Plotter(column=4, subfigsize_x=5)
for i_axis, datatype in enumerate(datatypes):
    plot_one_axis(newdatas[datatype], plotter=Pt, axn=i_axis, title=datatype)
Pt.set_ylabel("height (m)")
Pt.set_ylim([0, 5000])
Pt.savefig(picpath, "cotime_compare")

for datatype in datatypes:
    Pt = Plotter(column=1, subfigsize_x=5)
    plot_one_axis(datas[datatype], plotter=Pt, axn=0, title=datatype)
    Pt.set_ylabel("height (m)")
    Pt.set_ylim([0, 5000])
    Pt.savefig(picpath, datatype)
