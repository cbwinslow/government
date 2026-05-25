-- duplicate identifiers
select source_system, identifier_type, identifier_value, count(*)
from master.person_identifier
group by 1,2,3
having count(*) > 1;

-- transactions without matched person
select count(*) as unmatched_transactions
from disclosure.transaction
where person_id is null;

-- contributions without matched candidate
select count(*) as unmatched_contributions
from finance.contribution
where candidate_id is null;

-- late PTR heuristic check
select person_id, transaction_date, notification_date
from disclosure.transaction
where transaction_date is not null
  and notification_date is not null
  and notification_date > transaction_date + interval '45 days';
