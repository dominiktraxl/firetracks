
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
import deepgraph as dg

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

# computation parameters
min_chunk_size = 4000
max_pairs = 2e8
n_proc = 200

# file system
cwd = os.getcwd()
os.makedirs(os.path.join(cwd, 'logs'), exist_ok=True)


def grid_2d_dx(x_s, x_t):
    """x-distance on 2d-grid."""
    x_s = np.array(x_s, dtype=int)
    x_t = np.array(x_t, dtype=int)

    dx = x_t - x_s

    return dx


def grid_2d_dy(y_s, y_t):
    """y-distance on 2d-grid."""
    y_s = np.array(y_s, dtype=int)
    y_t = np.array(y_t, dtype=int)

    dy = y_t - y_s

    return dy


def grid_2d_octogonal_dx(dx, sources, targets):
    """Select first neighbours on 2d-grid, including diagonals."""
    dx_a = np.abs(dx)

    sources = sources[dx_a <= 1]
    targets = targets[dx_a <= 1]

    return sources, targets


def grid_2d_octogonal_dy(dy, sources, targets):
    """Select first neighbours on 2d-grid, including diagonals."""
    dy_a = np.abs(dy)

    sources = sources[dy_a <= 1]
    targets = targets[dy_a <= 1]

    return sources, targets


# use time as the fast track feature
ft_feature = ('t', 1)

# define relations to select from
connectors = [grid_2d_dx, grid_2d_dy]

# define selectors
selectors = [grid_2d_octogonal_dx, grid_2d_octogonal_dy, 'ft_selector']

# force dtypes
r_dtype_dic = {
    'ft_r': np.bool,
    'dx': np.int8,
    'dy': np.int8,
}

# index array
store = pd.HDFStore(os.path.join(cwd, 'v.h5'), mode='r')
n = store.get_storer('v').nrows
pos_array = np.array(np.linspace(0, n, n_proc), dtype=int)
store.close()


# parallel computation
def create_ei(i):

    # print('starting {}/{}'.format(i+1, n_proc))

    from_pos = pos_array[i]
    to_pos = pos_array[i+1]

    v = pd.HDFStore(os.path.join(cwd, 'v.h5'), mode='r')

    logfile = os.path.join(
        cwd, 'logs', '{:04d}_hdf_mcs{}_mp{}_n_proc{}.txt'.format(
            i, min_chunk_size, max_pairs, n_proc)
    )

    # initiate DataGraph
    g = dg.DeepGraph(v)

    # create links
    g.create_edges_ft(
        ft_feature=ft_feature, connectors=connectors,
        selectors=selectors, r_dtype_dic=r_dtype_dic,
        min_chunk_size=min_chunk_size, max_pairs=max_pairs,
        from_pos=from_pos, to_pos=to_pos,
        verbose=False, logfile=logfile,
    )
    v.close()

    # rename fast track weights
    g.e.rename(columns={'ft_r': 'dt'}, inplace=True)

    return g.e


if __name__ == '__main__':

    indices = np.arange(0, n_proc - 1)

    # compute edges
    eis = Pool(args.processes).map(create_ei, indices)

    # concat
    e = pd.concat(eis)

    # store dataframe
    e_file = os.path.join(cwd, 'e.pickle')
    e.to_pickle(e_file)
    print('stored {}'.format(e_file))
