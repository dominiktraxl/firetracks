
# Copyright (C) 2020 by
# Dominik Traxl <dominik.traxl@posteo.org>
# All rights reserved.
# MIT license.

# Prior to November 2000, the Terra MODIS instrument suffered from several
# hardware problems
# -> use from 2001 onwards is recommended

# FIRE PIXEL CLASSES
# 0 not processed (missing input data)
# 1 not processed (obsolete; not used since Collection 1)
# 2 not processed (other reason)
# 3 cloud (land or water) (originally 4!)
# 4 non-fire water pixel  (originally 3!)
# 5 non-fire land pixel
# 6 unknown (land or water)
# 7 fire (low confidence, land or water)
# 8 fire (nominal confidence, land or water)
# 9 fire (high confidence, land or water)

import os
import argparse
import multiprocessing as mp
from multiprocessing import Pool
from operator import itemgetter
from itertools import product
from datetime import datetime, timedelta
import urllib.request
import zipfile
from urllib.error import URLError

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pyhdf.SD import SD, SDC
from pyhdf.error import HDF4Error

# argument parameters
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    '-p', '--processes',
    help="number of processes to use for the computation",
    type=int,
    default=mp.cpu_count(),
)
args = parser.parse_args()

# file sytem
cwd = os.getcwd()
mod_data = os.path.join(cwd, 'MOD14A1')
myd_data = os.path.join(cwd, 'MYD14A1')

# (down)load countries shapefile
countries_shp = 'ne_10m_admin_0_countries.shp'
if not os.path.isfile(os.path.join(cwd, 'countries', countries_shp)):
    try:
        url = ("https://www.naturalearthdata.com"
               "/http//www.naturalearthdata.com/"
               "download/10m/cultural/ne_10m_admin_0_countries.zip")
        print('downloading countries shape file from \n{}\n ..'.format(
            url))
        filehandle, _ = urllib.request.urlretrieve(url)
        zip_file_object = zipfile.ZipFile(filehandle, 'r')
        zip_file_object.extractall(path=os.path.join(cwd, 'countries'))
        country_boundaries = gpd.read_file(
            os.path.join(cwd, 'countries', countries_shp))
        countries = True
    except URLError as e:
        countries = False
        print('could not download countries shape file because of:')
        print(e)
        print('proceeding without adding country information ..')
else:
    country_boundaries = gpd.read_file(
        os.path.join(cwd, 'countries', countries_shp))
    countries = True

# constants
# the radius of the idealized sphere representing earth [m]
R = 6371007.181
# the height and width of each MODIS tile in the projection plane [m]
T = 1111950.5196666666
# the western limit of the projection plane [m]
xmin = -20015109.354
# the northern limit of the projection plane [m]
ymax = 10007554.677
# the actual size of a "1-km" MODIS sinusoidal grid cell (926.62543305 [m])
w = T/1200.
# compute scan angle (manual p59)
s = 0.0014184397
# radius of earth [km]
R_e = 6378.137
# satellite altitude [km]
h = 705
# earth radius + satellite altitude [km]
r = R_e + h

# years to process
min_year = 2002
max_year = 2020

# MODIS tiles
Hs = np.arange(0, 36)
Vs = np.arange(0, 18)

# datetime <-> integer dictionary
dates = pd.date_range(
    str(min_year) + '-01-01', str(max_year + 1) + '-01-01', freq='D')
dtdic = {date: i for i, date in enumerate(dates)}

# neighbour dict
ndict = {
    0: 'not processed',
    1: 'not processed (obsolete; not used since Collection 1)',
    2: 'not processed (other reason)',
    3: 'cloud (land or water)',
    4: 'non-fire water pixel',
    5: 'non-fire land pixel',
    6: 'unknown (land or water)',
    7: 'fire c0',
    8: 'fire c1',
    9: 'fire c2',
}


# function to extract metadata from filename
def meta_from_file(f):
    satellite = f[:3]
    year = f[9:13]
    fday = f[13:16]
    H = f[18:20]
    V = f[21:23]
    return satellite, year, fday, H, V


# mod14a1 files (fire, terra)
mod_files = os.listdir(mod_data)
mod_files.sort()
mod_files_dict = {meta_from_file(fname): fname for fname in mod_files if
                  fname.endswith('.hdf')}

# myd14a1 files (fire, aqua)
myd_files = os.listdir(myd_data)
myd_files.sort()
myd_files_dict = {meta_from_file(fname): fname for fname in myd_files if
                  fname.endswith('.hdf')}


class ProcessYearFday(object):

    def __init__(self, year, fday):

        # dates
        stime = datetime(int(year), 1, 1) + timedelta(days=int(fday) - 1)
        etime = datetime(int(year), 1, 1) + timedelta(days=int(fday) + 6)
        dates = pd.date_range(start=stime, end=etime)

        date_before = stime - timedelta(days=1)
        date_after = etime + timedelta(days=1)

        if fday == 1:
            year_before = year - 1
            year_after = year
            fday_before = 361
            fday_after = 9
        elif fday == 361:
            year_before = year
            year_after = year + 1
            fday_before = 353
            fday_after = 1
        else:
            year_before = year
            year_after = year
            fday_before = fday - 8
            fday_after = fday + 8

        self.year = year
        self.fday = fday
        self.dates = dates
        self.dtdic = {dates[i]: i for i in range(8)}
        self.tddic = {i: dates[i] for i in range(8)}

        self.edges = ['before', 'after']
        self.eyears = [year_before, year_after]
        self.edates = [date_before, date_after]
        self.efdays = [fday_before, fday_after]

        # fire mask templates
        self.fm = np.zeros((8, 1200*18, 1200*36), dtype=np.uint8)
        self.fm_before = np.zeros((1200*18, 1200*36), dtype=np.uint8)
        self.fm_after = np.zeros((1200*18, 1200*36), dtype=np.uint8)

        # dataframes
        self.vs = []

        # metadata
        self.meta = []
        self.n_fires = 0

    def create_dataframe(self):

        # fill template, create dataframes
        for H, V in product(Hs, Vs):
            vt = self.fill_tile(self.year, self.fday, H, V)
            if vt is not None:
                self.vs.append(vt)

        # concat dataframes, process neighbours
        if len(self.vs) != 0:

            v = pd.concat(self.vs)
            v['neigh'] = self.process_neighbours(v)
            self.n_fires += len(v)

            # append integer time
            v['t'] = v['dtime'].apply(lambda x: dtdic[x])

            # sort by time
            v.sort_values('t', kind='mergesort', inplace=True,
                          ignore_index=True)

            return v

        else:
            return None

    def fill_tile(self, year, fday, H, V, edate=None, edge=None):

        mod_file = self.validate_file('MOD', year, fday, H, V, edate, edge)
        myd_file = self.validate_file('MYD', year, fday, H, V, edate, edge)

        # no files
        if not mod_file and not myd_file:
            return None

        # only MOD
        if mod_file and not myd_file:
            vt = self.process_fires_single_file(
                'MOD', mod_file, H, V, edate, edge)
            return vt

        # only MYD
        elif myd_file and not mod_file:
            vt = self.process_fires_single_file(
                'MYD', myd_file, H, V, edate, edge)
            return vt

        # both files
        elif mod_file and myd_file:
            vt = self.process_fires_both_files(
                mod_file, myd_file, H, V, edate, edge)
            return vt

    def validate_file(self, satellite, year, fday, H, V,
                      edate=None, edge=None):

        str_year = str(year)
        str_fday = str(fday).zfill(3)
        str_H = str(H).zfill(2)
        str_V = str(V).zfill(2)

        if satellite == 'MOD':
            mxd_data = mod_data
            mxd_files_dict = mod_files_dict

        elif satellite == 'MYD':
            mxd_data = myd_data
            mxd_files_dict = myd_files_dict

        # file exists?
        try:
            mxd_file = mxd_files_dict[
                (satellite, str_year, str_fday, str_H, str_V)]
        except KeyError:
            self.meta.append([year, fday, satellite, H, V, 'file missing'])
            return None

        # file can be opened?
        try:
            mxdds = SD(os.path.join(mxd_data, mxd_file), SDC.READ)
        except HDF4Error:
            self.meta.append([year, fday, satellite, H, V, 'file garbled'])
            return None

        # file has correct date(s)?
        mxd_dates = mxdds.attributes()['Dates'].split()
        mxdds.end()
        mxd_dates = pd.DatetimeIndex(mxd_dates)

        if edge is None:
            try:
                _ = [self.dtdic[mxd_date] for mxd_date in mxd_dates]
                self.meta.append(
                    [year, fday, satellite, H, V,
                     '{} days in file'.format(len(mxd_dates))]
                )
            except KeyError:
                print(mxd_file, '\n', self.dtdic, '\n', mxd_dates, '\n')
                self.meta.append(
                    [year, fday, satellite, H, V, 'file contains wrong dates']
                )
                return None

        else:
            try:
                _ = np.where(mxd_dates == edate)[0][0]
                self.meta.append(
                    [year, fday, satellite, H, V, edge + '_all_good']
                )
            except IndexError:
                self.meta.append(
                    [year, fday, satellite, H, V, edge + '_date_missing']
                )
                return None

        return mxd_file

    def process_fires_single_file(self, satellite, mxd_file, H, V,
                                  edate=None, edge=None):

        if satellite == 'MOD':
            mxd_data = mod_data

        elif satellite == 'MYD':
            mxd_data = myd_data

        mxdds = SD(os.path.join(mxd_data, mxd_file), SDC.READ)

        # dates within file
        mxd_dates = mxdds.attributes()['Dates'].split()
        mxd_dates = pd.DatetimeIndex(mxd_dates)

        if edge:
            self.fill_edge_single_file(mxd_dates, mxdds, H, V, edate, edge)
            mxdds.end()
            return None

        # setting fm
        mxd_fm_full = np.zeros((8, 1200, 1200), dtype=np.uint8)
        mxd_fm = mxdds.select('FireMask').get()

        # change order (see footnote on p.24 of the manual)
        id3 = np.where(mxd_fm == 3)
        id4 = np.where(mxd_fm == 4)
        mxd_fm[id3] = 4
        mxd_fm[id4] = 3

        # in case the file doesn't contain all 8 dates
        days = [self.dtdic[mxd_date] for mxd_date in mxd_dates]
        mxd_fm_full[days] = mxd_fm

        # put into mask
        self.fm[:, V*1200:(V+1)*1200, H*1200:(H+1)*1200] = mxd_fm_full

        # fires to process?
        fires = np.asarray(mxdds.attributes()['FirePix'])
        if (fires > 0).any():

            # maxfrp
            mxd_maxfrps_full = -np.ones((8, 1200, 1200), dtype=np.int32)
            mxd_maxfrps_full[days] = mxdds.select('MaxFRP').get()
            mxd_maxfrps_full = mxd_maxfrps_full[mxd_fm_full >= 7]

            # sample
            mxd_sample_full = np.empty(
                (8, 1200, 1200), dtype=np.float32) * np.nan
            mxd_sample_full[days] = mxdds.select('sample').get()
            mxd_sample_full = mxd_sample_full[mxd_fm_full >= 7]

            # area
            # theta = s * (mxd_sample_full - 676.5)
            # dS = R_e * s * (np.cos(theta) /
            #                 (np.sqrt((R_e/r)**2 - np.sin(theta)**2))-1)
            # dT = r * s * (np.cos(theta) -
            #               np.sqrt((R_e/r)**2 - np.sin(theta)**2))
            # area = dS * dT

            # fire properties
            days, i, j = np.where(mxd_fm_full >= 7)
            confidence = mxd_fm_full[mxd_fm_full >= 7]

            # location
            x = (j + .5) * w + int(H) * T + xmin
            y = ymax - (i + .5) * w - int(V) * T
            lat = y / R
            lon = x / (R * np.cos(lat))
            lat *= 180/np.pi
            lon *= 180/np.pi

            # create grid numbers
            x = int(H) * 1200 + j
            y = int(V) * 1200 + i

            # create dataframe
            vt = pd.DataFrame(data={'lat': lat,
                                    'lon': lon,
                                    'day': days,
                                    'x': x,
                                    'y': y,
                                    'H': H,
                                    'V': V,
                                    'i': i,
                                    'j': j,
                                    'dtime': itemgetter(*days)(self.tddic),
                                    'conf': confidence,
                                    # 'area': area,
                                    'maxFRP': mxd_maxfrps_full,
                                    'satellite': satellite})

            # for fday=361 get rid of fire events from next year
            if self.fday == 361:
                vt = vt[vt.dtime.dt.year == self.year]

            mxdds.end()
            return vt

        else:
            mxdds.end()
            return None

    def process_fires_both_files(self, mod_file, myd_file, H, V,
                                 edate=None, edge=None):

        modds = SD(os.path.join(mod_data, mod_file), SDC.READ)
        mydds = SD(os.path.join(myd_data, myd_file), SDC.READ)

        # dates
        mod_dates = pd.DatetimeIndex(modds.attributes()['Dates'].split())
        myd_dates = pd.DatetimeIndex(mydds.attributes()['Dates'].split())

        if edge:
            self.fill_edge_both_files(
                mod_dates, myd_dates, edate, modds, mydds, edge, H, V)
            modds.end()
            mydds.end()
            return None

        mod_days = [self.dtdic[mod_date] for mod_date in mod_dates]
        myd_days = [self.dtdic[myd_date] for myd_date in myd_dates]

        # firemask (MOD)
        mod_fm_full = np.zeros((8, 1200, 1200), dtype=np.uint8)
        mod_fm = modds.select('FireMask').get()

        # change order (see footnote on p.24 of the manual)
        mod_id3 = np.where(mod_fm == 3)
        mod_id4 = np.where(mod_fm == 4)
        mod_fm[mod_id3] = 4
        mod_fm[mod_id4] = 3

        # in case the file doesn't contain all 8 dates
        mod_fm_full[mod_days] = mod_fm

        # firemas (MYD)
        myd_fm_full = np.zeros((8, 1200, 1200), dtype=np.uint8)
        myd_fm = mydds.select('FireMask').get()

        # change order (see footnote on p.24 of the manual)
        myd_id3 = np.where(myd_fm == 3)
        myd_id4 = np.where(myd_fm == 4)
        myd_fm[myd_id3] = 4
        myd_fm[myd_id4] = 3

        # in case the file doesn't contain all 8 dates
        myd_fm_full[myd_days] = myd_fm

        # union of firemasks
        fm_full = np.where(mod_fm_full >= myd_fm_full,
                           mod_fm_full, myd_fm_full)

        # put into mask
        self.fm[:, V*1200:(V+1)*1200, H*1200:(H+1)*1200] = fm_full

        # check if there are fires
        mod_fires = np.asarray(modds.attributes()['FirePix'])
        myd_fires = np.asarray(mydds.attributes()['FirePix'])
        if (mod_fires > 0).any() or (myd_fires > 0).any():

            # which satellite
            mods = mod_fm_full[fm_full >= 7]
            myds = myd_fm_full[fm_full >= 7]
            mods = np.where(mods >= 7, True, False)
            myds = np.where(myds >= 7, True, False)
            satellite = []
            for mod, myd in zip(mods, myds):
                if mod and not myd:
                    satellite.append('MOD')
                elif myd and not mod:
                    satellite.append('MYD')
                else:
                    satellite.append('both')

            # maxfrp
            mod_maxfrps_full = -np.ones((8, 1200, 1200), dtype=np.int32)
            mod_maxfrps_full[mod_days] = modds.select('MaxFRP').get()
            mod_maxfrps_full = mod_maxfrps_full[fm_full >= 7]

            myd_maxfrps_full = -np.ones((8, 1200, 1200), dtype=np.int32)
            myd_maxfrps_full[myd_days] = mydds.select('MaxFRP').get()
            myd_maxfrps_full = myd_maxfrps_full[fm_full >= 7]

            # union of maxfrps
            maxfrps = np.where(mod_maxfrps_full >= myd_maxfrps_full,
                               mod_maxfrps_full, myd_maxfrps_full)

            # sample
            mod_sample_full = np.empty(
                (8, 1200, 1200), dtype=np.float32) * np.nan
            mod_sample_full[mod_days] = modds.select('sample').get()
            mod_sample_full = mod_sample_full[fm_full >= 7]

            myd_sample_full = np.empty(
                (8, 1200, 1200), dtype=np.float32) * np.nan
            myd_sample_full[myd_days] = mydds.select('sample').get()
            myd_sample_full = myd_sample_full[fm_full >= 7]

            # areas
            # mod_theta = s * (mod_sample_full - 676.5)
            # mod_dS = R_e * s * (np.cos(mod_theta) /
            #                     (np.sqrt((R_e/r)**2 -
            #                              np.sin(mod_theta)**2))-1)
            # mod_dT = r * s * (np.cos(mod_theta) -
            #                   np.sqrt((R_e/r)**2 - np.sin(mod_theta)**2))
            # mod_area = mod_dS * mod_dT

            # myd_theta = s * (myd_sample_full - 676.5)
            # myd_dS = R_e * s * (np.cos(myd_theta) /
            #                     (np.sqrt((R_e/r)**2 -
            #                              np.sin(myd_theta)**2))-1)
            # myd_dT = r * s * (np.cos(myd_theta) -
            #                   np.sqrt((R_e/r)**2 - np.sin(myd_theta)**2))
            # myd_area = myd_dS * myd_dT

            # union of areas
            # area = np.where(mod_area <= myd_area, mod_area, myd_area)

            # fire properties
            days, i, j = np.where(fm_full >= 7)
            confidence = fm_full[fm_full >= 7]

            x = (j + .5) * w + int(H) * T + xmin
            y = ymax - (i + .5) * w - int(V) * T
            lat = y / R
            lon = x / (R * np.cos(lat))
            lat *= 180/np.pi
            lon *= 180/np.pi

            # create grid numbers
            x = int(H) * 1200 + j
            y = int(V) * 1200 + i

            # create dataframe
            vt = pd.DataFrame(data={'lat': lat,
                                    'lon': lon,
                                    'day': days,
                                    'x': x,
                                    'y': y,
                                    'H': H,
                                    'V': V,
                                    'i': i,
                                    'j': j,
                                    'dtime': itemgetter(*days)(self.tddic),
                                    'conf': confidence,
                                    # 'area': area,
                                    'maxFRP': maxfrps,
                                    'satellite': satellite})

            # for fday=361 get rid of fire events from next year
            if self.fday == 361:
                vt = vt[vt.dtime.dt.year == self.year]

            modds.end()
            mydds.end()
            return vt

        else:
            modds.end()
            mydds.end()
            return None

    def process_neighbours(self, v):

        # fill before and after templates
        # (we don't need to fill 'after' for fday=361)
        if self.fday == 361:
            edges = ['before']
        else:
            edges = self.edges

        for eyear, efday, edate, edge in zip(self.eyears,
                                             self.efdays,
                                             self.edates,
                                             edges):
            for H, V in product(Hs, Vs):
                self.fill_tile(eyear, efday, H, V, edate=edate, edge=edge)

        # classify each fire's neighbourhood
        box = np.zeros((3, 3, 3), dtype=np.uint8)
        neighs = np.zeros(len(v), dtype=np.uint8)
        c = 0
        for day, y, x in zip(v['day'], v['y'], v['x']):
            if day == 0:
                box[0] = self.fm_before.take(
                    range(y-1, y+2), mode='wrap', axis=0).take(
                        range(x-1, x+2), mode='wrap', axis=1)

                box[1:] = self.fm[:2].take(
                    range(y-1, y+2), mode='wrap', axis=1).take(
                        range(x-1, x+2), mode='wrap', axis=2)
            elif day == 7:
                box[2] = self.fm_after.take(
                    range(y-1, y+2), mode='wrap', axis=0).take(
                        range(x-1, x+2), mode='wrap', axis=1)

                box[:2] = self.fm[6:8].take(
                    range(y-1, y+2), mode='wrap', axis=1).take(
                        range(x-1, x+2), mode='wrap', axis=2)
            else:
                box = self.fm[day-1:day+2].take(
                    range(y-1, y+2), mode='wrap', axis=1).take(
                        range(x-1, x+2), mode='wrap', axis=2)

            # find minimum
            neighs[c] = box.min()

            c += 1

        return neighs

    def fill_edge_single_file(self, mxd_dates, mxdds, H, V, edate, edge):

        ind = np.where(mxd_dates == edate)[0][0]
        mxd_fm = mxdds.select('FireMask').get()[ind]
        id3 = np.where(mxd_fm == 3)
        id4 = np.where(mxd_fm == 4)
        mxd_fm[id3] = 4
        mxd_fm[id4] = 3
        if edge == 'before':
            self.fm_before[V*1200:(V+1)*1200, H*1200:(H+1)*1200] = mxd_fm
        elif edge == 'after':
            self.fm_after[V*1200:(V+1)*1200, H*1200:(H+1)*1200] = mxd_fm

    def fill_edge_both_files(self, mod_dates, myd_dates, edate, modds, mydds,
                             edge, H, V):

        mod_ind = np.where(mod_dates == edate)[0][0]
        myd_ind = np.where(myd_dates == edate)[0][0]

        mod_fm = modds.select('FireMask').get()[mod_ind]
        myd_fm = mydds.select('FireMask').get()[myd_ind]

        mod_id3 = np.where(mod_fm == 3)
        mod_id4 = np.where(mod_fm == 4)
        mod_fm[mod_id3] = 4
        mod_fm[mod_id4] = 3

        myd_id3 = np.where(myd_fm == 3)
        myd_id4 = np.where(myd_fm == 4)
        myd_fm[myd_id3] = 4
        myd_fm[myd_id4] = 3

        fm_edge = np.where(mod_fm >= myd_fm, mod_fm, myd_fm)

        if edge == 'before':
            self.fm_before[V*1200:(V+1)*1200, H*1200:(H+1)*1200] = fm_edge
        elif edge == 'after':
            self.fm_after[V*1200:(V+1)*1200, H*1200:(H+1)*1200] = fm_edge

    def land_water_state(self, qa):
        bits = self._qa_encoding(qa)[:2]
        if bits == '00':
            state = 0  # 'water'  # blue
        elif bits == '01':
            state = 1  # 'land'  # green
        elif bits == '10':
            state = 2  # 'coast'  # black
        elif bits == '11':
            state = 3  # 'missing data'
        return state

    def day_night(self, qa):
        bit = self._qa_encoding(qa)[2]
        if bit == 0:
            day = False
        else:
            day = True
        return day

    @staticmethod
    def _qa_encoding(qa):
        bits = format(qa, '008b')[::-1]
        return bits

    @staticmethod
    def open_file(satellite, year, fday, H, V):

        str_year = str(year)
        str_fday = str(fday).zfill(3)
        str_H = str(H).zfill(2)
        str_V = str(V).zfill(2)

        if satellite == 'MOD':
            mxd_data = mod_data
            mxd_files_dict = mod_files_dict

        elif satellite == 'MYD':
            mxd_data = myd_data
            mxd_files_dict = myd_files_dict

        # file exists?
        try:
            mxd_file = mxd_files_dict[
                (satellite, str_year, str_fday, str_H, str_V)]
        except KeyError:
            print('file does not exist')
            return None

        # file is garbled?
        try:
            mxdds = SD(os.path.join(mxd_data, mxd_file), SDC.READ)
        except HDF4Error:
            print('file is garbled')
            return None

        return mxdds


def main(year):

    # print('processing {} ..'.format(year))

    vs = []
    metas = []
    for fday in np.arange(1, 365, 8):

        # extract and process MOD14A1/MYD14A1
        p = ProcessYearFday(year, fday)
        vs.append(p.create_dataframe())
        metas.append(pd.DataFrame(data=p.meta))

    # concat and add countries
    try:
        # concat
        v = pd.concat(vs)

        if countries:
            vg = gpd.GeoDataFrame(
                crs='epsg:4326',
                geometry=[Point(xy) for xy in zip(v['lon'], v['lat'])])
            vc = gpd.sjoin(
                vg, country_boundaries[['NAME_EN', 'CONTINENT', 'geometry']],
                how='left', op='intersects')
            v['country'] = vc['NAME_EN'].values
            v['continent'] = vc['CONTINENT'].values

    except ValueError:
        v = pd.DataFrame()
    meta = pd.concat(metas)

    return v, meta


if __name__ == '__main__':

    years = np.arange(min_year, max_year + 1)

    vs, metas = zip(*Pool(processes=args.processes).map(main, years))

    # concat meta data
    meta = pd.concat(metas)

    # set index
    meta.index = range(len(meta))

    # set column names of meta data
    meta.columns = ['year', 'fday', 'satellite', 'H', 'V', 'meta']

    # store meta dataframe
    meta.to_pickle(os.path.join(cwd, 'mxd14a1_meta.pickle'))
    print('stored {}'.format(os.path.join(cwd, 'mxd14a1_meta.pickle')))

    # concat fire event dataframes
    v = pd.concat(vs)

    # set index
    v.index = range(len(v))

    # add descriptive neighbors column
    v.loc[:, 'neigh_int'] = v['neigh']
    v.loc[:, 'neigh'] = v['neigh'].apply(lambda x: ndict[x])

    # create geographical location labels
    v.loc[:, 'gl'] = v.groupby(['x', 'y']).grouper.group_info[0]

    # get rid of needless columns
    del v['day']

    # dtypes
    v = v.astype({
        'x': np.uint16,
        'y': np.uint16,
        'H': np.uint8,
        'V': np.uint8,
        'i': np.uint16,
        'j': np.uint16,
        't': np.uint16,
        'gl': np.uint32,
    })

    # store as hdf
    store = pd.HDFStore(os.path.join(cwd, 'v.h5'), mode='w')
    store.append('v', v, format='t', data_columns=True, index=False)
    store.create_table_index('v', columns=['t', 'dtime'], kind='full')
    store.close()
    print('stored {}'.format(os.path.join(cwd, 'v.h5')))
