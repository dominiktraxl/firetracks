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
- [Comparison between Active Fire Events Table and MCD14ML](#comparison-between-active-fire-events-table-and-mcd14ml)
- [Comparison between Spatiotemporal Fire Component Table and Global Fire Atlas](#comparison-between-spatiotemporal-fire-component-table-and-global-fire-atlas)


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
  <img width="324" height="200" src="https://github.com/dominiktraxl/firetracks/blob/master/cp_scheme.svg">
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


## Comparison between Active Fire Events Table and MCD14ML

Apart from serving as the basis for the
[Spatiotemporal Fire Component Table](#spatiotemporal-fire-component-table-cph5),
the [Active Fire Events Table](#active-fire-events-table-vh5) can also be used as 
an alternative to the MODIS Global Monthly Fire Location Product 
[MCD14ML](https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/MCD14ML). 
MCD14ML is based on the swath products [MOD14](https://lpdaac.usgs.gov/products/mod14v006/) 
and [MYD14](https://lpdaac.usgs.gov/products/myd14v006/), rather than the tiled 
MOD14A1 and MYD14A1 products, and can be downloaded as tables in plain ASCII 
format. 

For each active fire, MCD14ML contains the geographic location, the exact time
of measurement, the satellite that made the measurement (Aqua or Terra), the
band 21/31 brightness temperatures, the sample number, the fire radiative power,
the detection confidence, a day/night algorithm flag, and an inferred hot spot
type (e.g. active volcano, offshore or presumed vegetation fire).
In comparison, the [Active Fire Events Table](#active-fire-events-table-vh5) does
not contain the exact time (i.e. hour and minute) of the measurement, since it is
based on the daily aggregates MOD14A1 and MYD14A1. The events table also does not contain the
brightness temperatures of fire pixels, the sample number, the day/night
algorithm flag, or the inferred hot spot type. It does however, in addition to
the other columns, contain the `neigh_int`-column, which provides information
as to whether there are any missing/cloud pixels in the neighborhood of a fire
event.

To our surprise, we extract a lot more single pixel fire events from the Level 3
MOD14A1 and MYD14A1 products than MCD14ML does from the Level 2 products MOD14
and MYD14. This is surprising, because the MOD14A1 and MYD14A1 products are
essentially maximum value composites of the MOD14 and MYD14 products. Our events
table should therefore contain strictly less single pixel fire events than
MCD14ML. We extract, however, a total of 145.673.360 single pixel fire events
for the time period from 2003 to 2016, whereas MCD14ML only contains a total of
67.081.995 fire events over the same period, less than half the amount. When we
bin fire events from both tables onto the same regular 0.05° lat/lon
grid with a daily resolution, we find a total of 45.242.414 grid cells
containing fires. The [Active Fire Events Table](#active-fire-events-table-vh5) covers 98.9% of those
burning grid cells, whereas MCD14ML only covers 82.5% of grid cells.
Unfortunately, we are unaware of the reason for this discrepancy. There is no
information in the manuals of the MODIS products that would explain it, and we
did not get a reply from the creators of the MODIS products pertaining to this
discrepancy. 

The figure below depicts the number of single pixel fires by year
for both the [Active Fire Events Table](#active-fire-events-table-vh5) and MCD14ML, as well the percentage of
all fires per year for each respective product. Although the percentage curves
of the events table and MCD14ML follow each other relatively closely, the
discrepancy between the two datasets is reflected in this figure as well,
particularly for the years 2003 and 2004, and the years 2011 and 2012.

<p align="center">
  <img width="506" height="301" src="https://github.com/dominiktraxl/firetracks/blob/master/fire_freq_Y_v_vs_mcd14ml.svg" alt>
  <figcaption align="center"><b><em>Fig. 1</b> Depicted is the absolute number of
  single pixel fire events entailed by FireTracks (FT) and MCD14ML per year (black line with
  circle markers and red line with hexagon markers, respectively). Additionally,
  the proportion (in percent) of all fire events between 2003 and 2016 of FT and
  MCD14ML is illustrated as solid black and red lines, respectively.</em></figcaption>
</p>

Overall, we conclude that our events table entails more than twice as many fires
as MCD14ML, whilst covering nearly all fires that MCD14ML contains.
Additionally, our events table has the advantage that it comes with the
[Active Fire Land Cover Table](#active-fire-land-cover-table-v_lch5), providing
land cover information for each fire.


## Comparison between Spatiotemporal Fire Component Table and Global Fire Atlas

There are only very few global datasets that provide information
on spatiotemporally tracked fire clusters. Two more well known datasets are the
[Global Fire Atlas](https://www.globalfiredata.org/fireatlas.html)
and the
[Global Wildfire Dataset for the Analysis of Fire Regimes and Fire Behaviour](https://doi.org/10.1038/s41597-019-0312-2).
Both of these datasets are derived from the MODIS 500-m Burned Area product
[MCD64A1](https://lpdaac.usgs.gov/products/mcd64a1v006/). To our knowledge, the 
FireTracks Scientific Dataset is the only dataset that uses active fires
to derive spatiotemporally tracked fire clusters.

Apart from using different input data, the algorithms used to identify spatiotemporal 
clusters of fires also differ substantially. The FireTracks Scientific Dataset
uses a very simple and conservative procedure: clusters are identified as the union of nearest 
neighbors of active fires in the discrete spacetime grid given by the spatial 
and temporal resolution of the MOD/MYD14A1 datasets. The Global Fire Atlas and the 
Global Wildfire Dataset, on the other hand, use much more complex algorithms to
detect spatiotemporal clusters.

It is very difficult to assess the quality of any of the aforementioned datasets, 
since ground based observations are scarce. Additional
validation of the fire parameter estimates of the different datasets is still
required. Principally, the quality of the datasets depends strongly on the inherent
limitations of the fire and land-cover data that serve as input. It is therefore highly
recommended to read the respective user guides before using the data. For instance, 
the smallest identifiable fire size is imposed by the spatial resolution of the 
input fire data. For the FireTracks Scientific Dataset this is 0.86 km<sup>2</sup>, 
and for the Global Fire Atlas it is 0.21 km<sup>2</sup>. The Global Fire Atlas is therefore
capable of identifying smaller fires. For both datasets, however, the error of 
the estimated burnt area is expected to grow for smaller fires.

Nevertheless, we can still compare the datasets to each other, and point out some
(dis)advantages of the FireTracks Scientific Dataset over the Global Fire Atlas:

  - Since the Global Fire Atlas is based on MCD64A1, it cannot account for 
    multiple burns within a month on the same pixel. For instance, fires that last multipe 
    days on the same location can therefore not be captured correctly by the Global Fire Atlas.

  - Under relative cloudiness and below overstorey vegetation, the active fires
    used by the FireTracks Scientific Dataset have an advantage, since their detection
    is triggered by temperature anomalies that can sometimes be captured even under
    those circumstances [[1]](#1). Changes in surface reflectance, as utilized by MCD64A1, 
    are more easily obscured.
    
  - Although the same land cover product is used in both datasets (MCD12Q1), the Global Fire
    Atlas uses collection 5.1, whereas the FireTracks Scientific Dataset uses collection 6. 
    This collection includes refinements and new features that cause significant 
    changes in the land-cover classification maps [[2]](#2).

  - The FireTracks Scientific Dataset provides more detailed land-cover information.
    The Global Fire Atlas provides one dominant land cover type for each fire cluster. 
    The details on how this dominant land cover is assigned are not described 
    in the documentation of the Global Fire Atlas. 
    In Addition to the dominant land cover type, the FireTracks Scientific Dataset 
    quantifies the area of each land use type burnt by a fire cluster. Furthermore, we provide the land use 
    type(s) on which the fire ignited. Also, all land cover schemes provided by MCD12Q1 can be readily downloaded, whereas 
    the Global Fire Atlas is only available with the UMD scheme.
    
  - The FireTracks Scientific Dataset is the only dataset that provides integrated fire radiative power for each
    fire cluster (FRP). The FRP can be used to quantify the combusted biomass [[3]](#3) [[4]](#4) [[5]](#5).
    
  - Since the clustering approach of the FireTracks Scientific Dataset is maximally
    conservative (no gaps between neighboring fires are allowed), we expect 
    the distribution of fire sizes to be more skewed towards smaller fires compared
    to the Global Fire Atlas. We do, however, provide information as to whether a fire
    is neighbouring any cloud or missing data pixels.
  
The figure below depicts the absolute frequency distribution of spatiotemporal
fire clusters by year for both the FireTracks Scientific Dataset (FT) and the 
Global Fire Atlas (GFA), as well the percentage of all fire clusters per year 
for each respective product. The number of fire clusters detected by the FT algorithm is 
approximately twice as high as that for the GFA (27.8 x 10<sup>6</sup> versus 
13.3 x 10<sup>6</sup> fire clusters, respectively). Although the percentage curves of FT 
and GFA follow each other to a certain extent, temporal discrepancies are clearly evident.

<p align="center">
  <img width="506" height="301" src="https://github.com/dominiktraxl/firetracks/blob/master/fire_freq_Y_cp_vs_gfa.svg" alt>
  <figcaption align="center"><b><em>Fig. 2</b> Frequency of spatiotemporal fire
  components of FT and GFA. The absolute number of spatiotemporal fire components
  entailed by FT and GFA per year is depicted (black line with circle markers and
  blue line with diamond markers, respectively). Additionally, the proportion
  (in percent) of all fire components between 2003 and 2016 of FT and GFA is
  shown as solid black and blue lines, respectively.</em></figcaption>
</p>

A reason for the difference in the absolute number of fire clusters detected by FT and GFA
can be inferred from the figure below. It shows the burnt area frequency distribution 
of spatiotemporal fire components of FT and GFA. FT is more skewed towards smaller fire sizes. One 
potential reason for this is our conservative clustering approach, leading to 
more fragmented fire clusters. 

<p align="center">
  <img width="506" height="301" src="https://github.com/dominiktraxl/firetracks/blob/master/hist_area.svg" alt>
  <figcaption align="center"><b><em>Fig. 3</b> Burnt area frequency distribution
  of spatiotemporal fire components of FT and GFA. Depicted is the absolute
  frequency distribution of the burnt area (in km<sup>2</sup>) of spatiotemporal fire
  components for FT (black circles) and GFA (blue diamonds).</em></figcaption>
</p>

Using the [powerlaw](https://github.com/jeffalstott/powerlaw) package, we fit a
set of candidate models to the distributions of different
spatiotemporal fire cluster characteristics (area, duration, expansion and FRP). 
These candidates include a log-normal, a stretched exponential, a powerlaw
and a truncated powerlaw. In order to determine the optimal parameters for these models with respect to
the observed distributions of characteristics, the powerlaw package employs maximum likelihood
estimation (MLE) [[6]](#6). To compare the likelihood of each
candidate, evaluated with the respective MLE-optimal parameters, the powerlaw package uses
likelihood-ratio tests [[7]](#7). The results are depicted below.

<p align="center">
  <img width="1012" height="602" src="https://github.com/dominiktraxl/firetracks/blob/master/pdf_models_svg.svg" alt>
  <figcaption align="center"><b><em>Fig. 4</b> Probability density functions for 
  different characteristics of spatiotemporal fire components (FT and GFA). 
  <b>(a)</b> Probability density of observed burnt areas (in km<sup>2</sup>) of 
  spatiotemporal fire components for FT (black circles) and GFA (blue diamonds). 
  A maximum likelihood estimation reveals a powerlaw distribution as the best fit 
  for FT (black solid line), and a stretched exponential distribution as the best distribution for GFA (blue solid line).
  <b>(b)</b> Probability density of observed durations (in days). For FT, there 
  is no clear winner among the tested candidate distributions. For GFA, a truncated 
  powerlaw distribution is the best model describing the distribution. <b>(c)</b> 
  Probability density of observed expansion speeds (in km<sup>2</sup> day<sup>-1</sup>). For FT, 
  a stretched exponential is the best fit, for GFA a truncated powerlaw. <b>(d)</b> 
  Probability density of observed integrated fire radiative power (in MW). Only FT 
  is shown, since GFA does not contain integrated fire radiative power for 
  spatiotemporal components. A log normal distribution is the clear winner among 
  the tested candidate distributions.</em></figcaption>
</p>

## References

<a id="1">[1]</a>
Humber, M. L., Boschetti, L., Giglio, L., & Justice, C. O. (2019). Spatial and 
temporal intercomparison of four global burned area products. International 
journal of digital earth, 12(4), 460-484.

<a id="2">[2]</a>
Sulla-Menashe, D., Gray, J. M., Abercrombie, S. P., & Friedl, M. A. (2019). 
Hierarchical mapping of annual global land cover 2001 to present: The MODIS 
Collection 6 Land Cover product. Remote Sensing of Environment, 222, 183-194.

<a id="3">[3]</a>
Wooster, M. J., Roberts, G., Perry, G. L. W., & Kaufman, Y. J. (2005). Retrieval 
of biomass combustion rates and totals from fire radiative power observations: 
FRP derivation and calibration relationships between biomass consumption and fire 
radiative energy release. Journal of Geophysical Research: Atmospheres, 110(D24).

<a id="4">[4]</a>
Ichoku, C., Giglio, L., Wooster, M. J., & Remer, L. A. (2008). Global 
characterization of biomass-burning patterns using satellite measurements of fire 
radiative energy. Remote sensing of Environment, 112(6), 2950-2962.

<a id="5">[5]</a>
Kumar, S. S., Roy, D. P., Boschetti, L., & Kremens, R. (2011). Exploiting the 
power law distribution properties of satellite fire radiative power retrievals: 
A method to estimate fire radiative energy and biomass burned from sparse 
satellite observations. Journal of Geophysical Research: Atmospheres, 116(D19).

<a id="6">[6]</a>
Clauset, A., Shalizi, C. R., & Newman, M. E. (2009). Power-law distributions in 
empirical data. SIAM review, 51(4), 661-703.

<a id="7">[7]</a>
Neyman, J., & Pearson, E. S. (1933). IX. On the problem of the most efficient 
tests of statistical hypotheses. Philosophical Transactions of the Royal Society 
of London. Series A, Containing Papers of a Mathematical or Physical Character, 
231(694-706), 289-337.
