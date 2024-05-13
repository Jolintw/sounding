from variable.pathconfig import EDT, ST1, ST2
from reader.ST   import STreader
from reader.RS41 import RS41reader 

def get_reader_and_filelist(datatype):
    if datatype == "RS41_EDT":
        RD = RS41reader(EDT)
        filelist = RD.filelist
    else:
        if datatype == "ST_L4p":
            RD = STreader(ST1)
            filelist = RD.getL4p_PBLlist()
            RD = STreader(ST2)
            filelist = filelist + RD.getL4p_PBLlist()
        elif datatype == "ST_L4":
            RD = STreader(ST1)
            filelist = RD.getfilelist("L4_PBL.eol")
            RD = STreader(ST2)
            filelist = filelist + RD.getfilelist("L4_PBL.eol")
        elif datatype == "ST_L1":
            RD = STreader(ST1)
            filelist = RD.getfilelist("L1.csv")
            RD = STreader(ST2)
            filelist = filelist + RD.getfilelist("L1.csv")
        else:
            raise Exception("datatype \"{:s}\" is not exist.".format(datatype))
    return RD, filelist