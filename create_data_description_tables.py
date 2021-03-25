
# Copyright (C) 2020 by
# Dominik Traxl <dominik.traxl@posteo.org>
# All rights reserved.
# MIT license.

import os
import pandas as pd

# file system
cwd = os.getcwd()


def convert_to_different_formats(df, name):

    # create dataframe
    df = pd.DataFrame(data=df)

    # to markdown
    df_md = df.copy()
    for col in df_md.columns:
        df_md[col] = df_md[col].str.replace('*', '&ast;', regex=True)

    # to other
    # ..

    # set index
    df_md.set_index('Name', inplace=True)

    # store as markdown file
    with open(os.path.join(cwd, name + '.md'), 'w') as f:
        df_md.to_markdown(f)


# ----------------------------------------------------------------------------
# v.h5

v = {'Name':

     ['lat', 'lon', 'x', 'y', 'H', 'V', 'i', 'j', 'dtime', 'conf',
      'maxFRP', 'satellite', 'neigh', 't', 'country', 'continent', 'neigh_int',
      'gl', 'cp'],

     'Description':

     ['location latitude',
      'location longitude',
      'x-coordinate on global sinusoidal MODIS grid',
      'y-coordinate on global sinusoidal MODIS grid',
      'horizontal MODIS tile coordinate',
      'vertical MODIS tile coordinate',
      'row coordinate of the grid cell within MODIS tile (H, V)',
      'column coordinate of the grid cell within MODIS tile (H, V)',
      'date (YYYY-MM-DD)',
      'detection confidence [7: low, 8: nominal, 9: high]',
      'maximum fire radiative power',
      'which satellite detected the fire [MOD, MYD, both]',
      'string representation of "neigh_int"',
      'days since 2002-01-01',
      'country of occurrence',
      'continent of occurrence',
      'minimum of fire pixel classes of neighboring grid cells',
      'location ID on the global sinusoidal MODIS grid',
      'component membership label'],

     'Unit':

     ['degress', 'degrees', '-', '-', '-', '-', '-', '-', '-', '-', 'MW*10',
      '-', '-', 'days since 2002-01-01', '-', '-', '-', '-', '-'],

     'Valid Range':

     ['[-180, 180]', '[-90, 90]', '[0, 36*1200-1]', '[0, 18*1200-1]',
      '[0, 35]', '[0, 17]', '[0, 1199]', '[0, 1199]', '>= 2002-01-01',
      '[7, 9]', '>= 0', '-', '-', '>= 0', '-', '-', '[0, 9]',
      '[0, 36*1200*18*1200-1]', '>= 0'],

     'Data Type':

     ['float64', 'float64', 'uint16', 'uint16', 'uint8', 'uint8', 'uint16',
      'uint16', 'datetime64', 'uint8', 'int32', 'string', 'string', 'uint16',
      'string', 'string', 'uint8', 'uint32', 'int64']}


# ----------------------------------------------------------------------------
# v_lc.h5

v_lc = {'Name':

        ['lc1', 'lc2', 'lc3', 'lc4'],

        'Description':

        ['land cover type of subpixel 1 (numerical)',
         'land cover type of subpixel 2 (numerical)',
         'land cover type of subpixel 3 (numerical)',
         'land cover type of subpixel 4 (numerical)',],

        'Unit':

        ['-', '-', '-', '-'],

        'Valid Range':

        ['[0, 255]', '[0, 255]', '[0, 255]', '[0, 255]'],

        'Data Type':

        ['uint8', 'uint8', 'uint8', 'uint8']}


# ----------------------------------------------------------------------------
# cp.h5

cp = {'Name':

      ['n_nodes', 't_min', 't_max', 'dtime_min', 'dtime_max', 'lat_mean',
       'lon_mean', 'maxFRP_mean', 'maxFRP_sum', 'neigh_int_min', 'neigh_min',
       'duration', 'unique_gls', 'area', 'expansion', 'country', 'continent'],

      'Description':

      ['number of constituent fire events',
       'ignition date (days since 2002-01-01)',
       'extinction date (days since 2002-01-01)', 'ignition date (YYYY-MM-DD)',
       'extinction date (YYYY-MM-DD)', 'mean location latitude',
       'mean location longitude', 'mean maximum fire radiative power',
       'sum of maximum fire radiative powers',
       'minimum of "neigh_int" values of constituent fire events',
       'string representation of "neigh_int_min"', 'fire duration',
       'number of grid locations burnt', 'total area burnt',
       'average daily fire expansion',
       'country of occurrence', 'continent of occurrence'],

      'Unit':

      ['-', 'days since 2002-01-01', 'days since 2002-01-01', '-', '-',
       'degrees', 'degrees', 'MW*10', 'MW*10', '-', '-', 'days', '-', 'km^2',
       'km^2 day^-1', '-', '-'],

      'Valid Range':

      ['>= 1', '>= 0', '>= 0', '>= 2002-01-01', '>= 2002-01-01', '[-180, 180]',
       '[-90, 90]', '>= 0', '>= 0', '[0, 9]', '-', '>= 1', '>= 1',
       '>= 0.86 (1 MODIS pixel)', '> 0', '-', '-'],

      'Data Type':

      ['int64', 'uint16', 'uint16', 'datetime64', 'datetime64', 'float64',
       'float64', 'float64', 'float64', 'uint8', 'string', 'uint16', 'uint32',
       'float64', 'float64', 'string', 'string']}


# ----------------------------------------------------------------------------
# cp_lc.h5

cp_lc = {'Name':

         ['dlc', 'lc_X', 'plc_X', 'flc_X'],

         'Description':

         ['dominant land cover type*',
          'number of subpixels burnt belonging to land cover X',
          'proportion of subpixels burnt belonging to land cover X',
          'number of ignition subpixels belonging to land cover X'],

         'Unit':

         ['-', '-', '-', '-'],

         'Valid Range':

         ['-', '>= 0', '[0, 1]', '>= 0'],

         'Data Type':

         ['string', 'int64', 'float64', 'int64'],}


# ----------------------------------------------------------------------------
# cp_poly

cp_poly = {'Name':

           ['cp', 'area', 'perimeter', 'geometry'],

           'Description':

           ['component membership label', 'total area burnt',
            'final perimeter',
            '(Multi)Polygon vector data of spatiotemporal fire component'],

           'Unit':

           ['-', 'km^2', 'km', '-'],

           'Valid Range':

           ['>= 0', '>= 0.86 (1 MODIS pixel)', '>= 3.71 (1 MODIS pixel)', '-'],

           'Data Type':

           ['int64', 'float64', 'float64', 'GeometryDtype'],}


# ----------------------------------------------------------------------------
# cpt_poly

cpt_poly = {'Name':

            ['cp', 't', 'area', 'perimeter', 'geometry'],

            'Description':

            ['component membership label', 'days since 2002-01-01',
             'total area burnt', 'perimeter at given day',
             '(Multi)Polygon vector data of spatiotemporal fire component'],

            'Unit':

            ['-', 'days since 2002-01-01', 'km^2', 'km', '-'],

            'Valid Range':

            ['>= 0', '>= 0', '>= 0.86 (1 MODIS pixel)',
             '>= 3.71 (1 MODIS pixel)', '-'],

            'Data Type':

            ['int64', 'int64', 'float64', 'float64', 'GeometryDtype'],}


# ----------------------------------------------------------------------------
# convert
dfs = [v, v_lc, cp, cp_lc, cp_poly, cpt_poly]
names = ['v', 'v_lc', 'cp', 'cp_lc', 'cp_poly', 'cpt_poly']

for df, name in zip(dfs, names):
    convert_to_different_formats(df, name)
