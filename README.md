# Chemical Clouds — PHP / MySQL

The band website now runs on PHP instead of Flask/Python, with MySQL instead of PostgreSQL/PostGIS. The existing home, biography, music, contact, tour list, map, photographs, font and embeds are retained. Tour locations use ordinary latitude/longitude columns; no spatial extension or Composer package is required.

## Server requirements

- PHP **8.2 or newer**, with **PDO MySQL** (`pdo_mysql`) and JSON support.
- MySQL **8.0.16 or newer**, with InnoDB and `utf8mb4` support.
- Apache, Nginx, or a shared hosting plan that runs PHP.
- Internet access in visitors' browsers for the existing Bootstrap, Leaflet, map tiles, icons, music and video embeds.

The server's PHP version and database details still need to be checked before deployment. This repository contains no live database credentials or database rows.

## Install on your hosting account

1. Download or check out this branch. The application lives in `chemapp-main/`.
2. In your hosting panel, create a MySQL database and user. Select that database in phpMyAdmin and import `chemapp-main/database/schema.sql`. This creates `shows`; it does not erase or overwrite existing data.
3. Copy `chemapp-main/config.example.php` to `chemapp-main/config.php`. Enter the MySQL host, port, database name, username and password provided by your host. This file is ignored by Git. Keep it private.
4. Upload the application and set the site's **document root to `chemapp-main/public/`**. Keep `src/`, `views/`, `database/`, `bin/`, `tests/`, and `config.php` outside the public web directory. Do not upload the whole repository into a publicly served folder.
5. Visit the home, About, Music, Contact and Tour Dates pages. Before show data is imported, Tour Dates displays an empty list and map. If MySQL is unavailable, it displays a service message and returns HTTP 503; private connection details go only to the PHP error log.

### Shared hosting with a fixed `public_html` directory

If you cannot change the document root, use this layout:

```text
account/
  chemapp-private/
    config.php
    src/
    views/
  public_html/
    index.php
    .htaccess
    static/
```

Copy the contents of `chemapp-main/public/` into `public_html/`, **including the images and font under `static/`**. Copy `src/`, `views/`, and your `config.php` into `chemapp-private/`. Change the `$appRoot` line near the top of `public_html/index.php` to:

```php
$appRoot = dirname(__DIR__) . '/chemapp-private';
```

The bootstrap, configuration and view templates use that private application directory; no other include paths need changing.

For a subfolder such as `public_html/band/`, adjust those paths to your actual private directory and set `'base_path' => '/band'` in `config.php`. Normal page links use `index.php?page=...` and do not need URL rewriting.

### Apache / Nginx

Apache's optional `public/.htaccess` supports the old URLs below. It requires `mod_rewrite`, `AllowOverride` permission, and Apache 2.4 authorization syntax. If your host disallows `Options`, remove the `Options -Indexes -MultiViews` line. If `.htaccess` is entirely unsupported, use the query-string URLs instead. The project-root `.htaccess` denies direct access as an extra precaution; it does not replace setting the correct document root. The public child explicitly grants access.

For Nginx, use the `public/` directory as the root, your host's normal PHP-FPM configuration, and `try_files $uri $uri/ /index.php?$query_string;` in `location /`. Do not serve private files from a second location. Nginx ignores `.htaccess`.

| Page | Works without rewrites | Legacy URL with rewrites |
| --- | --- | --- |
| Home | `/index.php?page=home` | `/` |
| Tour dates | `/index.php?page=map` | `/map/map_bp` |
| Music | `/index.php?page=music` | `/music/music_bp` |
| About | `/index.php?page=about` | `/about_bp` |
| Contact | `/index.php?page=mail` | `/mail/mail_bp` |
| Show details | `/index.php?page=info&id=123` | `/info_bp?id=123` |
| Shows API | `/index.php?page=api%2Fshows` | `/database/show` |

Prefix paths with the installation subfolder if necessary. Missing shows and unknown pages return HTTP 404.

## Move existing PostgreSQL show data

Changing the connection settings does **not** transfer the old rows. Keep the old site/database available until the new installation has been checked. Take a backup first.

1. On a computer with `psql` access to the existing PostgreSQL/PostGIS database, run:

   ```sh
   psql "your-existing-PostgreSQL-connection" -f chemapp-main/database/export-postgresql.sql
   ```

   This exports `public.show` to `shows.csv` in the current local directory. It only reads PostgreSQL. The columns are `id,name,date,latitude,longitude,link_ticket,link_img`. Known coordinate systems are transformed to WGS84. SRID 0 is assumed to mean WGS84; verify that assumption for your data. Empty locations remain empty and appear in the tour list without a map marker.

2. Validate the file with the new PHP CLI tools. Legacy `YYYY-M-D` dates are normalized to `YYYY-MM-DD`. Invalid dates, URLs, coordinates or duplicate IDs stop the import with a record number.

   ```sh
   cd chemapp-main
   php bin/import-shows.php --dry-run /private/path/shows.csv
   ```

3. If you have server shell access and have configured MySQL, import into the new empty table:

   ```sh
   php bin/import-shows.php --apply /private/path/shows.csv
   ```

   The CLI import uses one transaction, preserves IDs, and rolls back on errors or existing duplicate IDs. It never updates or deletes existing rows. Run it once against the empty destination table.

4. If your hosting only provides phpMyAdmin, run this command **locally** on a computer with PHP 8.2+, then import the generated SQL into the new empty MySQL `shows` table using phpMyAdmin:

   ```sh
   php bin/csv-to-mysql.php /private/path/shows.csv > /private/path/shows.mysql.sql
   ```

   Check the command succeeded before importing. This converter needs no database connection. It validates all records before emitting SQL and uses hex literals so quotes, backslashes and Unicode survive. Import only into an empty table: phpMyAdmin's error/transaction behavior can depend on its settings; stop on any SQL error and verify the row count afterward.

5. Compare row counts, event names/dates, ticket links and several map locations with the old site before switching traffic. Store CSV/SQL exports outside `public/` and do not commit them.

If you do not have access to the old database, the PHP site can run with an empty `shows` table; request an export from whoever manages PostgreSQL to recover the existing dates.

## Configuration via environment variables

A private `config.php` is simplest for shared hosting. Environment variables override it:

| Setting | Variable |
| --- | --- |
| MySQL host / port | `CHEMAPP_DB_HOST`, `CHEMAPP_DB_PORT` |
| Database / user / password | `CHEMAPP_DB_NAME`, `CHEMAPP_DB_USER`, `CHEMAPP_DB_PASSWORD` |
| Optional Unix socket | `CHEMAPP_DB_SOCKET` |
| Optional database TLS CA file | `CHEMAPP_DB_SSL_CA` |
| Optional private API write token | `CHEMAPP_WRITE_TOKEN` |
| URL prefix, e.g. `/band` | `CHEMAPP_BASE_PATH` |
| Alternate private config file | `CHEMAPP_CONFIG` |

Remote database TLS uses the configured CA and certificate verification. `CHEMAPP_CONFIG` must point to a trusted private PHP file. Use a database user restricted to the application's database. The website needs SELECT; the optional write API/import also needs INSERT. Schema installation requires CREATE separately. Remove the Python deployment and old PostgreSQL environment variables when you switch to this version.

## Shows API

`GET index.php?page=api%2Fshows` returns the shows as JSON. `POST` to the same URL (or the old `/database/show` with rewriting) adds a show. The old unauthenticated write endpoint is replaced with bearer-token authorization.

POST is disabled until you set a long random `write_token` in private configuration. Generate one locally with `php -r 'echo bin2hex(random_bytes(32)), PHP_EOL;'`. Send it only from a trusted admin tool over HTTPS, in an `Authorization: Bearer ...` header; never embed it in the public website. If your host strips Authorization headers, use its PHP/FastCGI forwarding setting. The Apache rewrite file includes forwarding.

Example JSON body, with `Content-Type: application/json`:

```json
{
  "name": "Venue name",
  "date": "2027-05-17",
  "geometry": {"type": "Point", "coordinates": [6.42, 52.02]},
  "link_ticket": "https://example.com/tickets",
  "link_img": "https://example.com/poster.jpg"
}
```

GeoJSON coordinates are **longitude, latitude**, matching the old API. Alternatively send `latitude` and `longitude` directly; omit both for a show without a map location. Links may be empty or valid HTTP(S) URLs. POST returns HTTP 201 and the new ID; validation/authentication/method errors return JSON with an appropriate status. There is no edit/delete admin interface in the original app or this port. Shows can also be maintained through phpMyAdmin.

## Local development and checks

```sh
cd chemapp-main
php -S 127.0.0.1:8000 -t public public/router.php
```

Open `http://127.0.0.1:8000`. The built-in server is only for development. Configure a local MySQL database and import `database/schema.sql` to test tour data.

```sh
find . -name '*.php' -print0 | xargs -0 -n1 php -l
php tests/validation.php
node --check public/static/javascript.js
node --check public/static/map.js
```

For a disposable MySQL database, set the database environment variables and run `CHEMAPP_TEST_DATABASE=1 php tests/database.php`. This test refuses a nonempty `shows` table, inserts inside a transaction and rolls back. The GitHub Actions workflow runs lint, validation, MySQL integration, CLI import/conversion and HTTP smoke tests on PHP 8.2 and 8.3. No real credentials or production database are used.

The original Python implementation remains available in Git history. This conversion does not deploy anything to your live server or migrate its real database automatically.
