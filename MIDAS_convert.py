from reader.MIDAS_reader import readMIDAS
from variable.pathconfig import MIDAS_ORI, MIDAS_EXT_BRIDGE, MIDAS_EXT_NTU

def write_txt(var, time, header, filepath, filename):
    lines = header
    linesformat = ""
    for _ in var:
        linesformat += "{:20.8f},"
    linesformat += "{:20.1f}\n"
    for write_values in zip(*var, time):
        lines += linesformat.format(*write_values)
    lines = lines[:-1]
    filepath.mkdir(parents=True, exist_ok=True)
    f = open(filepath/filename, "w")
    f.writelines(lines)
    f.close()

filelist = list(MIDAS_ORI.glob("*"))
header_base = "extracted from origin MIDAS data\n"
met_bridge = "met_bridge"
met_ntu = "met_ntu"

for file in filelist:
    data = readMIDAS(file)

    if met_bridge in data:
        metdata = data[met_bridge]
        header_bridge = header_base + "$WIXDR sensor on bridge\n"
        if "P" in metdata:
            var  = metdata["P"]
            time = metdata["P_time"]
            header = header_bridge + "{:>20s},{:>20s}\n".format("Pressure(bar)", "timestamp")
            write_txt([var], time, header, filepath=MIDAS_EXT_BRIDGE["P"], filename=file.parts[-1])
        if "H" in metdata:
            var  = metdata["H"]
            time = metdata["H_time"]
            header = header_bridge + "{:>20s},{:>20s}\n".format("Humidity(%)", "timestamp")
            write_txt([var], time, header, filepath=MIDAS_EXT_BRIDGE["RH"], filename=file.parts[-1])
        if "C" in metdata:
            var  = metdata["C"]
            time = metdata["C_time"]
            header = header_bridge + "{:>20s},{:>20s}\n".format("Temperature(Celsius)", "timestamp")
            write_txt([var], time, header, filepath=MIDAS_EXT_BRIDGE["T"], filename=file.parts[-1])
        if "G" in metdata:
            var  = metdata["G"]
            time = metdata["G_time"]
            header = header_bridge + "{:>20s},{:>20s}\n".format("SolarRadiation(W/m2)", "timestamp")
            write_txt([var], time, header, filepath=MIDAS_EXT_BRIDGE["solar"], filename=file.parts[-1])
    if met_ntu in data:
        metdata = data[met_ntu]
        header_ntu = header_base + "$PORWIA sensor on bow\n"
        header = header_ntu + "{:>20s},{:>20s},{:>20s}\n".format("Temperature(Celsius)", "Humidity(%)", "timestamp")
        write_txt([metdata["T"], metdata["RH"]], metdata["time"], header, filepath=MIDAS_EXT_NTU, filename=file.parts[-1])