-- Mazhar: trip reports, questions, replies and votes.
-- Nothing is public until a moderator (or the AI supervisor, D17/D22) approves it.
-- Anonymous visitors may insert (pen name only, D18) but only ever read approved rows.

create table public.trip_reports (
  id uuid primary key default gen_random_uuid(),
  substance text not null,
  title text not null default '',
  pen_name text not null default '',
  body jsonb not null,               -- background, doses, timeline, keywords (report.html format)
  status text not null default 'pending' check (status in ('pending','approved','rejected','escalated')),
  review_note text,
  created_at timestamptz not null default now(),
  reviewed_at timestamptz
);
create index on public.trip_reports (substance, status);

create table public.questions (
  id uuid primary key default gen_random_uuid(),
  text text not null check (char_length(text) between 10 and 1500),
  pen_name text not null default '',
  substances text[] not null default '{}',
  status text not null default 'pending' check (status in ('pending','approved','rejected','escalated')),
  review_note text,
  created_at timestamptz not null default now()
);
create index on public.questions using gin (substances);

create table public.replies (
  id uuid primary key default gen_random_uuid(),
  question_id uuid not null references public.questions(id) on delete cascade,
  text text not null check (char_length(text) between 2 and 3000),
  pen_name text not null default '',
  status text not null default 'pending' check (status in ('pending','approved','rejected','escalated')),
  correction text,                   -- AI supervisor correction linking to Info (D17.2)
  created_at timestamptz not null default now()
);

create table public.votes (
  target_id text not null,           -- question/reply id or 'faq-<id>'
  voter text not null,               -- random id kept on the device
  value smallint not null default 1 check (value in (1,-1)),
  created_at timestamptz not null default now(),
  primary key (target_id, voter)
);

alter table public.trip_reports enable row level security;
alter table public.questions   enable row level security;
alter table public.replies     enable row level security;
alter table public.votes       enable row level security;

-- read: approved only
create policy "read approved reports"   on public.trip_reports for select using (status = 'approved');
create policy "read approved questions" on public.questions   for select using (status = 'approved');
create policy "read approved replies"   on public.replies     for select using (status = 'approved');
create policy "read votes"              on public.votes       for select using (true);

-- write: anyone may submit, always as pending
create policy "submit report"   on public.trip_reports for insert with check (status = 'pending' and reviewed_at is null and review_note is null);
create policy "submit question" on public.questions   for insert with check (status = 'pending' and review_note is null);
create policy "submit reply"    on public.replies     for insert with check (status = 'pending' and correction is null);
create policy "vote"            on public.votes       for insert with check (true);
-- moderators use the service role (bypasses RLS) from the review tooling.
