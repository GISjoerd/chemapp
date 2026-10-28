<?php
declare(strict_types=1);
// Development server only: php -S 127.0.0.1:8000 -t public public/router.php
$path = rawurldecode(parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/');
$file = realpath(__DIR__ . $path);
if ($file !== false && str_starts_with($file, __DIR__ . DIRECTORY_SEPARATOR) && is_file($file) && $path !== '/router.php' && $path !== '/index.php' && !str_starts_with(basename($path), '.')) {
    return false;
}
$_SERVER['SCRIPT_NAME'] = '/index.php';
require __DIR__ . '/index.php';
