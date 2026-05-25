create extension if not exists vector;
create extension if not exists pg_trgm;

create schema if not exists ingest;
create schema if not exists raw;
create schema if not exists master;
create schema if not exists leg;
create schema if not exists finance;
create schema if not exists disclosure;
create schema if not exists rag;
create schema if not exists mart;

create table if not exists master.person (
  person_id bigserial primary key,
  display_name text not null,
  sort_name text,
  birth_date date,
  party_current text,
  home_state text,
  bio jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists master.person_identifier (
  person_identifier_id bigserial primary key,
  person_id bigint not null references master.person(person_id),
  source_system text not null,
  identifier_type text not null,
  identifier_value text not null,
  confidence numeric(5,4) default 1.0,
  unique (source_system, identifier_type, identifier_value)
);

create table if not exists leg.member_term (
  member_term_id bigserial primary key,
  person_id bigint not null references master.person(person_id),
  chamber text,
  congress int,
  state text,
  district text,
  party text,
  start_date date,
  end_date date,
  details jsonb not null default '{}'::jsonb
);

create table if not exists finance.candidate (
  candidate_id text primary key,
  person_id bigint references master.person(person_id),
  name text,
  office text,
  office_state text,
  party text,
  details jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists finance.committee (
  committee_id text primary key,
  name text,
  committee_type text,
  party text,
  treasurer_name text,
  details jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists finance.contribution (
  contribution_id bigserial primary key,
  cycle int,
  committee_id text references finance.committee(committee_id),
  candidate_id text references finance.candidate(candidate_id),
  contributor_name text,
  contributor_city text,
  contributor_state text,
  employer text,
  occupation text,
  contribution_date date,
  amount numeric(18,2),
  filing_id text,
  source_row_hash text unique,
  details jsonb not null default '{}'::jsonb
);

create table if not exists finance.expenditure (
  expenditure_id bigserial primary key,
  cycle int,
  committee_id text references finance.committee(committee_id),
  payee_name text,
  expenditure_date date,
  amount numeric(18,2),
  purpose text,
  category text,
  filing_id text,
  source_row_hash text unique,
  details jsonb not null default '{}'::jsonb
);

create table if not exists disclosure.filer (
  filer_id bigserial primary key,
  person_id bigint references master.person(person_id),
  source_system text not null,
  filer_name text not null,
  chamber text,
  state text,
  district text,
  is_member boolean,
  details jsonb not null default '{}'::jsonb
);

create table if not exists disclosure.report (
  report_id bigserial primary key,
  filer_id bigint not null references disclosure.filer(filer_id),
  report_type text not null,
  filing_year int,
  filed_at date,
  source_url text,
  checksum text,
  extracted_text text,
  details jsonb not null default '{}'::jsonb
);

create table if not exists disclosure.transaction (
  transaction_id bigserial primary key,
  report_id bigint references disclosure.report(report_id),
  person_id bigint references master.person(person_id),
  owner text,
  asset_name text,
  ticker text,
  asset_type text,
  issuer_name text,
  transaction_type text,
  transaction_date date,
  notification_date date,
  amount_range text,
  amount_low numeric(18,2),
  amount_high numeric(18,2),
  comment_text text,
  source_row_hash text unique,
  details jsonb not null default '{}'::jsonb
);

create table if not exists disclosure.asset_holding (
  holding_id bigserial primary key,
  report_id bigint references disclosure.report(report_id),
  person_id bigint references master.person(person_id),
  owner text,
  asset_name text,
  ticker text,
  asset_type text,
  value_range text,
  income_type text,
  income_amount_range text,
  details jsonb not null default '{}'::jsonb
);

create table if not exists rag.document (
  document_id bigserial primary key,
  source_system text not null,
  document_type text not null,
  external_id text,
  person_id bigint references master.person(person_id),
  report_id bigint references disclosure.report(report_id),
  title text,
  source_url text,
  checksum text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists rag.embedding_chunk (
  chunk_id bigserial primary key,
  document_id bigint not null references rag.document(document_id),
  chunk_index int not null,
  chunk_text text not null,
  metadata jsonb not null default '{}'::jsonb,
  embedding vector(3072),
  created_at timestamptz not null default now(),
  unique (document_id, chunk_index)
);

create index if not exists idx_person_display_name_trgm on master.person using gin (display_name gin_trgm_ops);
create index if not exists idx_person_identifier_source on master.person_identifier(source_system, identifier_type, identifier_value);
create index if not exists idx_member_term_person on leg.member_term(person_id, congress);
create index if not exists idx_finance_contribution_candidate on finance.contribution(candidate_id, cycle);
create index if not exists idx_finance_expenditure_committee on finance.expenditure(committee_id, cycle);
create index if not exists idx_disclosure_transaction_person_date on disclosure.transaction(person_id, transaction_date);
create index if not exists idx_rag_document_person on rag.document(person_id, document_type);
