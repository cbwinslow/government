create materialized view if not exists mart.politician_profile as
select
  p.person_id,
  p.display_name,
  p.party_current,
  p.home_state,
  count(distinct mt.member_term_id) as term_count,
  count(distinct r.report_id) as disclosure_report_count,
  count(distinct t.transaction_id) as transaction_count
from master.person p
left join leg.member_term mt on mt.person_id = p.person_id
left join disclosure.filer f on f.person_id = p.person_id
left join disclosure.report r on r.filer_id = f.filer_id
left join disclosure.transaction t on t.person_id = p.person_id
group by 1,2,3,4;
