import numpy as np
from mypkgs.plotter.plotter import TwinPlotter
from mypkgs.plotter.paintbox import Paintbox_1D
from mypkgs.processor.numericalmethod import RightAngleInterpolater
from variable.pathconfig import NORMALHPIC, NORMALHPIC_SFC
from reader.read import readall
from plotter.snapshot import plot_variable, plot_LCL_line, plot_CTH_CBH_line


datatype = "RS41_EDT" 
# datatype = "ST_L4p"
# datatype = "ST_L4"
# datatype = "ST_L1"

sfc_station = None #"bridge", None
data = readall(datatype, surface=sfc_station)
vars = data["vars"]

if sfc_station:
    picdir = NORMALHPIC_SFC / sfc_station
else:
    picdir = NORMALHPIC

data_to_plot = {}
data_to_plot["vars_NH"] = data["vars_normalized_height"]
data_to_plot["vars_to_plot"] = {}
for varname in ["PT", "EPT", "dEPTdz", "qv", "U", "V", "normalized_height"]:
    data_to_plot["vars_to_plot"][varname] = []
    for vars_NH in data_to_plot["vars_NH"]:
        data_to_plot["vars_to_plot"][varname].append(vars_NH[varname])
    data_to_plot["vars_to_plot"][varname] = np.nanmean(data_to_plot["vars_to_plot"][varname], axis=0)
data_to_plot["MLH_NH"] = [var["normalized_height"][ind] for ind, var in zip(data["MLH_ind"], vars)]
data_to_plot["inversion_NH"] = [var["normalized_height"][inversion.PBL_ind] for inversion, var in zip(data["inversion_layer"], vars)]
data_to_plot["LCL_NH"] = data["LCL_normalized_height"]
cloudmask = [cloud.get_mask_of_layer(var["P"]) for cloud, var in zip(data["cloud_layer"], vars)]
data_to_plot["cloud_mask_interpolate"] = []
for var, var_NH, cm in zip(vars, data_to_plot["vars_NH"], cloudmask):
    RIA = RightAngleInterpolater(X=var["normalized_height"], newX=var_NH["normalized_height"], equidistance=False, newX_out_of_X=True)
    data_to_plot["cloud_mask_interpolate"].append(RIA.interpolate(cm.astype(float)))
for key in data_to_plot:
    if isinstance(data_to_plot[key], (np.ndarray, int, float)):
        data_to_plot[key] = np.array(data_to_plot[key])
data_to_plot["cloud_ratio"] = 100 * np.mean(data_to_plot["cloud_mask_interpolate"], axis=0) # %
data_to_plot["CBH_NH"] = []
data_to_plot["CTH_NH"]    = []
for cloud , var in zip(data["cloud_layer"], vars):
    if cloud.layer_number > 0:
        data_to_plot["CBH_NH"].append(var["normalized_height"][cloud.bottom_ind[0]])
        data_to_plot["CTH_NH"].append(var["normalized_height"][cloud.top_ind[0]])
    else:
        data_to_plot["CBH_NH"].append(np.nan)
        data_to_plot["CTH_NH"].append(np.nan)



TP = TwinPlotter(column=3, row=1, subfigsize_x=6, subfigsize_y=12, sharey=True, fontsize=30)
Pb1   = Paintbox_1D(X=data_to_plot["vars_to_plot"], Y=data_to_plot["vars_to_plot"], fig=TP.fig)
Pb1_2 = Paintbox_1D(X=data_to_plot, Y=data_to_plot["vars_to_plot"], fig=TP.fig)

TP.grid(axis="y")

# first subplot
sub_num_now = 0
TP.change_twinaxes_name(newname="PT", sub_num=sub_num_now)
TP.twin(axesname="qv", xy="y", sub_num=sub_num_now)
TP.set_ylim(ylim=[0, 3], axn=None)
necepar = {"plotter":TP, "paintbox":Pb1, "sub_num":sub_num_now, "Yname":"normalized_height"}
par_dict = {"PT":{"xlim":[298,316], "color": "r", "label":"potential temperature"},
            "qv":{"xlim":[0.003,0.020], "color": "green", "label":"vapor mixing ratio"}}
for varname in par_dict:
    plot_variable(varname=varname, **necepar, **par_dict[varname])
qui = Pb1.quiver_y(Uname="U", Vname="V", Yname="normalized_height", xposition=0.93, ax = TP.axs[sub_num_now][0], scale_q=100, intv=10)
TP.quiverkey(qui, 0.8, 1.065, 10, label = "10 m/s", coordinates="axes", fontsize = None, axn = (sub_num_now, 0))


TP.set_xlabel("$\\theta\ (K)$", axn=(sub_num_now,"PT"), color=par_dict["PT"]["color"])
TP.set_xlabel("$q_v\ (g/kg)$", axn=(sub_num_now,"qv"), color=par_dict["qv"]["color"])
TP.auto_set_xticks(intv=5, strfmt="{:.0f}", axn = (sub_num_now, "PT"))
xticks      = np.arange(1,5)*5*1e-3
xticklabels = ["{:.1f}".format(xtick*1e3) for xtick in xticks]
TP.set_xticks(xticks, xticklabels, axn = (0,"qv"))

# second subplot
sub_num_now = 1
TP.change_twinaxes_name(newname="cloud_ratio", sub_num=sub_num_now)
necepar = {"plotter":TP, "paintbox":Pb1_2, "sub_num":sub_num_now, "Yname":"normalized_height"}
par_dict = {"cloud_ratio":{"xlim":[0, 100], "color": "k", "label":"cloud frequency"}}
for varname in par_dict:
    plot_variable(varname=varname, **necepar, **par_dict[varname])
TP.set_xlabel("Cloud Frequency (%)", axn=(sub_num_now,"cloud_ratio"), color=par_dict["cloud_ratio"]["color"])

# third subplot
sub_num_now = 2
TP.change_twinaxes_name(newname="EPT", sub_num=sub_num_now)
TP.twin(axesname="dEPTdz", xy="y", sub_num=sub_num_now)
necepar = {"plotter":TP, "paintbox":Pb1, "sub_num":sub_num_now, "Yname":"normalized_height"}
par_dict = {"EPT":{"xlim":[323,351], "color": "mediumblue", "label":"equivalent potential temperature"},
            "dEPTdz":{"xlim":[-0.04,0.01], "color": "mediumblue", "label":"equivalent potential temperature gradient", "linestyle":":"}}
for varname in par_dict:
    plot_variable(varname=varname, **necepar, **par_dict[varname])
TP.auto_set_xticks(intv=10, strfmt="{:.0f}", axn = (sub_num_now, "EPT"))
TP.auto_set_xticks(intv=0.02, strfmt="{:.2f}", axn = (sub_num_now, "dEPTdz"))
TP.set_xlabel("$\\theta_e$ (K) (solid)", axn=(sub_num_now,"EPT"), color=par_dict["EPT"]["color"])
TP.set_xlabel("$\\theta_e/dz$ (K/m) (dotted)", axn=(sub_num_now,"dEPTdz"), color=par_dict["dEPTdz"]["color"])

# multi subplots
TP.set_yticks([0, 1, 2], ["", "", ""], axn=None)
TP.set_yticks([0, 1, 2], ["surface", "MLH", "inversion"], axn=(0,0))
line_inv = TP.hline(np.median(data_to_plot["inversion_NH"]), color="dimgrey", linestyle="dashed", axn=None)
line_MLH = TP.hline(np.median(data_to_plot["MLH_NH"]), color="indigo", linestyle="dashed", axn=None)
for sub_num in [0, 2]:
    plot_LCL_line(TP, np.median(data_to_plot["LCL_NH"]), subplot_n=sub_num, xposition=0.15, color="hotpink")
plot_CTH_CBH_line(TP, np.nanmedian(data_to_plot["CTH_NH"]), np.nanmedian(data_to_plot["CBH_NH"]), subplot_n=1, xposition=0.75, color="black")

TP.savefig(picdir, datatype)