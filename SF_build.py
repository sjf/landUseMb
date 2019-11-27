#!/usr/bin/env python3
import psycopg2
from postgis.psycopg import register
from data.unionfind import UnionFind
from data.utils import *
from data.log import *

def execute(sql):
  global cursor
  print(sql)
  cursor.execute(sql)

TABLE = get_arg(1, 'sf_land_use')
NEXT_LEVEL = TABLE + '_2'
BUFFER = 0.000001
log('Building layers from', TABLE)

uf = UnionFind()

db = psycopg2.connect(dbname="sjf")
register(db)
cursor = db.cursor()

execute("""
  SELECT s1.gid,s2.gid
  from %s as s1
  inner join %s as s2 on s2.gid > s1.gid
  where s1.landuse = s2.landuse
    and st_distance(s1.geom,s2.geom) < %f;""" % (TABLE, TABLE, BUFFER))
for a,b in cursor.fetchall():
  print(a,b)
  uf.union(a,b)

print(uf.sets())
sys.exit()
execute("""
  DROP table if exists %s;
  CREATE table %s (
    gid integer unique,
    geom geometry(polygon,4326),
    landuse character varying(80)
  );
  CREATE INDEX %s_geom_idx
    ON %s
    USING GIST (geom);""" % (NEXT_LEVEL, NEXT_LEVEL, NEXT_LEVEL, NEXT_LEVEL))


for set_ in uf.sets():
  execute("""
    INSERT into %s
    SELECT min(s.gid), st_union(st_buffer(s.geom,%f)), s.landuse
    from %s as s
    where s.gid in (%s)
    group by landuse;
    """ % (NEXT_LEVEL, BUFFER, TABLE, ",".join(map(str,set_))))
db.commit()
cursor.close()
db.close()


