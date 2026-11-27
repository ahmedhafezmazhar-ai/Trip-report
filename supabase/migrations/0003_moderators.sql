-- Moderators for the /admin review panel.
-- A moderator is a Supabase Auth user listed in public.moderators. They sign in on /admin
-- with email + password; the page only ever holds the publishable key, and these policies
-- decide what a signed-in moderator may see and change.

create table if not exists public.moderators (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  added_at timestamptz not null default now()
);
alter table public.moderators enable row level security;

create or replace function public.is_moderator() returns boolean
  language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.moderators m where m.user_id = (select auth.uid()));
$$;
revoke all on function public.is_moderator() from public;
grant execute on function public.is_moderator() to anon, authenticated;

-- a moderator can see that they are one (the page uses this to check access)
create policy "moderator sees self" on public.moderators for select to authenticated using (user_id = (select auth.uid()));
grant select on public.moderators to authenticated;

-- moderators read everything, including pending and rejected rows
create policy "moderators read reports"   on public.trip_reports for select to authenticated using ((select public.is_moderator()));
create policy "moderators read questions" on public.questions   for select to authenticated using ((select public.is_moderator()));
create policy "moderators read replies"   on public.replies     for select to authenticated using ((select public.is_moderator()));

-- moderators change only the review columns
grant update (status, review_note, reviewed_at) on public.trip_reports to authenticated;
grant update (status, review_note) on public.questions to authenticated;
grant update (status, correction) on public.replies to authenticated;
create policy "moderators review reports"   on public.trip_reports for update to authenticated using ((select public.is_moderator())) with check ((select public.is_moderator()));
create policy "moderators review questions" on public.questions   for update to authenticated using ((select public.is_moderator())) with check ((select public.is_moderator()));
create policy "moderators review replies"   on public.replies     for update to authenticated using ((select public.is_moderator())) with check ((select public.is_moderator()));

-- add the first moderator: create the user in Authentication > Users, then run
-- insert into public.moderators (user_id, email) select id, email from auth.users where email = 'YOUR-EMAIL';
