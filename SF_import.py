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

def run_or_fail(cmd):
  class Runner:
    def run(self, cmd):
      log('Running', cmd)
      res = os.system(cmd)
      if res != 0:
        sys.exit(res)
      return self
    def exit(self):
      sys.exit()
  return Runner().run(cmd)

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

run_or_fail('ogr2ogr -overwrite -progress ' + SHAPE_FILE + ' ' + GEOJSON_OUT) \
  .run('pyshp2pgsql ' + SHAPE_FILE + ' ' + PREFIX) \
  .exit()

#os.system('tippecanoe --force -o SF_Land_Use.mbtiles SF_Land_Use_out.geojson')