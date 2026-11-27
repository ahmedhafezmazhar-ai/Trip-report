# Supabase backend

Project: `mazhar` (ref `sldpdcqysjmrdznqznvb`, region eu-central-1, Frankfurt).
Dashboard: https://supabase.com/dashboard/project/sldpdcqysjmrdznqznvb

The site (docs/v2) only holds the public project URL and the publishable key (`M.cloud` in
`docs/v2/assets/app.js`). That is safe to publish: row-level security lets visitors
**insert** reports, questions, replies and votes only as `pending`, and **read** only rows
whose `status = 'approved'`.

## Reviewing submissions (for now, by hand)

1. Open the dashboard, then Table Editor.
2. Open `review_queue` to see everything waiting, or open `trip_reports` / `questions`.
3. Change `status` to `approved` (publish) or `rejected`. Approved rows show up on the site right away.

The AI supervisor (D17/D22) will later do this with the service role key, which must never be put in the site.

## Migrations

`migrations/0001_*.sql` and `0002_*.sql` were applied on 2026-11-27.
