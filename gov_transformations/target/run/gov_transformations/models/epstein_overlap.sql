
  create view "govdata"."public_network_mapping"."epstein_overlap__dbt_tmp"
    
    
  as (
    

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
    OR e.known_aliases ILIKE '%' || f.last || '%'
  );