#!/usr/bin/env python3
import psycopg2
from psycopg2.extensions import AsIs
from psycopg2.extras import LoggingConnection
from postgis.psycopg import register
from data.unionfind import UnionFind
from data.utils import *
from data.log import *
import logging

TABLE = get_arg(1, 'sf_head')
NEXT_LEVEL = TABLE + '_2'
BUFFER = 0.000001
SRID = 4326
params = {'table': AsIs(TABLE),
          'next_level': AsIs(NEXT_LEVEL),
          'buffer': BUFFER,
          'SRID': SRID}

log('Building layers from', TABLE)

uf = UnionFind()

db = psycopg2.connect(dbname="sjf",connection_factory=LoggingConnection)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
db.initialize(logger)
register(db)
cursor = db.cursor()

cursor.execute("""SELECT gid,ST_AsText(geom),landuse from %(table)s""", params)
gids = cursor.fetchall()
log("Got %d rows" % (len(gids)))
i = 0
for gid,geom,landuse in gids:
  # don't use st_distance because it doesnt use the geom index.
  this_params = params.copy()
  this_params['gid'] = gid
  this_params['geom'] = geom
  this_params['landuse'] = landuse
  cursor.execute("""
    SELECT gid
    from %(table)s
    WHERE gid >= %(gid)s
      and ST_DWithin(geom,ST_GeomFromText(%(geom)s, %(SRID)s),%(buffer)s)
      and landuse = %(landuse)s
    """, this_params)
  neighbours = cursor.fetchall()
  i += 1
  # if i % 10 == 0:
  #   sys.stdout.write('.')
  #   sys.stdout.flush()
  if i % 1000 == 0:
    print('{:.2f}'.format(i/len(gids) * 100))
  for neighbour in neighbours:
    if len(neighbour) > 2:
      print(neighbours)
      sys.exit()
    #print(gid,neighbour[0])
    uf.union(gid,neighbour[0])

print()

# execute("""
#   SELECT s1.gid,s2.gid
#   from %s as s1
#   inner join %s as s2 on s2.gid > s1.gid
#   where s1.landuse = s2.landuse
#     and st_distance(s1.geom,s2.geom) < %f;""" % (TABLE, TABLE, BUFFER))
# for a,b in cursor.fetchall():
#   print(a,b)
#   uf.union(a,b)

print(uf.sets())

cursor.execute("""
  DROP table if exists %(next_level)s;
  CREATE table %(next_level)s (
    gid integer unique,
    geom geometry(multipolygon,4326),
    landuse character varying(80)
  );
  CREATE INDEX %(next_level)s_geom_idx
    ON %(next_level)s
    USING GIST (geom);""", params)
db.commit()

for set_ in uf.sets():
  this_params = params.copy()
  this_params['gids'] = AsIs(",".join(map(str,set_)))
  cursor.execute("""
    INSERT into %(next_level)s
    SELECT min(s.gid), st_multi(st_union(st_buffer(s.geom,%(buffer)s))), s.landuse
    from %(table)s as s
    where s.gid in (%(gids)s)
    group by landuse;
    """, this_params)
db.commit()
cursor.close()
db.close()


