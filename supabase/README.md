# Supabase backend

Project: `mazhar` (ref `sldpdcqysjmrdznqznvb`, region eu-central-1, Frankfurt).
Dashboard: https://supabase.com/dashboard/project/sldpdcqysjmrdznqznvb

The site (docs/v2) only holds the public project URL and the publishable key (`M.cloud` in
`docs/v2/assets/app.js`). That is safe to publish: row-level security lets visitors
**insert** reports, questions, replies and votes only as `pending`, and **read** only rows
whose `status = 'approved'`.

## Reviewing submissions

Use the admin panel: https://ahmedhafezmazhar-ai.github.io/Trip-report/admin/
Moderators sign in with email + password (Supabase Auth). Only accounts listed in
`public.moderators` can see pending posts or change their status (`0003_moderators.sql`).

Adding a moderator:
1. Dashboard → Authentication → Users → Add user → Create new user (tick "Auto Confirm User").
2. Dashboard → SQL Editor, run:
   `insert into public.moderators (user_id, email) select id, email from auth.users where email = 'THEIR-EMAIL';`

Optional: Authentication → Sign In / Providers → turn off "Allow new users to sign up",
so only accounts you create can exist.

Fallback: Table Editor, change `status` to `approved` or `rejected` by hand.

The AI supervisor (D17/D22) will later do this with the service role key, which must never be put in the site.

## Migrations

`migrations/0001_*.sql` and `0002_*.sql` were applied on 2026-11-27. `0003_moderators.sql` must be run once in the SQL Editor.
