<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
require dirname(__DIR__) . '/src/bootstrap.php';
require dirname(__DIR__) . '/src/import.php';
if ($argc !== 3 || !in_array($argv[1], ['--dry-run', '--apply'], true)) {
    fwrite(STDERR, "Usage: php bin/import-shows.php --dry-run|--apply /private/path/shows.csv\n");
    exit(1);
}
$pdo = null;
try {
    $apply = $argv[1] === '--apply';
    if ($apply) {
        $pdo = database();
        $pdo->beginTransaction();
    }
    $count = 0;
    foreach (csv_shows($argv[2]) as $show) {
        if ($apply) {
            insert_show($pdo, $show, $show['id']);
        }
        $count++;
    }
    if ($apply) {
        $pdo->commit();
    }
    echo $apply ? "Imported $count shows.\n" : "Validated $count shows; no database changes made.\n";
} catch (Throwable $error) {
    if ($pdo instanceof PDO && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    fwrite(STDERR, 'Import failed; no rows committed: ' . $error->getMessage() . "\n");
    exit(1);
}
