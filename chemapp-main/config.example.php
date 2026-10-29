<?php
declare(strict_types=1);
// Copy to config.php, next to src/ and OUTSIDE the public web directory.
// Never commit the real config.php or put these values in browser JavaScript.
return [
    'db_host' => '127.0.0.1',
    'db_port' => '3306',
    'db_name' => 'your_mysql_database',
    'db_user' => 'your_mysql_user',
    'db_password' => 'your_mysql_password',
    'db_socket' => '',        // Optional Unix socket; overrides db_host/db_port.
    'db_ssl_ca' => '',        // CA file for a remote TLS database, if required.
    'write_token' => '',      // Empty disables POST. Set a long random secret to enable.
    'base_path' => null,      // null autodetects; use '/band' if installed under /band/.
];
