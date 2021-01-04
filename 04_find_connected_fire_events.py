
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

# add component column as new node to v.h5
store = pd.HDFStore(os.path.join(cwd, 'v.h5'), mode='r+')
store.append('v_cp', g.v['cp'], format='t', data_columns=True, index=False)
store.close()
print("stored component column 'cp' as new node 'v_cp' in {}".format(
    os.path.join(cwd, 'v.h5')))
