
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
    ['python', '03_connect_neighboring_fire_events.py'],
    ['python', '04_find_connected_fire_events.py'],
    ['python', '05_create_fire_component_table.py'],
    ['python', '06_create_component_land_cover_table.py', 'LC_Type1'],
    ['python', '07_create_component_polygons.py'],
    ['python', '07_create_component_polygons.py', '-s'],
]


def main():
    for cmd in cmds:
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
