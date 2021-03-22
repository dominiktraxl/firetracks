# FireTracks Scientific Dataset

## About

This is a collection of python scripts that produces the
[FireTracks Scientific Dataset](https://add.data.link). The dataset is
based on the MODIS Fire Products MOD14A1/MYD14A1 and the MODIS Land Cover
Product MCD12Q1. It entails HDF5-tables/GeoPackages of active fire events,
spatiotemporal components of fire events and associated land cover information.

See [Data Content](#data-content) for further details.

## Installation

No installation is required.

However, to run the python scripts the following packages are required:

- pyhdf
- numpy
- scipy
- pandas
- tables
- deepgraph
- geopandas
- shapely

You can use [conda](https://docs.conda.io/en/latest/) to set up an environment
and install all dependencies via

```console
$ conda create -n FT
$ conda activate FT
$ conda install -c conda-forge pyhdf numpy scipy pandas pytables deepgraph geopandas shapely
```

## Getting Original Data

To create the FireTracks Scientific Dataset, you need to first download the
original data that it is based on: MOD14A1, MYD14A1 and MCD12Q1.

You can download the data here: https://search.earthdata.nasa.gov/search

Search for the products (MOD14A1, MYD14A1 and MCD12Q1), select the spatial and
temporal domain you're interested in, and then download the data either via
direct download or an access script.

The data must be stored in their respective folders (MOD14A1, MYD14A1, MCD12Q1)
in the same directory as the python scripts. There should be no subdirectories
within the data folders.

Note: to associate land cover information with fire events, you need to
download the MCD12Q1 files from one year *before* the actual occurrence of the
fire events.


## Creating the FireTracks Scientific Dataset

1. Download the python scripts contained in this repository

2. Store the python scripts in the directory that contains the folders with the
downloaded original data (MOD14A1, MYD14A1, MCD12Q1)

3. `cd` into the directory containing the scripts and the downloaded original
data folders, then run the scripts in the indicated order:

        $ python 01_create_fire_event_table.py
        ...
        $ python 07_create_component_polygons.py

Note: some scripts have positional and/or optional arguments. Use

```console
$ python *script*.py -h
```

for more information.


## Loading the FireTracks Scientific Dataset Using Python

Using Python Pandas/GeoPandas, you can load the HDF5/GeoPackage Data via the
following commands:

```python
import os

import pandas as pd
import geopandas as gpd

# active fire events table
v = pd.read_hdf('v.h5', 'v')

# add component membership labels to v
v['cp'] = pd.read_hdf('v.h5', 'v_cp')

# active fire land cover table
v_lc = pd.read_hdf('v_LC_Type1.h5')

# spatiotemporal fire component table
cp = pd.read_hdf('cp.h5')

# spatiotemporal fire component land cover table
cp_lc = pd.read_hdf('cp_LC_Type1.h5')

# spatiotemporal fire component shapefile
cp_poly = gpd.read_file(os.path.join(os.getcwd(), 'cp_poly.gpkg'))

# spatiotemporal fire component shapefile per time-slice
cpt_poly = gpd.read_file(os.path.join(os.getcwd(), 'cpt_poly.gpkg'))

```

Note: `v.h5` is sorted and indexed by `dtime`, allowing for fast queries by
time, e.g.:

```python
v_2015 = pd.read_hdf('v.h5', 'v', where='dtime >= "2015-01-01" & dtime < "2016-01-01"')
```

## Data Content

### Active Fire Events Table `v.h5`

The active fire events table is a combination of the MODIS products MOD14A1 and
MYD14A1. Fire events from the fire masks of both products are extracted and stored in
table format. For fires measured by both satellites, the maximum value of the
individual `maxFRP` values is stored. Furthermore, for each fire, the minimum
of the fire pixel classes of all 26 neighboring grid cells (3\*3\*3
[lat\*lon\*time] grid cell box with the fire event in the center) is recorded.
Possible fire pixel classes are as follows (note that class 3 and 4 are swapped
compared to the original fire pixel classes):

| Class | Meaning                                                |
|:------|:-------------------------------------------------------|
| 0     | not processed (missing input data)                     |
| 1     | not processed (obsolete; not used since Collection 1)  |
| 2     | not processed (other reason)                           |
| 3     | cloud (land or water)                                  |
| 4     | non-fire water pixel                                   |
| 5     | non-fire land pixel                                    |
| 6     | unknown (land or water)                                |
| 7     | fire (low confidence, land or water)                   |
| 8     | fire (nominal confidence, land or water)               |
| 9     | fire (high confidence, land or water)                  |

This minimum value (`neigh_int`) allows us to see if there are any
missing/cloud pixels in the neighborhood of a fire event.

| Name      | Description                                                  | Unit                  | Valid Range                        | Data Type   |
|:----------|:-------------------------------------------------------------|:----------------------|:-----------------------------------|:------------|
| lat       | location latitude                                            | degress               | [-180, 180]                        | float64     |
| lon       | location longitude                                           | degrees               | [-90, 90]                          | float64     |
| x         | x-coordinate on global sinusoidal MODIS grid                 | -                     | [0, 36&ast;1200-1]                 | uint16      |
| y         | y-coordinate on global sinusoidal MODIS grid                 | -                     | [0, 18&ast;1200-1]                 | uint16      |
| H         | horizontal MODIS tile coordinate                             | -                     | [0, 35]                            | uint8       |
| V         | vertical MODIS tile coordinate                               | -                     | [0, 17]                            | uint8       |
| i         | row coordinate of the grid cell within MODIS tile (H, V)     | -                     | [0, 1199]                          | uint16      |
| j         | column coordinate of the grid cell within MODIS tile (H, V)  | -                     | [0, 1199]                          | uint16      |
| dtime     | date (YYYY-MM-DD)                                            | -                     | >= 2002-01-01                      | datetime64  |
| conf      | detection confidence [7: low, 8: nominal, 9: high]           | -                     | [7, 9]                             | uint8       |
| maxFRP    | maximum fire radiative power                                 | MW&ast;10             | >= 0                               | int32       |
| satellite | which satellite detected the fire [MOD, MYD, both]           | -                     | -                                  | string      |
| neigh     | string representation of "neigh_int"                         | -                     | -                                  | string      |
| t         | days since 2002-01-01                                        | days since 2002-01-01 | >= 0                               | uint16      |
| country   | country of occurrence                                        | -                     | -                                  | string      |
| continent | continent of occurrence                                      | -                     | -                                  | string      |
| neigh_int | minimum of fire pixel classes of neighboring grid cells      | -                     | [0, 9]                             | uint8       |
| gl        | location ID on the global sinusoidal MODIS grid              | -                     | [0, 36&ast;1200&ast;18&ast;1200-1] | uint32      |
| cp        | component membership label                                   | -                     | >= 0                               | int64       |


### Active Fire Land Cover Table `v_*lc*.h5`

The active fire land cover table is based on the MODIS product MCD12Q1 and
provides land cover information for each fire event of the active fire events
table. Since the resolution of MCD12Q1 is twice as high as that of
MOD14A1/MYD14A1, each fire event is associated with 4 subpixel land cover type
values.

Note: Land cover values are extracted from MCD12Q1 for the year *before* the
fire event.

| Name   | Description                               | Unit   | Valid Range   | Data Type   |
|:-------|:------------------------------------------|:-------|:--------------|:------------|
| lc1    | land cover type of subpixel 1 (numerical) | -      | [0, 255]      | uint8       |
| lc2    | land cover type of subpixel 2 (numerical) | -      | [0, 255]      | uint8       |
| lc3    | land cover type of subpixel 3 (numerical) | -      | [0, 255]      | uint8       |
| lc4    | land cover type of subpixel 4 (numerical) | -      | [0, 255]      | uint8       |


### Spatiotemporal Fire Component Table `cp.h5`

The spatiotemporal fire component table provides summarizing characteristics
of spatiotemporally tracked fire components.

A component is defined as a coherent set of grid cells, all of which have the same
state. Cells are coherent if they can reach each other via nearest neighbor
relations. In most cases, the von Neumann neighborhood (four adjacent cells)
is considered.

| Name          | Description                                            | Unit                  | Valid Range             | Data Type   |
|:--------------|:-------------------------------------------------------|:----------------------|:------------------------|:------------|
| n_nodes       | number of constituent fire events                      | -                     | >= 1                    | int64       |
| t_min         | ignition date (days since 2002-01-01)                  | days since 2002-01-01 | >= 0                    | uint16      |
| t_max         | extinction date (days since 2002-01-01)                | days since 2002-01-01 | >= 0                    | uint16      |
| dtime_min     | ignition date (YYYY-MM-DD)                             | -                     | >= 2002-01-01           | datetime64  |
| dtime_max     | extinction date (YYYY-MM-DD)                           | -                     | >= 2002-01-01           | datetime64  |
| lat_mean      | mean location latitude                                 | degrees               | [-180, 180]             | float64     |
| lon_mean      | mean location longitude                                | degrees               | [-90, 90]               | float64     |
| maxFRP_mean   | mean maximum fire radiative power                      | MW&ast;10             | >= 0                    | float64     |
| neigh_int_min | minimum of constituent fire event´s "neigh_int" values | -                     | [0, 9]                  | uint8       |
| neigh_min     | string representation of "neigh_int_min"               | -                     | -                       | string      |
| duration      | fire duration                                          | days                  | >= 1                    | uint16      |
| unique_gls    | number of grid locations burnt                         | -                     | >= 1                    | uint32      |
| area          | total area burnt                                       | km^2                  | >= 0.86 (1 MODIS pixel) | float64     |
| expansion     | average daily fire expansion                           | km^2 day^-1           | > 0                     | float64     |
| country       | country of occurrence                                  | -                     | -                       | string      |
| continent     | continent of occurrence                                | -                     | -                       | string      |


### Spatiotemporal Fire Component Land Cover Table `cp_*lc*.h5`

The spatiotemporal fire component land cover table provides land cover
information for each spatiotemporal fire component.

| Name   | Description                                             | Unit   | Valid Range   | Data Type   |
|:-------|:--------------------------------------------------------|:-------|:--------------|:------------|
| dlc    | dominant land cover type&ast;                           | -      | -             | string      |
| lc_X   | number of subpixels burnt belonging to land cover X     | -      | >= 0          | int64       |
| plc_X  | proportion of subpixels burnt belonging to land cover X | -      | [0, 1]        | float64     |
| flc_X  | number of ignition subpixels belonging to land cover X  | -      | >= 0          | int64       |

*a spatiotemporal fire component has a dominant land cover type X, if at least
80% of burnt subpixels belong to land cover X. Otherwise, `dlc` is set to
"None".


### Spatiotemporal Fire Component GeoPackage `cp_poly.gpkg`

The spatiotemporal fire component geopackage provides polygon vector data for
each spatiotemporal fire component.

| Name      | Description                                                 | Unit   | Valid Range             | Data Type     |
|:----------|:------------------------------------------------------------|:-------|:------------------------|:--------------|
| cp        | component membership label                                  | -      | >= 0                    | int64         |
| area      | total area burnt                                            | km^2   | >= 0.86 (1 MODIS pixel) | float64       |
| perimeter | final perimeter                                             | km     | >= 3.71 (1 MODIS pixel) | float64       |
| geometry  | (Multi)Polygon vector data of spatiotemporal fire component | -      | -                       | GeometryDtype |


### Spatiotemporal Fire Component (Per Time-Slice) GeoPackage `cpt_poly.gpkg`

The spatiotemporal fire component geopackage provides polygon vector data for
each time-slice of every spatiotemporal fire component.

| Name      | Description                                                 | Unit                  | Valid Range             | Data Type     |
|:----------|:------------------------------------------------------------|:----------------------|:------------------------|:--------------|
| cp        | component membership label                                  | -                     | >= 0                    | int64         |
| t         | days since 2002-01-01                                       | days since 2002-01-01 | >= 0                    | int64         |
| area      | total area burnt                                            | km^2                  | >= 0.86 (1 MODIS pixel) | float64       |
| perimeter | perimeter at given day                                      | km                    | >= 3.71 (1 MODIS pixel) | float64       |
| geometry  | (Multi)Polygon vector data of spatiotemporal fire component | -                     | -                       | GeometryDtype |
