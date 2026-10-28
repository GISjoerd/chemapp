<?php
declare(strict_types=1);
require dirname(__DIR__) . '/src/bootstrap.php';
require dirname(__DIR__) . '/src/import.php';

function check(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}
function rejects(callable $operation): void
{
    try {
        $operation();
    } catch (InvalidArgumentException) {
        return;
    }
    throw new RuntimeException('Expected validation failure.');
}
$show = ['name' => 'Mañana 🎸', 'date' => '2024-5-17', 'geometry' => ['type' => 'Point', 'coordinates' => [6.42, 52.02]], 'link_ticket' => 'https://example.com/tickets?x=1&y=2', 'link_img' => ''];
$valid = validate_show($show);
check($valid['date'] === '2024-05-17', 'Legacy date normalization failed.');
check($valid['latitude'] === 52.02 && $valid['longitude'] === 6.42, 'GeoJSON coordinate order reversed.');
check(validate_show(['name' => 'No location', 'date' => '2028-02-29'])['latitude'] === null, 'Nullable location failed.');
check(validate_show(['name' => 'At zero', 'date' => '2027-01-01', 'latitude' => 0, 'longitude' => 0])['longitude'] === 0.0, 'Zero coordinates lost.');
foreach ([['date' => '2027-02-29'], ['date' => '0001-01-01'], ['name' => ''], ['name' => str_repeat('é', 101)], ['name' => []], ['link_ticket' => 'javascript:alert(1)'], ['link_img' => 'data:image/png;base64,abc'], ['geometry' => ['type' => 'LineString', 'coordinates' => [0, 0]]], ['geometry' => ['type' => 'Point', 'coordinates' => [181, 0]]], ['geometry' => ['type' => 'Point', 'coordinates' => [0, -91]]], ['geometry' => ['type' => 'Point', 'coordinates' => [false, 0]]]] as $change) {
    rejects(fn () => validate_show(array_replace($show, $change)));
}
rejects(fn () => validate_show(['name' => 'Partial location', 'date' => '2027-01-01', 'latitude' => 52]));
check(http_url('javascript:alert(1)') === '', 'Unsafe URL allowed.');
check(e('<script>"&') === '&lt;script&gt;&quot;&amp;', 'HTML escaping failed.');
$_SERVER['SCRIPT_NAME'] = '/band/index.php';
check(asset('alien_cow.ttf') === '/band/static/alien_cow.ttf', 'Subfolder asset path failed.');
check(page_url('info', ['id' => 3]) === '/band/index.php?page=info&id=3', 'Subfolder page link failed.');
$_SERVER['SCRIPT_NAME'] = '/index.php';
check(asset('style.css') === '/static/style.css', 'Root asset path failed.');
$public = public_show(['id' => '2', 'latitude' => '52.02', 'longitude' => '6.42', 'name' => 'Test', 'date' => '2027-01-01', 'link_ticket' => '', 'link_img' => '']);
check($public['geometry']['coordinates'] === [6.42, 52.02], 'API GeoJSON failed.');
$temp = tempnam(sys_get_temp_dir(), 'chemapp-csv-');
try {
    $file = fopen($temp, 'wb');
    fputcsv($file, ['id', 'name', 'date', 'latitude', 'longitude', 'link_ticket', 'link_img'], ',', '"', '');
    fputcsv($file, [7, "Mañana, \"Live\" \\ 🎸\nFestival", '2024-5-17', '52.02', '6.42', '', ''], ',', '"', '');
    fputcsv($file, [8, 'No location', '2027-01-01', '', '', '', ''], ',', '"', '');
    fclose($file);
    $rows = iterator_to_array(csv_shows($temp));
    check(count($rows) === 2 && $rows[0]['id'] === 7, 'CSV IDs/count failed.');
    check($rows[0]['name'] === "Mañana, \"Live\" \\ 🎸\nFestival", 'CSV quoting/Unicode failed.');
    check($rows[1]['longitude'] === null, 'CSV null coordinates failed.');
    $file = fopen($temp, 'ab');
    fputcsv($file, [7, 'Duplicate', '2027-01-01', '', '', '', ''], ',', '"', '');
    fclose($file);
    rejects(fn () => iterator_to_array(csv_shows($temp)));
} finally {
    unlink($temp);
}
echo "Validation, coordinate order, URL/HTML safety, subfolder links and CSV tests passed.\n";
