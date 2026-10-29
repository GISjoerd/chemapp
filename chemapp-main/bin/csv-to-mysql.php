<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
require dirname(__DIR__) . '/src/bootstrap.php';
require dirname(__DIR__) . '/src/import.php';
if ($argc !== 2) {
    fwrite(STDERR, "Usage: php bin/csv-to-mysql.php /private/path/shows.csv > shows.mysql.sql\n");
    exit(1);
}
try {
    // Validate the entire file before emitting SQL, so a bad record cannot leave a partial export.
    $rows = iterator_to_array(csv_shows($argv[1]));
    echo "-- Import into a new empty shows table after schema.sql.\nSET NAMES utf8mb4;\nSTART TRANSACTION;\n";
    foreach ($rows as $row) {
        $values = [];
        foreach (['id', 'name', 'date', 'latitude', 'longitude', 'link_ticket', 'link_img'] as $key) {
            $value = $row[$key];
            // Hex string literals preserve Unicode, quotes, backslashes and line breaks regardless of SQL mode.
            $values[] = $value === null ? 'NULL' : (is_int($value) || is_float($value) ? (string) $value : "X'" . bin2hex($value) . "'");
        }
        echo 'INSERT INTO shows (id, name, date, latitude, longitude, link_ticket, link_img) VALUES (' . implode(', ', $values) . ");\n";
    }
    echo "COMMIT;\n";
} catch (Throwable $error) {
    fwrite(STDERR, 'Conversion failed: ' . $error->getMessage() . "\n");
    exit(1);
}
