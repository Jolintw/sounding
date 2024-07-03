# -*- coding: utf-8 -*-
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime as dd
from mypkgs.plotter.plotter import MapPlotter
from variable.pathconfig import DATA, STATION, PIC_MAP
from reader.stationlist_reader import read_stationlist
from reader.SurfaceTS_reader import read_Surfacewater_nc

filename_RS41 = DATA / "launchrecord_RS41.txt"
filename_ST   = DATA / "launchrecord_ST.txt"
stationlist = STATION
RS41 = {}
ST = {}
stations = read_stationlist()
RS41["t"], RS41["lat"], RS41["lon"] = np.loadtxt(filename_RS41, delimiter=',', skiprows=1, unpack=True, usecols=(0,1,2))
ST["t"], ST["lat"], ST["lon"] = np.loadtxt(filename_ST, delimiter=',', skiprows=1, unpack=True, usecols=(0,1,2))
sfc_water = read_Surfacewater_nc()

RS41["datetime"] = []
ST["datetime"] = []
for t in RS41["t"]:
    RS41["datetime"].append(dd.strptime(str(int(t))+"+0000", "%Y%m%d%H%z"))
for t in ST["t"]:
    ST["datetime"].append(dd.strptime(str(int(t))+"+0000", "%Y%m%d%H%z"))

ft = 30
MP = MapPlotter(figsize = (15, 15), fontsize = ft)
MP.coastlines()
MP.setlatlonticks(ticksitvl = [3,2], xlim = [120,135], ylim = [6,23])
for i_t, t in enumerate(RS41["datetime"]):
    if t.strftime("%H")=="00" and t.strftime("%d")!="04":
        MP.ax.text(RS41["lon"][i_t], RS41["lat"][i_t], t.strftime("%m/%d %HZ"), fontsize=ft)
for i_st, st in enumerate(stations["name"]):
    shift = -0.7
    MP.ax.text(stations["lon"][i_st]+shift, stations["lat"][i_st]+shift, st, fontsize=ft*0.8)
ms = 20
MP.ax.plot(stations["lon"], stations["lat"], "k^", label="eddy stations", ms=ms)
MP.ax.plot(RS41["lon"], RS41["lat"], "ro", label="RS41", ms=ms*0.7)
MP.ax.plot(ST["lon"], ST["lat"], "bx", label="ST", ms=ms)

MP.ax.legend(fontsize = ft)
lon, lat = np.meshgrid(np.linspace(120, 135, 500), np.linspace(6, 23, 500))
vortexcenter = [131, 18]
vortexmask = np.sqrt((vortexcenter[0]-lon)**2 + (vortexcenter[1]-lat)**2) < 1
cs = MP.ax.contourf(lon, lat, vortexmask, levels=[0.9,1], alpha=0.3)

#artists, labels = cs.legend_elements(str_format='')
#MP.ax.legend(artists, labels, handleheight=2, framealpha=1)
MP.savefig(PIC_MAP, "large_sounding_map", tight_layout=False)
ft = 30
MP = MapPlotter(figsize = (15, 9), fontsize = ft)
MP.coastlines()
MP.setlatlonticks(ticksitvl = [2,1], xlim = [128.5,134.2], ylim = [15,20])
for i_t, t in enumerate(RS41["datetime"]):
    if t.strftime("%H")=="00" and t.strftime("%d")!="04":
        if t.day >=28 and t.day <= 30:
            MP.ax.text(RS41["lon"][i_t], RS41["lat"][i_t], t.strftime("%m/%d %HZ"), fontsize=ft)
for i_st, st in enumerate(stations["name"]):
    shift = -0.4
    MP.ax.text(stations["lon"][i_st]+shift, stations["lat"][i_st]+shift, st, fontsize=ft*0.8)
ms = 20
MP.ax.plot(stations["lon"], stations["lat"], "k^", label="eddy stations", ms=ms)
# MP.ax.plot(RS41["lon"], RS41["lat"], "ro", label="RS41", ms=ms*0.7)
# MP.ax.plot(ST["lon"], ST["lat"], "bx", label="ST", ms=ms)
SC = MP.ax.scatter(sfc_water["lon"], sfc_water["lat"], c=sfc_water["T90"], vmin=26.5, vmax=28, cmap=mpl.cm.jet, s=50, zorder=20)
cbar = plt.colorbar(SC)
cbar.ax.tick_params(labelsize=ft)

# MP.ax.legend(fontsize = ft)

MP.savefig(PIC_MAP, "large_sfctemp_map", tight_layout=False)
