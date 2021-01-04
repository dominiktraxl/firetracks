
# Copyright (C) 2020 by
# Dominik Traxl <dominik.traxl@posteo.org>
# All rights reserved.
# MIT license.

import os

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import deepgraph as dg

# file system
cwd = os.getcwd()

# neighbor dict
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

# load fire events and component information
store = pd.HDFStore(os.path.join(cwd, 'v.h5'), mode='r')
v = store.select(
    'v', columns=['t', 'dtime', 'lat', 'lon', 'maxFRP', 'neigh_int', 'gl']
)
v['cp'] = store['v_cp']
store.close()

# feature functions, will be applied on each component
feature_funcs = {
    't': ['min', 'max'],
    'dtime': ['min', 'max'],
    'lat': ['mean'],
    'lon': ['mean'],
    'maxFRP': ['mean'],
    'neigh_int': ['min'],
}

# create spatiotemporal components
g = dg.DeepGraph(v)
cp, gv = g.partition_nodes('cp', feature_funcs, return_gv=True)

# rename neighbor column
cp.loc[:, 'neigh_min'] = cp['neigh_int_min'].apply(lambda x: ndict[x])

# compute lifetime
cp.loc[:, 'duration'] = cp['t_max'] - cp['t_min'] + 1

# compute area
cp.loc[:, 'unique_gls'] = gv['gl'].nunique()
cp.loc[:, 'area'] = cp['unique_gls'] * 0.92662543305**2  # page 50 manual

# compute expansion (km^2 day^-1)
cp.loc[:, 'expansion'] = cp['area'] / cp['duration']

# add countries
countries_shp = 'ne_10m_admin_0_countries.shp'
if os.path.isfile(os.path.join(cwd, 'countries', countries_shp)):
    country_boundaries = gpd.read_file(
        os.path.join(cwd, 'countries', countries_shp))
    cpg = gpd.GeoDataFrame(
        crs='epsg:4326',
        geometry=[Point(xy) for xy in zip(cp['lon_mean'], cp['lat_mean'])])
    cpc = gpd.sjoin(
        cpg, country_boundaries[['NAME_EN', 'CONTINENT', 'geometry']],
        how='inner', op='intersects')
    cp['country'] = cpc['NAME_EN']
    cp['continent'] = cpc['CONTINENT']


# dtypes
cp = cp.astype({'unique_gls': np.uint32})

# store cp as hdf5
cp_file = os.path.join(cwd, 'cp.h5')
store = pd.HDFStore(cp_file, mode='w')
store.append('cp', cp, format='t', data_columns=True, index=False)
store.close()
print('stored {}'.format(cp_file))
