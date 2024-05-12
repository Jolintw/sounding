import numpy as np
from mypkgs.plotter.plotter import TwinPlotter
from mypkgs.plotter.paintbox import Paintbox_1D
from variable.pathconfig import ST1, ST2, EDT, SSPIC_RS41, SSPIC_ST, SSPIC
from reader.ST import STreader
from reader.RS41 import RS41reader
from processor.cloudlayer import find_cloud_layer
from processor.MLH import find_MLH
from processor.smooth5hPa import smooth_5hPa
from processor.inversion import find_inversion_layer
from processor.interpolate import interpolate_by, create_Parray_asnewX
from plotter.snapshot import plot_inversion_line, plot_MLH_line, set_yticks, plot_cloud_layer_mark

# datatype = "RS41" 
# datatype = "ST_p"
datatype = "ST_s"
# datatype = "ST_L1"

if datatype == "RS41":
    RD = RS41reader(EDT)
    picdir = SSPIC_RS41
    filelist = RD.filelist
else:
    if datatype == "ST_p":
        RD = STreader(ST1)
        filelist = RD.getL4p_PBLlist()
        RD = STreader(ST2)
        filelist = filelist + RD.getL4p_PBLlist()
        picdir = SSPIC_ST
    elif datatype == "ST_s":
        RD = STreader(ST1)
        filelist = RD.getfilelist("L4_PBL.eol")
        RD = STreader(ST2)
        filelist = filelist + RD.getfilelist("L4_PBL.eol")
        picdir = SSPIC / "ST_second"
    elif datatype == "ST_L1":
        RD = STreader(ST1)
        filelist = RD.getfilelist("L1.csv")
        RD = STreader(ST2)
        filelist = filelist + RD.getfilelist("L1.csv")
        picdir = SSPIC / "ST_L1"

for file in filelist:
    print(file)
    if not file.is_file():
        continue
    if datatype == "RS41":
        vardict = RD.readEDT(file)
    elif datatype == "ST_p":
        vardict = RD.readL4_p(file)
    elif datatype == "ST_s":
        vardict = RD.readL4_second(file)
    elif datatype == "ST_L1":
        vardict = RD.readL1(file)
    if not vardict:
        continue
    firsttime = RD.getfirsttime(vardict)
    print(firsttime)
    vardict = smooth_5hPa(vardict)
    P = vardict["P"]
    for key in vardict:
        vardict[key] = vardict[key][P>650]
    if np.nanmin(vardict["P"]) > 700 or np.nanmax(vardict["P"]) < 950:
        print("under 700 hPa")
        continue

    cloud_layer     = find_cloud_layer(vardict["RH"]/100, vardict["height"])
    inversion_layer = find_inversion_layer(vardict["PT"], vardict["height"], cloud_layer.get_mask_of_layer(vardict["PT"]))
    MLH_ind         = find_MLH(P=vardict["P"], PT=vardict["PT"], qv=vardict["qv"]*1000)
    newX        = create_Parray_asnewX(intv=10, maxP=np.nanmax(vardict["P"]), minP=700)
    # print(vardict["P"])
    # print(newX)
    vardict_P10 = interpolate_by(vardict=vardict, Xname="P", newX=newX)

    TP    = TwinPlotter(subfigsize_x = 12, subfigsize_y = 12, fontsize=30)
    Pb1   = Paintbox_1D(X=vardict, Y=vardict, fig=TP.fig)
    Pb1_2 = Paintbox_1D(X=vardict_P10, Y=vardict_P10, fig=TP.fig)
    TP.grid()
    TP.twin(xy="y")
    TP.twin(xy = "y")
    TP.axs[0][2].spines.top.set_position(("axes", 1.09))
    TP.set_ylim(ylim=[np.nanmax(vardict["P"]),700], axn=(0,0))
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

    qui = Pb1_2.quiver_y(Uname="U", Vname="V", Yname="P", xposition=0.93, ax = TP.axs[0][0], scale_q=200)
    TP.quiverkey(qui, 0.8, 1.065, 10, label = "10 m/s", coordinates="axes", fontsize = None, axn = None)

    plot_MLH_line(plotter=TP, vardict=vardict, MLH_ind=MLH_ind, subplot_n=0, xposition=0.04)
    plot_inversion_line(plotter=TP, vardict=vardict, inversion_layer=inversion_layer, subplot_n=0, xposition=0.04)
    plot_cloud_layer_mark(plotter=TP, paintbox_1D=Pb1, vardict=vardict, cloud_layer=cloud_layer, subplot_n=0, xposition=0.84)
    set_yticks(plotter=TP, vardict=vardict, ifhticks = True)

    nearest_hour = RD.get_nearest_hour(vardict, 3)
    titlestr = nearest_hour.strftime("%Y%m%d%H")
    TP.title(titlestr=titlestr, y=1.15)
    TP.fig.set_tight_layout(True)
    TP.savefig(picdir, nearest_hour.strftime("%Y%m%d%H"))