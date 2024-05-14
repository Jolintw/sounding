import numpy as np
from reader.read import readall
from variable.pathconfig import PBL_PAR

# datatype = "RS41_EDT"
datatype = "ST_L4p"
data = readall(datatype=datatype)
data["soundingtimestamp"]   = [time.timestamp() for time in data["soundingtime"]]
data["inversion_ind"]       = [inversion.PBL_ind for inversion in data["inversion_layer"]]
data["inversion_height"]    = [vardict["height"][ind] for vardict, ind in zip(data["vars"], data["inversion_ind"])]
data["MLH"]                 = [vardict["height"][ind] for vardict, ind in zip(data["vars"], data["MLH_ind"])]
data["cloud_bottom_height"] = []
data["cloud_top_height"]    = []
for cloud in data["cloud_layer"]:
    if cloud.layer_number > 0:
        data["cloud_bottom_height"].append(cloud.bottom_H[0])
        data["cloud_top_height"].append(cloud.top_H[0])
    else:
        data["cloud_bottom_height"].append(-9999)
        data["cloud_top_height"].append(-9999)

writedata = ["soundingtimestamp", "inversion_height", "MLH", "cloud_top_height", "cloud_bottom_height"]
header = ""
for name in ["soundingtimestamp(s)", "inversion_height(m)", "    MLH(m)", "cloud_top_height(m)", "cloud_bottom_height(m)"]:
    header += name + ","
lines = header[:-1] + "\n"
for i_line in range(len(data["soundingtimestamp"])):
    value = [data[name][i_line] for name in writedata]
    lines += "{:20.1f},{:19.1f},{:10.1f},{:19.1f},{:22.1f}\n".format(*value)
lines = lines[:-1]
PBL_PAR.mkdir(parents=True, exist_ok=True)
f = open(PBL_PAR / datatype, "w")
f.writelines(lines)
f.close()
