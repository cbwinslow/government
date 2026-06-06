-- Epstein Network Mapping & Financial Correlation
-- Maps known associates and flight logs against financial disclosures

CREATE SCHEMA IF NOT EXISTS network_mapping;

-- 1. Create Epstein Associates Table
CREATE TABLE IF NOT EXISTS network_mapping.epstein_associates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    role VARCHAR(255),
    flight_log_count INT,
    known_aliases VARCHAR(500)
);

-- 2. Create the Correlation View
-- This view cross-references our newly ingested financial_data
-- with the Epstein associates to find any financial overlap.
CREATE OR REPLACE VIEW network_mapping.epstein_financial_overlap AS
SELECT 
    f.filing_year,
    f.first AS first_name,
    f.last AS last_name,
    f.docid,
    f.filingtype,
    e.name AS epstein_associate_name,
    e.role AS associate_role
FROM 
    financial_data.house_financial_disclosures f
JOIN 
    network_mapping.epstein_associates e 
    ON f.last ILIKE '%' || e.name || '%'
    OR e.known_aliases ILIKE '%' || f.last || '%';
