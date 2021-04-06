
# Copyright (C) 2020 by
# Dominik Traxl <dominik.traxl@posteo.org>
# All rights reserved.
# MIT license.

# to keep track of memory consumption:
# install memory_profiler, e.g. via
# $ conda install memory_profiler
# and run
# $ mprof run --include-children test_firetracks.py
# $ mprof plot

import subprocess

# scripts to run
cmds = [
    ['python', 'create_data_description_tables.py'],

    ['python', '01_create_fire_event_table.py'],

    ['python', '02_create_land_cover_table.py', 'LC_Type1'],
    ['python', '02_create_land_cover_table.py', 'LC_Type2'],
    ['python', '02_create_land_cover_table.py', 'LC_Type3'],
    ['python', '02_create_land_cover_table.py', 'LC_Type4'],
    ['python', '02_create_land_cover_table.py', 'LC_Type5'],
    ['python', '02_create_land_cover_table.py', 'LC_Prop1'],
    ['python', '02_create_land_cover_table.py', 'LC_Prop2'],
    ['python', '02_create_land_cover_table.py', 'LC_Prop3'],
    ['python', '02_create_land_cover_table.py', 'LC_Prop1_Assessment'],
    ['python', '02_create_land_cover_table.py', 'LC_Prop2_Assessment'],
    ['python', '02_create_land_cover_table.py', 'LC_Prop3_Assessment'],
    ['python', '02_create_land_cover_table.py', 'QC'],
    ['python', '02_create_land_cover_table.py', 'LW'],

    ['python', '03_connect_neighboring_fire_events.py'],
    ['python', '04_find_connected_fire_events.py'],
    ['python', '05_create_fire_component_table.py'],

    ['python', '06_create_component_land_cover_table.py', 'LC_Type1'],
    ['python', '06_create_component_land_cover_table.py', 'LC_Type2'],
    ['python', '06_create_component_land_cover_table.py', 'LC_Type3'],
    ['python', '06_create_component_land_cover_table.py', 'LC_Type4'],
    ['python', '06_create_component_land_cover_table.py', 'LC_Type5'],
    ['python', '06_create_component_land_cover_table.py', 'LC_Prop1'],
    ['python', '06_create_component_land_cover_table.py', 'LC_Prop2'],
    ['python', '06_create_component_land_cover_table.py', 'LC_Prop3'],
    ['python', '06_create_component_land_cover_table.py', 'QC'],
    ['python', '06_create_component_land_cover_table.py', 'LW'],

    ['python', '07_create_component_polygons.py'],
    ['python', '07_create_component_polygons.py', '-s'],
]


def main():
    for cmd in cmds:
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
