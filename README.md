[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5075988.svg)](https://doi.org/10.5281/zenodo.5075988)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4461575.svg)](https://doi.org/10.5281/zenodo.4461575)

# The FireTracks Scientific Dataset

![](cp_time_evolution.gif)


## Content

- [About](#about)
- [Overview](#overview)
- [Installation](#installation)
- [Getting Orginal Data](#getting-original-data)
- [Creating the FireTracks Scientific Dataset](#creating-the-firetracks-scientific-dataset)
- [Loading the FireTracks Scientific Dataset Using Python](#loading-the-firetracks-scientific-dataset-using-python)
- [Converting HDF5 files to CSV files (CLI)](#converting-hdf5-files-to-csv-files-cli)
- [Data Content](#data-content)
  - [Active Fire Events Table](#active-fire-events-table-vh5)
  - [Active Fire Land Cover Table](#active-fire-land-cover-table-v_lch5)
  - [Spatiotemporal Fire Component Table](#spatiotemporal-fire-component-table-cph5)
  - [Spatiotemporal Fire Component Land Cover Table](#spatiotemporal-fire-component-land-cover-table-cp_lch5)
  - [Spatiotemporal Fire Component GeoPackage](#spatiotemporal-fire-component-geopackage-cp_polygpkg)
  - [Spatiotemporal Fire Component (Per Time-Slice) GeoPackage](#spatiotemporal-fire-component-per-time-slice-geopackage-cpt_polygpkg)


## About

This is a collection of python scripts that produces the
[FireTracks Scientific Dataset](https://doi.org/10.5281/zenodo.4461575). The dataset is based on
the MODIS Fire Products
[MOD14A1](https://lpdaac.usgs.gov/products/mod14a1v006/)/
[MYD14A1](https://lpdaac.usgs.gov/products/myd14a1v006/) and the MODIS Land
Cover Product [MCD12Q1](https://lpdaac.usgs.gov/products/mcd12q1v006/). It
entails HDF5-tables/GeoPackages of active fire events, spatiotemporal
components of fire events and associated land cover information.

Note: the quality of the FireTracks Scientific Dataset depends entirely on the
underlying MOD14A1/MYD14A1/MCD12Q1 datasets, and it is strongly recommended to
read the respective user guides before using the data:

- [MOD14A1 User Guide](https://lpdaac.usgs.gov/documents/876/MOD14_User_Guide_v6.pdf)
- [MYD14A1 User Guide](https://lpdaac.usgs.gov/documents/876/MOD14_User_Guide_v6.pdf)
- [MCD12Q1 User Guide](https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf)

Download: the FireTracks Scientific Dataset, processed for the years 2002-2020,
can be downloaded here: https://doi.org/10.5281/zenodo.4461575


## Overview

The FireTracks Scientific Dataset is derived from the Aqua and Terra Moderate
Resolution Imaging Spectroradiometer (MODIS) Collection 6 (C6) Thermal
Anomalies and Fire Data (MOD14A1 and MYD14A1). These satellite products include
1-km gridded fire masks over daily (24-hour) compositing periods on a global scale,
from the year 2000 to the present.

Part of the FireTracks Scientific Dataset is the
[Active Fire Events Table](#active-fire-events-table-vh5), which contains single
pixel fire events in table format extracted from the fire masks of both satellite
products. The [Active Fire Land Cover Table](#active-fire-land-cover-table-v_lch5)
provides land cover information for each fire event of the active fire events
table, derived from the MODIS product MCD12Q1.

The centerpiece of the FireTracks Scientific Dataset is the
[Spatiotemporal Fire Component Table](#spatiotemporal-fire-component-table-cph5),
providing summarizing characteristics of spatiotemporally tracked fire components.
It is derived from the active fire events table by performing a spatiotemporal
clustering of the single pixel fire events. A spatiotemporal cluster is
identified as the union of nearest neighbors of fire events in the discrete
space-time grid prescribed by the resolution of the MODIS fire masks (temporal
resolution: 1 day, spatial resolution: 1 km). We consider a 3d-Moore
neighborhood for the clustering (26 adjacent cells, 3\*3\*3 [x\*y\*time] grid
cell box with the fire event in the center). Below, you see an example of a
spatiotemporal fire component comprised of 5 single pixel fire events, evolving
over 4 consecutive days. At the top of this webpage, you see the temporal
evolution of one of the largest spatiotemporal fire components found in the
data. It was recorded in the summer of 2018 in California, lasting 48 days and
burning a total of 1893 km^2 with an integrated radiative power of 1.614.436 MW.

<p align="center">
  <img width="324" height="200" src="https://github.com/dominiktraxl/firetracks/blob/main/cp_scheme.svg">
</p>

The active fire events table and the spatiotemporal fire component table are
linked to each other via the `cp` column of the events table
(the component membership label) and the `cp` column of the component table
(the component index).

Land cover information for each spatiotemporal fire component is summarized in the
[Spatiotemporal Fire Component Land Cover Table](#spatiotemporal-fire-component-land-cover-table-cp_lch5).

Additionally, the FireTracks Scientific Dataset provides polygon vector data for
each spatiotemporal fire component ([Spatiotemporal Fire Component GeoPackage](#spatiotemporal-fire-component-geopackage-cp_polygpkg)),
as well as for each time-slice of every spatiotemporal fire component
([Spatiotemporal Fire Component (Per Time-Slice) GeoPackage](#spatiotemporal-fire-component-per-time-slice-geopackage-cpt_polygpkg)).

For further details of the provided HDF5-tables/GeoPackages, see [Data Content](#data-content).

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
temporal domain you're interested in, and then download the data.

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
v = pd.read_hdf('v.h5')

# active fire land cover table
v_lc = pd.read_hdf('v_LC_Type1.h5')

# spatiotemporal fire component table
cp = pd.read_hdf('cp.h5')

# spatiotemporal fire component land cover table
cp_lc = pd.read_hdf('cp_LC_Type1.h5')

# spatiotemporal fire component shapefile
cp_poly = gpd.read_file('cp_poly.gpkg')

# spatiotemporal fire component shapefile per time-slice
cpt_poly = gpd.read_file('cpt_poly.gpkg')

```

Note:

- `v.h5` and `v_*lc*.h5` are sorted and indexed by `dtime`, allowing for fast
queries by time, e.g.:

    ```python
    v_2019 = pd.read_hdf('v.h5', where='dtime >= "2019-01-01" & dtime < "2020-01-01"')
    v_lc_2019 = pd.read_hdf('v_LC_Type1.h5', where='dtime >= "2019-01-01" & dtime < "2020-01-01"')
    ```

- `cp.h5` and `cp_*lc*.h5` are sorted and indexed by `dtime_min`, allowing for
fast queries by time, e.g.:

    ```python
    cp_2019 = pd.read_hdf('cp.h5', where='dtime_min >= "2019-01-01" & dtime_min < "2020-01-01"')
    cp_lc_2019 = pd.read_hdf('cp_LC_Type1.h5', where='dtime_min >= "2019-01-01" & dtime_min < "2020-01-01"')
    ```

- to load specific rows of `cp_poly.gpkg` or `cpt_poly.gpkg` using geopandas,
you can pass an `int` or `slice` object as argument `rows` to the `gpd.read_file` method,
e.g.:

    ```python
    cp_poly_selection = gpd.read_file('cp_poly.gpkg', rows=5)
    cpt_poly_selection = gpd.read_file('cpt_poly.gpkg', rows=slice(10, 20))
    ```


## Converting HDF5 files to CSV files (CLI)

The `h5tocsv.py` file contained in this repository allows you to convert
the HDF5 files of the FireTracks Scientific Dataset into CSV files using
the command line. Via optional arguments, it is possible to subset the original
data by time and/or columns before the conversion to CSV.

To run the conversion CLI, the following packages are required:

- pandas
- tables

You can use [conda](https://docs.conda.io/en/latest/) to set up an environment
and install all dependencies via

```console
$ conda create -n FTC
$ conda activate FTC
$ conda install -c conda-forge pandas pytables
```

To show the documentation of the CLI, type
```console
$ python h5tocsv.py -h
```
This will show the help message of `h5tocsv.py` and exit.

The following example converts `cp.h5` into `cp.csv`, including only components
with ignition dates between `2003-01-01` and `2003-07-01` (excluded). Only the
columns `cp`, `maxFRP_sum`, `duration`, `area` and `country` are included in the CSV file.
```console
$ python h5tocsv.py cp.h5 cp.csv --from-time 2003-01-01 --to-time 2003-07-01 --columns cp maxFRP_sum duration area country
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

| Name      | Description                                                 | Unit                  | Valid Range                        | Data Type   |
|:----------|:------------------------------------------------------------|:----------------------|:-----------------------------------|:------------|
| lat       | location latitude                                           | degress               | [-180, 180]                        | float64     |
| lon       | location longitude                                          | degrees               | [-90, 90]                          | float64     |
| x         | x-coordinate on global sinusoidal MODIS grid                | -                     | [0, 36&ast;1200-1]                 | uint16      |
| y         | y-coordinate on global sinusoidal MODIS grid                | -                     | [0, 18&ast;1200-1]                 | uint16      |
| H         | horizontal MODIS tile coordinate                            | -                     | [0, 35]                            | uint8       |
| V         | vertical MODIS tile coordinate                              | -                     | [0, 17]                            | uint8       |
| i         | row coordinate of the grid cell within MODIS tile (H, V)    | -                     | [0, 1199]                          | uint16      |
| j         | column coordinate of the grid cell within MODIS tile (H, V) | -                     | [0, 1199]                          | uint16      |
| dtime     | date (YYYY-MM-DD)                                           | -                     | >= 2002-01-01                      | datetime64  |
| conf      | detection confidence [7: low, 8: nominal, 9: high]          | -                     | [7, 9]                             | uint8       |
| maxFRP    | maximum fire radiative power                                | MW&ast;10             | >= 0                               | int32       |
| satellite | which satellite detected the fire [MOD, MYD, both]          | -                     | -                                  | string      |
| neigh     | string representation of "neigh_int"                        | -                     | -                                  | string      |
| t         | days since 2002-01-01                                       | days since 2002-01-01 | >= 0                               | uint16      |
| country   | country of occurrence                                       | -                     | -                                  | string      |
| continent | continent of occurrence                                     | -                     | -                                  | string      |
| neigh_int | minimum of fire pixel classes of neighboring grid cells     | -                     | [0, 9]                             | uint8       |
| gl        | location ID on the global sinusoidal MODIS grid             | -                     | [0, 36&ast;1200&ast;18&ast;1200-1] | uint32      |
| cp        | component membership label                                  | -                     | >= 0                               | int64       |


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
| dtime  | date (YYYY-MM-DD)                         | -      | >= 2002-01-01 | datetime64  |


### Spatiotemporal Fire Component Table `cp.h5`

The spatiotemporal fire component table provides summarizing characteristics
of spatiotemporally tracked fire components.

A fire component is defined as a coherent set of grid cells on fire. Cells are
coherent if they can reach each other via nearest neighbor relations considering
a 3d-Moore neighborhood (26 adjacent cells, 3\*3\*3 [lat\*lon\*time] grid cell
box with the fire event in the center).

| Name          | Description                                              | Unit                  | Valid Range             | Data Type   |
|:--------------|:---------------------------------------------------------|:----------------------|:------------------------|:------------|
| cp            | component index                                          | -                     | >= 0                    | int64       |
| n_nodes       | number of constituent fire events                        | -                     | >= 1                    | int64       |
| t_min         | ignition date (days since 2002-01-01)                    | days since 2002-01-01 | >= 0                    | uint16      |
| t_max         | extinction date (days since 2002-01-01)                  | days since 2002-01-01 | >= 0                    | uint16      |
| dtime_min     | ignition date (YYYY-MM-DD)                               | -                     | >= 2002-01-01           | datetime64  |
| dtime_max     | extinction date (YYYY-MM-DD)                             | -                     | >= 2002-01-01           | datetime64  |
| lat_mean      | mean location latitude                                   | degrees               | [-180, 180]             | float64     |
| lon_mean      | mean location longitude                                  | degrees               | [-90, 90]               | float64     |
| maxFRP_mean   | mean maximum fire radiative power                        | MW&ast;10             | >= 0                    | float64     |
| maxFRP_sum    | sum of maximum fire radiative powers                     | MW&ast;10             | >= 0                    | float64     |
| neigh_int_min | minimum of "neigh_int" values of constituent fire events | -                     | [0, 9]                  | uint8       |
| neigh_min     | string representation of "neigh_int_min"                 | -                     | -                       | string      |
| duration      | fire duration                                            | days                  | >= 1                    | uint16      |
| unique_gls    | number of grid locations burnt                           | -                     | >= 1                    | uint32      |
| area          | total area burnt                                         | km^2                  | >= 0.86 (1 MODIS pixel) | float64     |
| expansion     | average daily fire expansion                             | km^2 day^-1           | > 0                     | float64     |
| country       | country of occurrence                                    | -                     | -                       | string      |
| continent     | continent of occurrence                                  | -                     | -                       | string      |


### Spatiotemporal Fire Component Land Cover Table `cp_*lc*.h5`

The spatiotemporal fire component land cover table provides land cover
information for each spatiotemporal fire component.

| Name      | Description                                             | Unit   | Valid Range   | Data Type   |
|:----------|:--------------------------------------------------------|:-------|:--------------|:------------|
| cp        | component index                                         | -      | >= 0          | int64       |
| dlc       | dominant land cover type&ast;                           | -      | -             | string      |
| lc_X      | number of subpixels burnt belonging to land cover X     | -      | >= 0          | int64       |
| plc_X     | proportion of subpixels burnt belonging to land cover X | -      | [0, 1]        | float64     |
| flc_X     | number of ignition subpixels belonging to land cover X  | -      | >= 0          | int64       |
| dtime_min | ignition date (YYYY-MM-DD)                              | -      | >= 2002-01-01 | datetime64  |

*a spatiotemporal fire component has a dominant land cover type X, if at least
80% of burnt subpixels belong to land cover X. Otherwise, `dlc` is set to
"None".


### Spatiotemporal Fire Component GeoPackage `cp_poly.gpkg`

The spatiotemporal fire component geopackage provides polygon vector data for
each spatiotemporal fire component.

| Name      | Description                                                 | Unit   | Valid Range             | Data Type     |
|:----------|:------------------------------------------------------------|:-------|:------------------------|:--------------|
| cp        | component index                                             | -      | >= 0                    | int64         |
| area      | total area burnt                                            | km^2   | >= 0.86 (1 MODIS pixel) | float64       |
| perimeter | final perimeter                                             | km     | >= 3.71 (1 MODIS pixel) | float64       |
| geometry  | (Multi)Polygon vector data of spatiotemporal fire component | -      | -                       | GeometryDtype |


### Spatiotemporal Fire Component (Per Time-Slice) GeoPackage `cpt_poly.gpkg`

The spatiotemporal fire component geopackage provides polygon vector data for
each time-slice of every spatiotemporal fire component.

| Name      | Description                                                 | Unit                  | Valid Range             | Data Type     |
|:----------|:------------------------------------------------------------|:----------------------|:------------------------|:--------------|
| cp        | component index                                             | -                     | >= 0                    | int64         |
| t         | days since 2002-01-01                                       | days since 2002-01-01 | >= 0                    | int64         |
| area      | total area burnt                                            | km^2                  | >= 0.86 (1 MODIS pixel) | float64       |
| perimeter | perimeter at given day                                      | km                    | >= 3.71 (1 MODIS pixel) | float64       |
| geometry  | (Multi)Polygon vector data of spatiotemporal fire component | -                     | -                       | GeometryDtype |
