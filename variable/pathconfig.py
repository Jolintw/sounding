from pathlib import Path

ROOT = Path("D:/NOR10069")

DATA = ROOT / "data"
STDATA = DATA / "ST"
ST1 = STDATA / "ST_20240326-0330"
ST2 = STDATA / "ST_20240330-0404"
RS41DATA = DATA / "RS41"
EDT = RS41DATA / "EDTdata"
MIDAS     = DATA / "MIDAS"
MIDAS_MAT = MIDAS / "mat_file"
MIDAS_ORI = MIDAS / "origin"
MIDAS_EXT = MIDAS / "extracted"
keys = ["P", "T", "RH", "solar"]
MIDAS_EXT_BRIDGE = {key:MIDAS_EXT / ("bridge_" + key) for key in keys}
MIDAS_EXT_NTU = MIDAS_EXT / "met_ntu"
MIDAS_MIN_MEAN = MIDAS / "minute_averaged"
MIDAS_MIN_MEAN_BRIDGE = MIDAS_MIN_MEAN / "met_bridge.nc"

PIC  = ROOT / "pic"
SSPIC = PIC / "snapshot"
BOXPIC = PIC / "parameter_boxplot"

OUT = ROOT / "out"
PBL_PAR = OUT / "PBL_parameters"