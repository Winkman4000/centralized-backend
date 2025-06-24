-- Ultimate Geographical Database Schema
-- Hierarchical structure: Continents > Countries > States/Provinces > Cities/Towns

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- 1. CONTINENTS (Top level)
CREATE TABLE continents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    code TEXT UNIQUE, -- e.g., 'NA' for North America
    area_km2 REAL,
    population INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. COUNTRIES (Belongs to continent)
CREATE TABLE countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    continent_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code_iso2 TEXT UNIQUE, -- e.g., 'US', 'CA', 'FR'
    code_iso3 TEXT UNIQUE, -- e.g., 'USA', 'CAN', 'FRA'
    capital TEXT,
    area_km2 REAL,
    population INTEGER,
    currency TEXT,
    language_primary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (continent_id) REFERENCES continents(id) ON DELETE CASCADE,
    UNIQUE(continent_id, name) -- Prevent duplicate country names within same continent
);

-- 3. STATES/PROVINCES (Belongs to country)
CREATE TABLE states_provinces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code TEXT, -- e.g., 'CA' for California, 'ON' for Ontario
    type TEXT DEFAULT 'state', -- 'state', 'province', 'region', 'territory'
    capital TEXT,
    area_km2 REAL,
    population INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE,
    UNIQUE(country_id, name) -- Prevent duplicate state names within same country
);

-- 4. CITIES/TOWNS (Belongs to state/province)
CREATE TABLE cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_province_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'city', -- 'city', 'town', 'village', 'municipality'
    population INTEGER,
    area_km2 REAL,
    elevation_m INTEGER,
    latitude REAL,
    longitude REAL,
    is_capital BOOLEAN DEFAULT FALSE, -- Is this the state/province capital?
    founded_year INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_province_id) REFERENCES states_provinces(id) ON DELETE CASCADE,
    UNIQUE(state_province_id, name) -- Prevent duplicate city names within same state
);

-- INDEXES for better query performance
CREATE INDEX idx_countries_continent ON countries(continent_id);
CREATE INDEX idx_states_country ON states_provinces(country_id);
CREATE INDEX idx_cities_state ON cities(state_province_id);
CREATE INDEX idx_cities_population ON cities(population);
CREATE INDEX idx_countries_population ON countries(population);

-- VIEWS for easy hierarchical queries
-- View to see full hierarchy path
CREATE VIEW location_hierarchy AS
SELECT 
    c.id as city_id,
    c.name as city_name,
    c.type as city_type,
    c.population as city_population,
    sp.name as state_province_name,
    sp.type as state_province_type,
    co.name as country_name,
    co.code_iso2 as country_code,
    cont.name as continent_name,
    -- Full path like "North America > United States > California > Los Angeles"
    cont.name || ' > ' || co.name || ' > ' || sp.name || ' > ' || c.name as full_path
FROM cities c
JOIN states_provinces sp ON c.state_province_id = sp.id
JOIN countries co ON sp.country_id = co.id
JOIN continents cont ON co.continent_id = cont.id;

-- View for continent statistics
CREATE VIEW continent_stats AS
SELECT 
    cont.id,
    cont.name as continent_name,
    COUNT(DISTINCT co.id) as total_countries,
    COUNT(DISTINCT sp.id) as total_states_provinces,
    COUNT(DISTINCT c.id) as total_cities,
    SUM(co.population) as total_population,
    SUM(co.area_km2) as total_area_km2
FROM continents cont
LEFT JOIN countries co ON cont.id = co.continent_id
LEFT JOIN states_provinces sp ON co.id = sp.country_id
LEFT JOIN cities c ON sp.id = c.state_province_id
GROUP BY cont.id, cont.name;

-- View for country statistics
CREATE VIEW country_stats AS
SELECT 
    co.id,
    co.name as country_name,
    co.code_iso2,
    cont.name as continent_name,
    COUNT(DISTINCT sp.id) as total_states_provinces,
    COUNT(DISTINCT c.id) as total_cities,
    co.population as country_population,
    SUM(c.population) as cities_population_sum
FROM countries co
JOIN continents cont ON co.continent_id = cont.id
LEFT JOIN states_provinces sp ON co.id = sp.country_id
LEFT JOIN cities c ON sp.id = c.state_province_id
GROUP BY co.id, co.name, co.code_iso2, cont.name, co.population;

-- Sample data to get started
INSERT INTO continents (name, code, area_km2, population) VALUES
('North America', 'NA', 24709000, 579000000),
('South America', 'SA', 17840000, 434000000),
('Europe', 'EU', 10180000, 746000000),
('Asia', 'AS', 44579000, 4641000000),
('Africa', 'AF', 30370000, 1340000000),
('Australia/Oceania', 'OC', 8600000, 45000000),
('Antarctica', 'AN', 14200000, 0);

-- Sample countries
INSERT INTO countries (continent_id, name, code_iso2, code_iso3, capital, area_km2, population, currency, language_primary) VALUES
(1, 'United States', 'US', 'USA', 'Washington D.C.', 9833520, 331900000, 'USD', 'English'),
(1, 'Canada', 'CA', 'CAN', 'Ottawa', 9984670, 38000000, 'CAD', 'English'),
(1, 'Mexico', 'MX', 'MEX', 'Mexico City', 1964375, 128900000, 'MXN', 'Spanish'),
(3, 'France', 'FR', 'FRA', 'Paris', 643801, 67400000, 'EUR', 'French'),
(3, 'Germany', 'DE', 'DEU', 'Berlin', 357022, 83200000, 'EUR', 'German'),
(3, 'United Kingdom', 'GB', 'GBR', 'London', 243610, 67500000, 'GBP', 'English');

-- Sample states/provinces
INSERT INTO states_provinces (country_id, name, code, type, capital, area_km2, population) VALUES
(1, 'California', 'CA', 'state', 'Sacramento', 423967, 39500000),
(1, 'Texas', 'TX', 'state', 'Austin', 695662, 29000000),
(1, 'New York', 'NY', 'state', 'Albany', 141297, 19800000),
(1, 'Florida', 'FL', 'state', 'Tallahassee', 170312, 21500000),
(2, 'Ontario', 'ON', 'province', 'Toronto', 1076395, 14700000),
(2, 'Quebec', 'QC', 'province', 'Quebec City', 1542056, 8500000),
(2, 'British Columbia', 'BC', 'province', 'Victoria', 944735, 5100000);

-- Sample cities
INSERT INTO cities (state_province_id, name, type, population, area_km2, latitude, longitude, is_capital, founded_year) VALUES
(1, 'Los Angeles', 'city', 3980000, 1302, 34.0522, -118.2437, FALSE, 1781),
(1, 'San Francisco', 'city', 875000, 121, 37.7749, -122.4194, FALSE, 1776),
(1, 'Sacramento', 'city', 525000, 259, 38.5816, -121.4944, TRUE, 1848),
(1, 'San Diego', 'city', 1420000, 964, 32.7157, -117.1611, FALSE, 1769),
(2, 'Houston', 'city', 2320000, 1658, 29.7604, -95.3698, FALSE, 1836),
(2, 'Dallas', 'city', 1340000, 999, 32.7767, -96.7970, FALSE, 1841),
(2, 'Austin', 'city', 965000, 827, 30.2672, -97.7431, TRUE, 1839),
(3, 'New York City', 'city', 8380000, 783, 40.7128, -74.0060, FALSE, 1624),
(3, 'Buffalo', 'city', 255000, 136, 42.8864, -78.8784, FALSE, 1789),
(3, 'Albany', 'city', 97000, 56, 42.6526, -73.7562, TRUE, 1614),
(5, 'Toronto', 'city', 2930000, 630, 43.6532, -79.3832, TRUE, 1793),
(5, 'Ottawa', 'city', 995000, 2790, 45.4215, -75.6972, FALSE, 1826),
(6, 'Montreal', 'city', 1780000, 365, 45.5017, -73.5673, FALSE, 1642),
(6, 'Quebec City', 'city', 540000, 454, 46.8139, -71.2080, TRUE, 1608),
(7, 'Vancouver', 'city', 675000, 115, 49.2827, -123.1207, FALSE, 1886),
(7, 'Victoria', 'city', 92000, 20, 48.4284, -123.3656, TRUE, 1843); 