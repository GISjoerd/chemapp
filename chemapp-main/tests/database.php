<?php
declare(strict_types=1);
require dirname(__DIR__) . '/src/bootstrap.php';
if (getenv('CHEMAPP_TEST_DATABASE') !== '1') {
    fwrite(STDERR, "Set CHEMAPP_TEST_DATABASE=1 only for a disposable test database.\n");
    exit(1);
}
$pdo = database();
if ((int) $pdo->query('SELECT COUNT(*) FROM shows')->fetchColumn() !== 0) {
    throw new RuntimeException('Refusing to test against a nonempty shows table.');
}
function check(bool $condition, string $message): void
{
    if (!$condition) throw new RuntimeException($message);
}
$pdo->beginTransaction();
try {
    $name = "Mañana '); DROP TABLE shows; -- 🎸";
    $data = validate_show(['name' => $name, 'date' => '2027-05-17', 'geometry' => ['type' => 'Point', 'coordinates' => [6.42, 52.02]], 'link_ticket' => 'https://example.com/tickets']);
    $id = insert_show($pdo, $data);
    $row = find_show($pdo, $id);
    check($row['name'] === $name, 'Prepared statement / Unicode round trip failed.');
    check($row['geometry']['coordinates'] === [6.42, 52.02], 'Database coordinate round trip failed.');
    $empty = validate_show(['name' => 'Without a location', 'date' => '2026-01-01']);
    $explicit = insert_show($pdo, $empty, 12345);
    check($explicit === 12345 && find_show($pdo, 12345)['geometry'] === null, 'Preserved ID/null location failed.');
    check(count(all_shows($pdo)) === 2 && all_shows($pdo)[0]['id'] === $id, 'Show sorting failed.');
    check(find_show($pdo, 99999) === null, 'Missing show lookup failed.');
} finally {
    $pdo->rollBack();
}
check((int) $pdo->query('SELECT COUNT(*) FROM shows')->fetchColumn() === 0, 'Rollback did not leave the table empty.');
echo "MySQL prepared statements, Unicode, dates, coordinates, IDs, sorting and transaction tests passed.\n";
