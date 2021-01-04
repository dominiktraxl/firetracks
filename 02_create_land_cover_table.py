
# Copyright (C) 2020 by
# Dominik Traxl <dominik.traxl@posteo.org>
# All rights reserved.
# MIT license.

import os
import argparse
import multiprocessing as mp
from multiprocessing import Pool
from itertools import product

import numpy as np
import pandas as pd
from pyhdf.SD import SD, SDC
from pyhdf.error import HDF4Error

# argument parameters
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    'lc-type',
    help="which MCD12Q1 Science Data Set to use (short name)",
    choices=[
        'LC_Type1',
        'LC_Type2',
        'LC_Type3',
        'LC_Type4',
        'LC_Type5',
        'LC_Prop1',
        'LC_Prop2',
        'LC_Prop3',
        'LC_Prop1_Assessment',
        'LC_Prop2_Assessment',
        'LC_Prop3_Assessment',
        'QC',
        'LW'],
    type=str,
)
parser.add_argument(
    '-p', '--processes',
    help="number of processes to use for the computation",
    type=int,
    default=mp.cpu_count(),
)
args = parser.parse_args()
lc_type = getattr(args, 'lc-type')

# file system
cwd = os.getcwd()
mcd_data = os.path.join(cwd, 'MCD12Q1')

# load fire event table
v = pd.read_hdf(os.path.join(cwd, 'v.h5'), 'v', columns=['dtime', 'x', 'y'])


# to extract metadata from file
def meta_from_file(f):
    satellite = f[:3]
    year = f[9:13]
    fday = f[13:16]
    H = f[18:20]
    V = f[21:23]
    return satellite, year, fday, H, V


# mcd12q1 files
mcd_files = os.listdir(mcd_data)
mcd_files.sort()
mcd_files_dict = {meta_from_file(fname): fname for fname in mcd_files if
                  fname.endswith('.hdf')}


# MODIS tiles
Hs = np.arange(0, 36)
Vs = np.arange(0, 18)


class CreateLCM(object):

    def __init__(self, year):

        self.year = year - 1
        self.fday = 1

        self.lcm_meta = []
        self.lcm = np.ones((2400*18, 2400*36), dtype=np.uint8) * 254

    def create_lcm(self):

        for H, V in product(Hs, Vs):

            mcd_file = self.validate_file('MCD', self.year, self.fday, H, V)

            if mcd_file is not None:

                # open file
                mcdds = SD(os.path.join(mcd_data, mcd_file), SDC.READ)

                # load land cover mask
                lcm = mcdds.select(lc_type).get()
                mcdds.end()

                self.lcm[V*2400:(V+1)*2400, H*2400:(H+1)*2400] = lcm

        return self.lcm

    def validate_file(self, satellite, year, fday, H, V):

        str_year = str(year)
        str_fday = str(fday).zfill(3)
        str_H = str(H).zfill(2)
        str_V = str(V).zfill(2)

        # file exists?
        try:
            mcd_file = mcd_files_dict[
                (satellite, str_year, str_fday, str_H, str_V)]
        except KeyError:
            self.lcm_meta.append([year, H, V, 'missing'])
            return None

        # file can be opened?
        try:
            _ = SD(os.path.join(mcd_data, mcd_file), SDC.READ)
            _.end()
        except HDF4Error:
            self.lcm_meta.append([year, H, V, 'garbled'])
            return None

        self.lcm_meta.append([year, H, V, 'all_good'])

        return mcd_file


def process_land_cover(vt, lcm):

    # land cover and flags
    lc1234 = np.zeros((len(vt), 4), dtype=np.uint8)

    # process land cover for each fire
    c = 0
    for y, x in zip(vt['y'], vt['x']):

        # land cover box
        box = lcm[2*y:2*y+2, 2*x:2*x+2]

        # store original land covers
        lc1234[c] = box.flatten().tolist()

        c += 1

    vt_lc = pd.DataFrame(lc1234)
    vt_lc.columns = ['lc1', 'lc2', 'lc3', 'lc4']

    return vt_lc


def main(year):

    # load land cover data and create meta file
    p = CreateLCM(year)
    lcm = p.create_lcm()

    # store meta dataframe
    meta = pd.DataFrame(data=p.lcm_meta)

    # find land covers for each fire event
    vt = v.loc[v['dtime'].dt.year == year]
    vt_lc = process_land_cover(vt, lcm)

    return vt_lc, meta


if __name__ == '__main__':

    # which years to process
    min_year = v['dtime'].dt.year.min()
    max_year = v['dtime'].dt.year.max() + 1
    years = np.arange(min_year, max_year)

    # process land cover types
    vt_lcs, metas = zip(*Pool(args.processes).map(main, years))

    # concat meta data
    meta = pd.concat(metas)

    # set index
    meta.index = range(len(meta))

    # set column names of meta data
    meta.columns = ['year', 'H', 'V', 'meta']

    # store meta dataframe
    meta.to_pickle(os.path.join(cwd, 'mcd12q1_meta.pickle'))
    print('stored {}'.format(os.path.join(cwd, 'mcd12q1_meta.pickle')))

    # concat land cover dataframes
    v_lc = pd.concat(vt_lcs, axis=0, sort=False)

    # set index
    v_lc.index = range(len(v_lc))

    # store dataframe as hdf
    v_lc_file = os.path.join(cwd, 'v_{}.h5'.format(lc_type))
    store = pd.HDFStore(v_lc_file, mode='w')
    store.append('v_{}'.format(lc_type), v_lc, format='t', data_columns=True,
                 index=False)
    store.close()
    print('stored {}'.format(v_lc_file))
