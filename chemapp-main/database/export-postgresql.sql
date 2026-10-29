-- Run in psql connected to the OLD PostgreSQL/PostGIS database:
--   psql "your-existing-connection" -f database/export-postgresql.sql
-- Writes shows.csv into the current local directory. Does not modify PostgreSQL.
-- Coordinates with a known SRID are transformed to WGS84 (longitude/latitude).
-- SRID 0 is assumed to already mean WGS84: verify your old data before importing.
-- The CSV importer rejects invalid dates/coordinates rather than silently changing them.
\copy (SELECT id, name, date, ST_Y(CASE WHEN ST_SRID(geometry) = 0 THEN ST_SetSRID(geometry, 4326) ELSE ST_Transform(geometry, 4326) END) AS latitude, ST_X(CASE WHEN ST_SRID(geometry) = 0 THEN ST_SetSRID(geometry, 4326) ELSE ST_Transform(geometry, 4326) END) AS longitude, COALESCE(link_ticket, '') AS link_ticket, COALESCE(link_img, '') AS link_img FROM public.show ORDER BY id) TO 'shows.csv' WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8')
