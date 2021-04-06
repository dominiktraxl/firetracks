
# Copyright (C) 2020 by
# Dominik Traxl <dominik.traxl@posteo.org>
# All rights reserved.
# MIT license.

import os
import multiprocessing as mp
from multiprocessing import Pool
import argparse

import numpy as np
import pandas as pd

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

# parameters
min_perc = .8  # for dominant land use type of a component
n_proc = 100

# file system
cwd = os.getcwd()

# load land cover table, location labels, time and component information
v = pd.read_hdf(os.path.join(cwd, 'v.h5'), columns=['gl', 't', 'cp'])
v_lc = pd.read_hdf(os.path.join(cwd, 'v_{}.h5'.format(lc_type)))
v_lc['cp'] = v['cp'].values
v_lc['gl'] = v['gl'].values
v_lc['t'] = v['t'].values
del v

# load cp.h5 index for sorting
cp = pd.read_hdf(os.path.join(cwd, 'cp.h5'), columns=['cp', 'dtime_min'])

# unique land covers
lcs = np.sort(pd.unique(v_lc[['lc1', 'lc2', 'lc3', 'lc4']].values.ravel('K')))

# index array
n_cps = v_lc['cp'].max() + 1
n_proc = min(n_proc, n_cps)
pos_array = np.array(np.linspace(0, n_cps, n_proc), dtype=int)


# lc value counts
def lc_vc(group):
    values = group[['lc1', 'lc2', 'lc3', 'lc4']].values.ravel('K')
    lc, count = np.unique(values, return_counts=True)
    df = pd.Series(index=['{}_{}'.format('lc', lcn) for lcn in lcs], data=0)
    df.loc[['{}_{}'.format('lc', lcn) for lcn in lc]] = count
    return df


def main(i):

    # print('starting {}/{}'.format(i+1, n_proc))

    # subset v_lc
    from_cp = pos_array[i]
    to_cp = pos_array[i+1]
    vt_lc = v_lc.loc[(v_lc['cp'] >= from_cp) & (v_lc['cp'] < to_cp)]

    # compute land cover value counts for each cp
    lcvc = vt_lc.groupby(['cp', 'gl']).nth(0)
    glcvc = lcvc.groupby('cp')
    lc_counts = glcvc.apply(lc_vc)

    # lc proportions
    plc = lc_counts.divide(lc_counts.sum(axis=1), axis=0)
    plc.columns = ['p{}'.format(col) for col in plc.columns]

    # dominant land cover
    dlc = plc.idxmax(axis=1)
    dlc = dlc.apply(lambda x: x[x.find('_') + 1:])
    dlc.loc[(plc < min_perc).all(axis=1)] = 'None'
    dlc.name = 'dlc'

    # first land cover types
    flcs = []
    for n in [1, 2, 3, 4]:
        flc = vt_lc.groupby(['cp', 't', 'lc{}'.format(n)]).size()
        flc = flc.unstack(fill_value=0)
        flc = flc.groupby('cp').nth(0)
        for lc in lcs:
            if lc not in flc.columns.values:
                flc.loc[:, lc] = 0
        flc = flc[lcs]
        flcs.append(flc)
    flc = sum(flcs)
    flc.columns = ['flc_{}'.format(lc) for lc in lcs]

    # concat
    cpt_lc = pd.concat((lc_counts, plc, dlc, flc), axis=1)

    return cpt_lc


if __name__ == '__main__':

    indices = np.arange(0, n_proc - 1)

    # compute component tables
    cpt_lcs = Pool(args.processes).map(main, indices)

    # concat
    cp_lc = pd.concat(cpt_lcs)

    # sort like cp.h5
    cp_lc = cp_lc.loc[cp['cp'].values]

    # add dtime
    cp_lc['dtime_min'] = cp['dtime_min'].values

    # reset index
    cp_lc.reset_index(inplace=True)

    # store cp as hdf5
    cp_lc_file = os.path.join(cwd, 'cp_{}.h5'.format(lc_type))
    store = pd.HDFStore(cp_lc_file, mode='w')
    store.append('cp_{}'.format(lc_type), cp_lc, format='t', data_columns=True,
                 index=False)
    store.create_table_index('cp_{}'.format(lc_type), columns=['dtime_min'],
                             kind='full')
    store.close()
    print('stored {}'.format(cp_lc_file))
