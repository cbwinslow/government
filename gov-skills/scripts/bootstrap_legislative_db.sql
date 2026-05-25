create schema if not exists ingest;
create schema if not exists raw;
create schema if not exists core;
create schema if not exists leg;
create schema if not exists mart;

create table if not exists ingest.job_run (
  job_run_id bigserial primary key,
  job_name text not null,
  source_system text not null,
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  status text not null default 'running',
  details jsonb not null default '{}'::jsonb
);

create table if not exists ingest.api_cursor (
  cursor_id bigserial primary key,
  source_system text not null,
  cursor_name text not null,
  cursor_value text,
  updated_at timestamptz not null default now(),
  unique (source_system, cursor_name)
);

create table if not exists ingest.api_request_log (
  request_id bigserial primary key,
  source_system text not null,
  endpoint text not null,
  request_url text not null,
  http_status int,
  requested_at timestamptz not null default now(),
  response_ms int,
  error_text text,
  meta jsonb not null default '{}'::jsonb
);

create table if not exists raw.govinfo_package (
  raw_id bigserial primary key,
  package_id text not null,
  collection_code text,
  request_url text not null,
  fetched_at timestamptz not null default now(),
  content_sha256 text,
  payload jsonb not null,
  unique (package_id, content_sha256)
);

create table if not exists raw.govinfo_granule (
  raw_id bigserial primary key,
  package_id text not null,
  granule_id text not null,
  request_url text not null,
  fetched_at timestamptz not null default now(),
  content_sha256 text,
  payload jsonb not null,
  unique (package_id, granule_id, content_sha256)
);

create table if not exists core.govinfo_package (
  package_id text primary key,
  collection_code text,
  title text,
  last_modified timestamptz,
  date_issued date,
  package_url text,
  details jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists core.govinfo_granule (
  granule_id text primary key,
  package_id text not null references core.govinfo_package(package_id),
  title text,
  granule_class text,
  granule_url text,
  details jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists leg.bill (
  bill_pk bigserial primary key,
  congress int not null,
  bill_type text not null,
  bill_number int not null,
  title text,
  origin_chamber text,
  introduced_at date,
  latest_action_at date,
  latest_action_text text,
  source_url text,
  raw_last_retrieved_at timestamptz,
  details jsonb not null default '{}'::jsonb,
  unique (congress, bill_type, bill_number)
);

create table if not exists leg.bill_action (
  bill_action_id bigserial primary key,
  congress int not null,
  bill_type text not null,
  bill_number int not null,
  action_date date,
  action_text text,
  action_code text,
  source_url text,
  details jsonb not null default '{}'::jsonb
);

create index if not exists idx_core_govinfo_package_collection on core.govinfo_package(collection_code);
create index if not exists idx_core_govinfo_package_last_modified on core.govinfo_package(last_modified);
create index if not exists idx_core_govinfo_granule_package_id on core.govinfo_granule(package_id);
create index if not exists idx_leg_bill_identity on leg.bill(congress, bill_type, bill_number);
create index if not exists idx_leg_bill_action_identity on leg.bill_action(congress, bill_type, bill_number);
create index if not exists idx_request_log_source_time on ingest.api_request_log(source_system, requested_at desc);
