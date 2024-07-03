import matplotlib.pyplot as plt
from datetime import datetime as dd
from mypkgs.plotter.plotter import TwinPlotter
from mypkgs.plotter.paintbox import Paintbox_1D
from reader.SurfaceTS_reader import read_Surfacewater_nc
from reader.stationlist_reader import read_stationlist
from variable.pathconfig import PIC_SFCWATER

timefmt = "%Y%m%d%H%z"
timerange = [dd.strptime("2024032712+0000", timefmt), dd.strptime("2024033112+0000", timefmt)]

station = read_stationlist()
data = read_Surfacewater_nc()
TP    = TwinPlotter(subfigsize_x = 12, subfigsize_y = 3, fontsize=25, sharex=True)
Pb1   = Paintbox_1D(X=data, Y=data, fig=TP.fig)
TP.twin(xy="y")
TP.grid()
Pb1.plot(Xname="time", Yname="T90", fig=TP.fig, ax=TP.axs[0][0], color="r")
TP.set_xlim([time.timestamp() for time in timerange], axn=[(0,0), (0,1)])
TP.set_ylim([24.5, 28.5])
TP.set_yticks([25,26,27,28], [25,26,27,28])
TP.set_ylabel("[$^oC$]")
TP.set_xticks(xticks=station["starttimestamp"], xticklabels=station["name"], axn=(0,1))
TP.set_timeticks(start=timerange[0].timestamp()+(-timerange[0].hour)%24*3600, end=timerange[1].timestamp()+1, intv=86400, timefmt="%m/%d", axn=(0, 0))
fnametimefmt = "%m%d%H"
TP.savefig(PIC_SFCWATER, f"{timerange[0].strftime(fnametimefmt)}-{timerange[1].strftime(fnametimefmt)}")

timefmt = "%Y%m%d%H%z"
timerange = [dd.strptime("2024032700+0800", timefmt), dd.strptime("2024033100+0800", timefmt)]
print(timerange)
print(timerange[0].hour)
station = read_stationlist()
data = read_Surfacewater_nc()
TP    = TwinPlotter(subfigsize_x = 12, subfigsize_y = 3, fontsize=25, sharex=True)
Pb1   = Paintbox_1D(X=data, Y=data, fig=TP.fig)
TP.twin(xy="y")
TP.grid()
Pb1.plot(Xname="time", Yname="T90", fig=TP.fig, ax=TP.axs[0][0], color="r")
TP.set_xlim([time.timestamp() for time in timerange], axn=[(0,0), (0,1)])
TP.set_ylim([24.5, 28.5])
TP.set_yticks([25,26,27,28], [25,26,27,28])
TP.set_ylabel("[$^oC$]")
TP.set_xticks(xticks=station["starttimestamp"], xticklabels=station["name"], axn=(0,1))
TP.set_timeticks(start=timerange[0].timestamp()+(-timerange[0].hour)%24*3600, end=timerange[1].timestamp()+1, intv=86400, timefmt="%m/%d", startfmt="%m/%d\n%z", timezonehour=8, axn=(0, 0))
fnametimefmt = "%m%d%H"
TP.savefig(PIC_SFCWATER, f"{timerange[0].strftime(fnametimefmt)}-{timerange[1].strftime(fnametimefmt)}UTC+8")
