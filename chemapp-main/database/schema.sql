-- Select the MySQL database created in your hosting panel before importing this file.
-- No DROP, CREATE DATABASE, or automatic data replacement is performed.
CREATE TABLE IF NOT EXISTS shows (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    latitude DECIMAL(10,7) NULL,
    longitude DECIMAL(10,7) NULL,
    link_ticket VARCHAR(255) NOT NULL DEFAULT '',
    link_img VARCHAR(255) NOT NULL DEFAULT '',
    PRIMARY KEY (id),
    KEY shows_date (date),
    CONSTRAINT valid_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT valid_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    CONSTRAINT coordinate_pair CHECK ((latitude IS NULL) = (longitude IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
