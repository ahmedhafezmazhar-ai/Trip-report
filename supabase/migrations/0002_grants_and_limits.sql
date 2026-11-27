-- Explicit API grants (newer Supabase projects don't expose new tables to the API by default)
-- and size limits so anonymous submissions can't be used to dump large blobs.

grant usage on schema public to anon, authenticated;
grant select, insert on public.trip_reports, public.questions, public.replies, public.votes to anon, authenticated;

alter table public.trip_reports add constraint trip_reports_size check (
  char_length(substance) <= 120 and char_length(title) <= 200 and char_length(pen_name) <= 60
  and pg_column_size(body) <= 200000);
alter table public.questions add constraint questions_size check (
  char_length(pen_name) <= 60 and cardinality(substances) <= 10);
alter table public.replies add constraint replies_size check (char_length(pen_name) <= 60);
alter table public.votes add constraint votes_size check (char_length(target_id) <= 80 and char_length(voter) <= 80);

-- moderators: queue view for the review tooling (service role only)
create or replace view public.review_queue with (security_invoker = true) as
  select 'report' as kind, id, substance as topic, pen_name, created_at, status from public.trip_reports where status in ('pending','escalated')
  union all
  select 'question', id, array_to_string(substances, ', '), pen_name, created_at, status from public.questions where status in ('pending','escalated')
  union all
  select 'reply', id, question_id::text, pen_name, created_at, status from public.replies where status in ('pending','escalated');
revoke all on public.review_queue from anon, authenticated;
