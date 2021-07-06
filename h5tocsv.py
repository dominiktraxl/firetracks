"""
==============================================================================

Command line interface to convert FireTracks HDF5 files into CSV files.

==============================================================================


Works with all HDF5 files of the FireTracks Scientific Dataset
(see https://github.com/dominiktraxl/firetracks):

'v.h5',
'cp.h5',

'v_LC_Type1.h5',
'v_LC_Type2.h5',
'v_LC_Type3.h5',
'v_LC_Type4.h5',
'v_LC_Type5.h5',
'v_LC_Prop1.h5',
'v_LC_Prop2.h5',
'v_LC_Prop3.h5',
'v_LC_Prop1_Assessment.h5',
'v_LC_Prop2_Assessment.h5',
'v_LC_Prop3_Assessment.h5',
'v_QC.h5',
'v_LW.h5',

'cp_LC_Type1.h5',
'cp_LC_Type2.h5',
'cp_LC_Type3.h5',
'cp_LC_Type4.h5',
'cp_LC_Type5.h5',
'cp_LC_Prop1.h5',
'cp_LC_Prop2.h5',
'cp_LC_Prop3.h5',
'cp_QC.h5',
'cp_LW.h5',

==============================================================================
"""

# Copyright (C) 2021 by
# Dominik Traxl <dominik.traxl@posteo.org>
# All rights reserved.
# MIT license.


import argparse

import pandas as pd

# argument parameters
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument(
    'input_file_name',
    metavar='input-file-name',
    help="the input file to convert into csv "
         "(including the file ending '.h5')",
    type=str,
)
parser.add_argument(
    'output_file_name',
    metavar='output-file-name',
    help="the output file. "
         "Detects compression mode from the following file extensions: '.gz', "
         "'.bz2', '.zip' or '.xz' (otherwise no compression)",
    type=str,
)
parser.add_argument(
    '-f', '--from-time',
    help="select only rows from the given time (default: %(default)s)",
    type=str,
    default='2002-01-01',
    required=False,
)
parser.add_argument(
    '-t', '--to-time',
    help="select only rows until the given time (excluded) (default: %(default)s)",
    type=str,
    default='2021-01-01',
    required=False,
)
parser.add_argument(
    '-c', '--columns',
    nargs='+',
    help="list of columns to include in the csv output file. "
         "Column names and their descriptions can be found here: "
         "https://github.com/dominiktraxl/firetracks",
    required=False)
args = parser.parse_args()

# event or component table?
if args.input_file_name.startswith('v'):
    dtcol = 'dtime'
elif args.input_file_name.startswith('cp'):
    dtcol = 'dtime_min'

# load .h5 file
df = pd.read_hdf(
    args.input_file_name,
    where=f'{dtcol} >= "{args.from_time}" & {dtcol} < "{args.to_time}"',
    columns=args.columns,
)

# store as csv
df.to_csv(args.output_file_name)
