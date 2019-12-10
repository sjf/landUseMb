#!/usr/bin/env python3
from data.utils import *

TABLE = get_arg(1, 'sf_head_2')
#SHP = TABLE + '.shp'
INTERIM = TABLE + '.geojson'
MBTILES = get_arg(2, TABLE + '.mbtiles')

run(f'/usr/local/Cellar/gdal/2.4.2_3/bin/ogr2ogr -f GeoJSON {INTERIM} "PG:dbname=sjf" -sql "select * from {TABLE}"')
#run('pgsql2shp -f %s sjf "SELECT * from %s"' % (INTERM, TABLE))
run(f'tippecanoe --force -o {MBTILES} {INTERIM}')