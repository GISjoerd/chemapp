<?php
declare(strict_types=1);

/** Stream and validate the PostgreSQL export; never silently skip a bad record. */
function csv_shows(string $path): Generator
{
    $handle = @fopen($path, 'rb');
    if ($handle === false) {
        throw new RuntimeException('Cannot open the CSV file.');
    }
    try {
        $header = fgetcsv($handle, 0, ',', '"', '');
        $required = ['id', 'name', 'date', 'latitude', 'longitude', 'link_ticket', 'link_img'];
        if (is_array($header) && is_string($header[0])) {
            $header[0] = preg_replace('/^\xEF\xBB\xBF/', '', $header[0]);
        }
        if (!is_array($header) || count($header) !== count($required) || count(array_unique($header)) !== count($required) || array_diff($required, $header) !== []) {
            throw new InvalidArgumentException('CSV headers must be: ' . implode(',', $required));
        }
        $record = 1;
        $ids = [];
        while (($row = fgetcsv($handle, 0, ',', '"', '')) !== false) {
            $record++;
            if ($row === [null]) {
                continue;
            }
            if (count($row) !== count($header)) {
                throw new InvalidArgumentException('Incorrect number of columns at CSV record ' . $record);
            }
            $data = array_combine($header, $row);
            $id = filter_var($data['id'], FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 4294967295]]);
            if ($id === false || isset($ids[$id])) {
                throw new InvalidArgumentException('Invalid or duplicate id at CSV record ' . $record);
            }
            $ids[$id] = true;
            try {
                $show = validate_show($data);
            } catch (InvalidArgumentException $error) {
                throw new InvalidArgumentException('CSV record ' . $record . ': ' . $error->getMessage());
            }
            yield ['id' => $id] + $show;
        }
    } finally {
        fclose($handle);
    }
}
