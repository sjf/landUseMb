#!/usr/bin/env python3
import os
from data.geojson import *
from data.csv import to_int, to_float
from data.log import *
import sys
from data.utils import *

FILE = get_arg(1, 'SF_Land_Use.geojson')
PREFIX = os.path.splitext(FILE)[0]
GEOJSON_OUT = PREFIX + '_out.geojson'
SHAPE_FILE = PREFIX + '_out.shp'

# Source https://data.sfgov.org/Housing-and-Buildings/Land-Use/us3s-fp9q
log("Reading geojson")
geojson = read_geojson(FILE)
converters =  {'resunits': to_int,
               'bldgsqft':  to_int,
               'yrbuilt':  to_int,
               'total_uses': to_int,
               'yrbuilt':  to_int,
               'shape_area': to_float,
               }
convert_properties(geojson, converters)
log("Writing geojson")
write_geojson(geojson, GEOJSON_OUT)

run('ogr2ogr -overwrite -progress ' + SHAPE_FILE + ' ' + GEOJSON_OUT)
run('pyshp2pgsql ' + SHAPE_FILE + ' ' + PREFIX)


