
# Copyright (C) 2020 by
# Dominik Traxl <dominik.traxl@posteo.org>
# Taylor Smith <tasmith@uni-potsdam.de>
# All rights reserved.
# MIT license.

import os
import multiprocessing as mp
from multiprocessing import Pool
import argparse

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon

# argument parameters
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    '-s', '--slice-by-time',
    help="create (multi)polygon for each time slice of a component",
    action='store_true',
)
parser.add_argument(
    '-p', '--processes',
    help="number of processes to use for the computation",
    type=int,
    default=mp.cpu_count(),
)
args = parser.parse_args()

# parameters
n_proc = 100

# file system
cwd = os.getcwd()
if args.slice_by_time:
    fname = os.path.join(cwd, 'cpt_poly')
else:
    fname = os.path.join(cwd, 'cp_poly')

# MODIS constants
# the height and width of each MODIS tile in the projection plane [m]
T = 1111950.5196666666
# the western/eastern limit of the projection plane [m]
xmin = -20015109.354
xmax = 20015109.354
# the northern/southern limit of the projection plane [m]
ymax = 10007554.677
ymin = -10007554.677
# the actual size of a "1-km" MODIS sinusoidal grid cell (926.6254330 m)
w = T/1200.

# load fire event dataframe
store = pd.HDFStore(os.path.join(cwd, 'v.h5'), mode='r')
v = store.select('v', columns=['lat', 'lon', 'H', 'V', 'i', 'j', 't'])
v['cp'] = store['v_cp']
store.close()

# convert to geodataframe
v = gpd.GeoDataFrame(
    v,
    crs='epsg:4326',
    geometry=[Point(xy) for xy in zip(v['lon'], v['lat'])]
)

# index array
n_cps = v['cp'].max() + 1
n_proc = min(n_proc, n_cps)
pos_array = np.array(np.linspace(0, n_cps, n_proc), dtype=int)


def corners_to_poly(H, V, i, j):
    """Convert MODIS coordinates to geographic coordinates.

    Take the H/V (MODIS box) and i/j (pixel within box) coordinates and convert
    to geographic coordinates.

    Adapted from: https://code.env.duke.edu/projects/mget/wiki/SinusoidalMODIS

    """

    # x/y min/max
    min_x = xmin + H*T + j * w
    max_x = xmin + H*T + (j + 1.) * w
    min_y = ymax - V*T - i * w
    max_y = ymax - V*T - (i + 1) * w

    # check for edge wrapping
    if min_y < ymin:
        min_y = ymin - min_y
    if max_y > ymax:
        max_y = ymax - max_y
    if min_x < xmin:
        min_x = xmin - min_x
    if max_x > xmax:
        max_x = xmax - max_x

    # create shapely polygon from corner coordinates
    geom = Polygon(
        ((min_x, max_y),
         (max_x, max_y),
         (max_x, min_y),
         (min_x, min_y),
         (min_x, max_y))
    )

    return geom


def to_poly(group):
    """Convert set of fire events to polygons."""

    # create geometries from events
    geometries = []
    for _, row in group.iterrows():
        geometry = corners_to_poly(row['H'], row['V'], row['i'], row['j'])
        geometries.append(geometry)

    # convert to single polygon
    vt_poly = gpd.GeoDataFrame(
        crs='+proj=sinu +R=6371007.181 +nadgrids=@null +wktext',
        geometry=geometries,
    )

    # dissolve polygons
    vt_poly['dissolvefield'] = 1
    vt_poly = vt_poly.dissolve('dissolvefield')

    # reproject to WGS84
    vt_poly = vt_poly.to_crs('epsg:4326')

    return vt_poly


def main(i):

    # print('starting {}/{}'.format(i+1, n_proc))

    # subset v by components
    from_cp = pos_array[i]
    to_cp = pos_array[i+1]
    vt = v.loc[(v['cp'] >= from_cp) & (v['cp'] < to_cp)]

    # group by component, and optionally time
    if args.slice_by_time:
        gvt = vt.groupby(['cp', 't'])
    else:
        gvt = vt.groupby('cp')

    # create geodataframe
    cpt_poly = gvt.apply(to_poly)

    # drop index level
    cpt_poly.index = cpt_poly.index.droplevel('dissolvefield')

    return cpt_poly


if __name__ == '__main__':

    indices = np.arange(0, n_proc - 1)

    # compute polygons
    cpt_polys = Pool(processes=args.processes).map(main, indices)

    # concat
    cp_poly = pd.concat(cpt_polys)

    # add area
    cp_poly['area'] = cp_poly['geometry'].to_crs({'proj':'cea'}).map(
        lambda x: x.area / 10**6)

    # add perimeter
    cp_poly['perimeter'] = cp_poly['geometry'].to_crs({'proj':'cea'}).map(
        lambda x: x.length / 10**3)

    # set index
    cp_poly.reset_index(inplace=True)
    cp_poly.index = range(len(cp_poly))

    # dtypes
    if args.slice_by_time:
        cp_poly = cp_poly.astype({'t': np.uint16})  # not stored as such :/

    # store
    cp_poly.to_file(fname + '.gpkg', driver='GPKG')
    print('stored {}'.format(fname + '.gpkg'))
