
# Copyright (C) 2020 by
# Dominik Traxl <dominik.traxl@posteo.org>
# All rights reserved.
# MIT license.

import os

import pandas as pd
import deepgraph as dg

# file system
cwd = os.getcwd()

# fire events (index)
store = pd.HDFStore(os.path.join(cwd, 'v.h5'), mode='r')
n = store.get_storer('v').nrows
store.close()
v = pd.DataFrame(index=range(n))

# load edges
e = pd.read_pickle(os.path.join(cwd, 'e.pickle'))

# find components
g = dg.DeepGraph(v, e)
g.append_cp()
cps = g.v['cp'].values

# free up memory
del g
del e

# load v.h5
v = pd.read_hdf(os.path.join(cwd, 'v.h5'))

# append cp column
v['cp'] = cps

# store as hdf (overwrite)
store = pd.HDFStore(os.path.join(cwd, 'v.h5'), mode='w')
store.append('v', v, format='t', data_columns=True, index=False)
store.create_table_index('v', columns=['t', 'dtime'], kind='full')
store.close()
print('overwrote {}'.format(os.path.join(cwd, 'v.h5')))
