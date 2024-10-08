from pathlib import Path

ROOT = Path("D:/NOR10069")

DATA = ROOT / "data"

STDATA = DATA / "ST"
ST1 = STDATA / "ST_20240326-0330"
ST2 = STDATA / "ST_20240330-0404"

RS41DATA = DATA / "RS41"
EDT = RS41DATA / "EDTdata"

SFCTS = DATA / "SurfaceTS"
SFCTS_NC = SFCTS / "Surfacewater.nc"

MIDAS     = DATA / "MIDAS"
MIDAS_MAT = MIDAS / "mat_file"
MIDAS_ORI = MIDAS / "origin"
MIDAS_EXT = MIDAS / "extracted"
keys = ["P", "T", "RH", "solar"]
MIDAS_EXT_BRIDGE = {key:MIDAS_EXT / ("bridge_" + key) for key in keys}
MIDAS_EXT_NTU = MIDAS_EXT / "met_ntu"
MIDAS_MIN_MEAN = MIDAS / "minute_averaged"
MIDAS_MIN_MEAN_BRIDGE = MIDAS_MIN_MEAN / "met_bridge.nc"

STATION = DATA / "eddystationlist.txt"

PIC  = ROOT / "pic"
PIC_MAP = PIC / "map"
PIC_SFCWATER = PIC / "surfacewater"
SSPIC = PIC / "snapshot"
BOXPIC = PIC / "parameter_boxplot"
SSPIC_SFC = PIC / "snapshot_sfc"
BOXPIC_SFC = PIC / "parameter_boxplot_sfc"
NORMALHPIC = PIC / "normalized_height_composite"
NORMALHPIC_SFC = PIC / "normalized_height_composite_sfc"
TIMESERIES_2D = PIC / "timeseries_2d"
TIMESERIES_2D_SFC = PIC / "timeseries_2d_sfc"

OUT = ROOT / "out"
PBL_PAR = OUT / "PBL_parameters"
PBL_PAR_SFC = OUT / "PBL_parameters_sfc"