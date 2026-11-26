# Mazhar App: design log

Status: **finished** (Hany closed the design on 2026-11-26 and moved to the build step). Changes from now on are added as new decisions and recorded in the change history.
Started: 2026-11-25

Only decisions Hany has explicitly agreed to are recorded here. Each decision has a number and a date. A changed decision is marked as superseded, never deleted.

## Agreed decisions

**D1 (2026-11-25): Reddit community section for each subject.** Each subject (substance or topic) gets its own section with relevant Reddit discussions. It is kept separate from the sourced reference content. How it gets the content and how it is labelled are still open (see Q4 and Q5).

**[SUPERSEDED 2026-11-26]** **D2 (2026-11-25): All gathered data is combined into structured JSON.** Every source (PsychonautWiki, books, Reddit, future sources) is merged into JSON files, with a source/credit on every entry.

**[SUPERSEDED 2026-11-26]** **D3 (2026-11-25): The app gets answers by calling fixed data endpoints, not by putting the data into system prompts or LLM prompts.** Hany's word for this is "webhooks". Each kind of question maps to a fixed endpoint that reads the JSON and returns structured data with its sources.

**[SUPERSEDED 2026-11-26]** **D4 (2026-11-25): Feature set, items 1 to 17 of the first brainstorm.**
- For people seeking guidance:
  1. Substance profile in plain language (what it does, onset/peak/duration timeline, dose ranges, main risks up front).
  2. Interaction checker for 2+ substances, including prescription meds, with colour-coded risk and the reason.
  3. Emergency mode (overdose warning signs, what to do, recovery position, when to call emergency services, local numbers).
  4. Safer use checklist per substance (testing, set and setting, trip sitter, redosing, hydration, aftercare).
  5. Drug checking guide (which reagent test, what the colours mean).
  6. Personal risk factors (conditions, pregnancy, mental health history, medications) to tailor warnings; may stay on device only.
  7. Dependence and tolerance info, with links to support and treatment.
- For researchers:
  8. Full search and filters (chemical class, effect, receptor, legal status, route).
  9. Every claim linked to its source, with a confidence level (clinical vs anecdotal).
  10. Compare view for 2+ substances.
  11. Data export (CSV/JSON) with citations, respecting source licences.
- For students:
  12. Learning paths (pharmacology basics, drug classes, history and policy).
  13. Glossary.
  14. Quizzes or flashcards.
- Across everyone:
  15. Ask a question in plain words, answered only from the library with citations, and a refusal when the library doesn't cover it (how AI is involved: see Q6).
  16. Multilingual (which languages: see Q3).
  17. Works offline.

**D5 (2026-11-25): Trip report flow.** Users write their own trip reports, in this order:
1. Choose the substance.
2. See its harm reduction information, dosage and effects first.
3. Write the report as a timeline.
4. Familiar terms (e.g. come-up, peak, comedown, redose, named effects) are explained along the way.

**D6 (2026-11-26): Web app, two ways in.** The product is a web app. The first step is finding a substance either by typing its name or through a "smart map" (what the map shows: see Q11).

**D7 (2026-11-26): Each substance page has two sections.** (a) Info: all PsychonautWiki information about the substance. (b) Trip reports. Trip reports live inside each substance page, not in a separate app (answers part of Q10).

**D8 (2026-11-26): Trip report format, smarter than Erowid's classic format.** A report has:
1. Background first: the writer's past experiences with different substances, age, and the setting.
2. A very detailed timeline of the trip.
3. Keywords the writer picks to describe the trip: what they feel and what they see.
Builds on D5.

**D9 (2026-11-26): Smart map has both views.** Users can browse substances by family (chemical class) or by effect. Answers Q11.

**D10 (2026-11-26): Age is given as a range** (e.g. 18-24, 25-34), not an exact age, to protect anonymity.

**D11 (2026-11-26): New trip reports are displayed in a classic readable report format like Erowid's.** The structured data from D8 (background, timeline, keywords) sits behind it.

**D12 (2026-11-26): Reddit links and summary on each substance page.** Refines D1 and answers Q4 (summaries plus links).
1. The user first confirms the substance name, because names can be confusing.
2. The page then links directly to the relevant Reddit posts, so users can read them with all comments, responses and upvotes.
3. If possible, a general summary of what Reddit says: general warnings, how much information is available, and the level of risk.

**D13 (2026-11-26): Trip reports are 18+ only.** Minimum age 18; age given as a range (D10).

**D14 (2026-11-26): A general harm reduction page** for the whole site (not tied to one substance).

**D15 (2026-11-26): A warning intro for each substance,** shown on its page.

**D16 (2026-11-26): Third section on each substance page: questions forum.**
1. Important questions are featured, e.g. "What are the signs of overdose and what do I do?"
2. Forum-style display.
3. Users post their own questions, and other users reply.
4. Everything happens under AI bot supervision.

**D17 (2026-11-26): What the AI supervisor does in the forum.**
1. Screens posts before they appear: blocks buying/selling, personal details, and anything suggesting a minor.
2. Flags dangerous replies (wrong dose, risky combination) and attaches a correction linking to the Info section.
3. Emergency detection: if a post sounds like an emergency happening now, it instantly shows overdose steps and the local emergency number.
4. Suggests existing answers before a duplicate is posted.
5. Sends anything unclear to a human moderator.
Featured questions are answered from verified info, not by users.

**D18 (2026-11-26): Posting identity: both options.** Users can post with a pen name only (no email, no real name), or create an account.

**D19 (2026-11-26): Order of the Trip reports section.** Refines D12 (the Reddit part lives here).
1. A general summary drawn from both Reddit posts and reports submitted on the site.
2. The site's own trip reports.
3. Trip reports from Reddit, with links to the original posts (after the substance name is confirmed).

**D20 (2026-11-26): Trip report keywords.** The feel/see vocabulary is PsychonautWiki's effect list (Subjective Effect Index). Each keyword has an intensity of 1 to 4 and is tied to a moment in the timeline. Answers Q12.

**D21 (2026-11-26): Extra background fields (optional).** Besides past experiences, age range and setting: weight, medications, mood and intention, and whether the substance was tested. Answers Q13.

**D22 (2026-11-26): The AI supervisor (D17) also reviews trip reports before they are published.** Answers Q19.

**D23 (2026-11-26): Live trip report visibility.** A live session can be started as private or public, and switched either way later.

**D24 (2026-11-26): An AI companion is always present in a live session.**

**D25 (2026-11-26): Human support is essential in live sessions.** Experienced psychonauts can see who is live, join, and answer their questions. Human answers carry more weight with people than AI ones.

**D26 (2026-11-26): Who can be a human sitter.** Sitters need an account (not pen name only). An "Experienced sitter" badge is earned by completing a short sitter guide and quiz (from the trip sitter material) plus good ratings from people helped; badge holders show first. Repeated bad advice caught by the AI supervisor removes the badge. A "Live now" board lists public sessions (pen name, substance, current phase, raised hand when they have a question); psychonauts tap to join the session chat.

**D27 (2026-11-26): Protections for people while live.**
1. No private messages from strangers; chat stays in the session unless the tripper invites someone.
2. No sharing of phone numbers, social handles or meeting places (AI blocks it).
3. One-tap block and report; the tripper can remove anyone.
4. The AI supervisor (D17) watches live chat.

**D28 (2026-11-26): Private friend-sitter link.** The tripper can share a private link so a friend follows live (timeline, check-ins) and is alerted on a missed check-in or SOS, with a sitter guide.

**D29 (2026-11-26): Live mode basics.**
1. Phase tracker: where you are on the substance's timeline (come-up, peak, comedown) and time left.
2. Big-button logging for an altered state: one-tap feel/see keywords, intensity, short notes or voice notes.
3. Redose and interaction warnings.
4. Check-ins every 30 to 60 minutes.
5. An always-visible SOS button: overdose steps, local emergency number, alerts the sitter; location sharing opt-in only.
6. Afterwards, the session becomes a draft trip report (D8 format) to edit, then publish or keep private.

**D30 (2026-11-26): Languages.** English is the default. Everything can be translated into any language, and users can write in their own language and it is translated. Answers Q3.

**D31 (2026-11-26): Extra tools live in the Questions forum section.** All four come back there: (a) interaction checker for 2+ substances including medications, (b) drug checking guide (reagent test colours), (c) research tools (filters, compare, export), (d) learning paths for students.

**D32 (2026-11-26): Shulgin substances.** Every substance Shulgin worked on links to his own trip report for it. Extra information about his work and history is shown, more extensively than PsychonautWiki does.

**D33 (2026-11-26): Shulgin details.** Refines D32.
1. Link target: each substance's own PiHKAL/TiHKAL entry in Erowid's online Shulgin library.
2. A "Shulgin" card on each of his substances: book and entry number, his dose and duration, his rating (±, +, ++, +++, ++++), the year he made or tested it, and a "Read his report" link.
3. A dedicated Alexander and Ann Shulgin page: biography, timeline of their work, the Shulgin rating scale explained, list of all their compounds.
4. A "Shulgin compounds" filter on the smart map.

**D34 (2026-11-26): Translation display.** Refines D30. Translated text shows a "translated" label and a "view original" toggle. Full right-to-left layout for Arabic, Persian and Hebrew.

**D35 (2026-11-26): The third section of each substance page is named "Questions & Tools".**

**D36 (2026-11-26): Release everything at once,** not in phases. Answers Q23 and Q1.

**D37 (2026-11-26): Human moderators are Hany plus a team of moderators.** They review what the AI supervisor escalates. Answers Q24.

**D38 (2026-11-26): The Reddit summary is labelled "What the Reddit community says, not verified".**

**D39 (2026-11-26): Home page.** Search bar, smart map, "Live now" count, newest trip reports, link to the harm reduction page, and a button to start a report. Answers Q25.

**D40 (2026-11-26): Web app only, usable from any device, no download needed.** Answers Q2.

**D41 (2026-11-26): The "Start a report" button offers two choices:** "Write about a past trip" and "Go live now". Answers Q26.

**D42 (2026-11-26): Installable from the browser** ("add to home screen", no app store), opening like an app, with the harm reduction page and emergency steps working offline. Answers Q27.

**D43 (2026-11-26): Reddit sources, for now:** r/DrugNerds, r/harmreduction, r/Psychonaut, r/microdosing, r/researchchemicals, plus one subreddit per substance where one exists. Hany: "good for now", so the list may grow. Answers Q28.

**D44 (2026-11-26): Substance map approved with all 14 proposed fixes.** Hany replied "Approved" (no per-item answers saved on the review page, so every proposal applies as written). Review page: https://claude.ai/artifact/HR819smztZeLjFUAFS1L6R, data in design/substance-map/. Fixes: THC and its 5 variants move to Cannabinoids; Methadone and Pethidine move to Opioids; obvious unclassified substances are refiled (rest go to Other); 27 recipes and extraction methods leave the map and show on their parent substance page; 41 two-family substances show in both families; duplicate class names are merged; odd class labels are fixed; Antipsychotics, Antidepressants and Anxiolytics merge into "Prescription medicines"; missing classes, effects and doses get filled later, with clear warnings until then; Ego death is added as an effect; 125 Shulgin-only compounds are added with a "Shulgin only" tag; a Plants & fungi family is added.

**D45 (2026-11-26): The 10 featured FAQs are approved** as drafted in the doc "Mazhar featured FAQs" (https://claude.ai/artifact/AsmpUPkQ9p4YUp8TmHt953): a general answer from PsychonautWiki plus a substance-specific auto-fill, and user-added questions optionally tied to a substance, screened as in D17.

**D46 (2026-11-26): Users can upvote forum questions and answers.** Answers Q29.

_Note (2026-11-26): Hany confirmed D2 (JSON), D3 (endpoints, not prompts) and D4 (features 1 to 17) no longer stand under the new concept. They are kept above, marked superseded, for history._

## Open questions

1. ~~Folded into Q23 (release phases)~~ Which audiences and feature groups make up version 1?
2. ~~Answered by D40~~ Platform: web app agreed (D6). Is a phone app also wanted later?
3. ~~Answered by D30~~ Languages at launch?
4. ~~Reddit section, how it gets content~~ Answered by D12 (links plus summary). Note: Reddit's API terms apply; commercial use needs Reddit's permission.
5. Reddit section, labelling and safety: label it "community experiences, not verified"? Filter or flag dangerous advice? Which subreddits count as sources?
6. ~~Dropped with D3~~ Is there an AI layer for free-text questions at all? (a) none: search box with autocomplete plus structured pages and tools; (b) AI only reads the question, picks which endpoint to call, and words the result, never answering from its own knowledge; (c) undecided.
7. ~~Dropped with D3~~ The endpoint list and the JSON shape for a substance (draft proposed in the thread on 2026-11-25).
8. ~~Dropped with D4~~ Brainstorm items 18 to 20 (no account/no tracking, content pipeline with credit, legal status by country): in or out? Hany locked "17 features".
9. ~~Mostly settled by D12, D17, D22, D24~~ Which AI uses to adopt (build-time data enrichment and runtime features, proposed 2026-11-25).
10. Trip reports (D5, D7, D8): moderation, anonymity, safety checks while writing, and how copyrighted reports (TiHKAL, Shulgin Index, Erowid pending permission) may be used. Age: 18+ and range agreed (D10, D13).
11. ~~Smart map: what does it map?~~ Answered by D9.
12. ~~Answered by D20~~ Keyword vocabulary: use PsychonautWiki's Subjective Effect Index? Intensity scale per keyword? Keywords tied to timeline moments?
13. ~~Answered by D21~~ Background fields beyond past experiences, age and setting (e.g. weight, medications, mood/intention, tested or not)?
14. ~~Do D2 to D4 still stand?~~ Answered: no, superseded.
15. How data is stored and served under the new concept (replaces D2/D3).
16. ~~Answered by D14 to D16, D31~~ Which other features (beyond info, trip reports, map, Reddit) the web app needs (replaces D4). Partly answered by D14, D15, D16; still open: interaction checker, drug checking guide, research tools, learning, languages.
17. ~~Forum details~~ Answered by D17, D18.
18. ~~Where Reddit sits~~ Answered by D19.
19. ~~Answered by D22~~ Does the AI supervisor (D17) also review submitted trip reports before they are published?

20. ~~Answered by D23 to D29~~ Live trip report and sitter. Was open: live mode basics (timeline position, quick logging, redose/interaction warnings, check-ins, SOS, auto-draft report); who can be a human sitter (any account vs earned/trained badge); private friend-sitter link; protections for people while live (no unsolicited private messages, sitters need an account, AI supervisor watches live chat).

21. ~~Answered by D33~~ Shulgin (D32): a dedicated Alexander and Ann Shulgin page (biography, timeline, rating scale explained, list of all compounds), a "Shulgin compounds" filter on the smart map, and which link target to use for his reports.
22. ~~Answered by D34~~ Translation (D30): show a "machine translated" label with a "view original" toggle? Right-to-left layout for Arabic and similar languages?

23. ~~Answered by D36~~ Release phases: build everything at once, or in phases?
24. ~~Answered by D37~~ Who are the human moderators that the AI supervisor escalates to?
25. ~~Answered by D39~~ Home page: what it shows.

26. ~~Answered by D41~~ "Start a report" button (D39): does it offer both "write about a past trip" and "go live now"?
27. ~~Answered by D42~~ Installable from the browser ("add to home screen", no app store) so it opens like an app and the harm reduction page and emergency steps work offline?
28. ~~Answered by D43~~ Which subreddits count as Reddit sources (proposed: r/DrugNerds, r/harmreduction, r/Psychonaut, r/microdosing, r/researchchemicals, plus one subreddit per substance)?

29. ~~Answered by D46~~ Forum: can users upvote questions and answers?

## Change history

- 2026-11-25: log created, no decisions yet.
- 2026-11-25: D1 added (Reddit section); Q4 and Q5 added.
- 2026-11-25: D2 (JSON) and D3 (endpoints, not prompts) added; Q6 and Q7 added.
- 2026-11-25: D4 (features 1 to 17) added; Q8 and Q9 added.
- 2026-11-25: Q10 added (trip reports web app).
- 2026-11-25: D5 added (trip report flow); Q10 narrowed.
- 2026-11-26: Hany started a new concept for the whole web app. D6, D7, D8 added; Q2 and Q10 narrowed; Q11 to Q14 added.
- 2026-11-26: D9 (map: family + effect), D10 (age range), D11 (Erowid-like display), D12 (Reddit links + summary) added; Q4 and Q11 answered; Q10 and Q14 narrowed.
- 2026-11-26: D13 (18+) added. D2, D3, D4 marked superseded per Hany. Q6, Q7, Q8 dropped; Q14 answered; Q15, Q16 added.
- 2026-11-26: D14 (general harm reduction page), D15 (warning intro per substance), D16 (questions forum) added; Q16 narrowed; Q17, Q18 added.
- 2026-11-26: D17 (AI supervisor), D18 (pen name or account), D19 (trip reports section order) added; Q17, Q18 answered; Q19 added.
- 2026-11-26: D20 (keywords), D21 (background fields), D22 (AI reviews trip reports) added; Q12, Q13, Q19 answered; Q20 added (live trip report and sitter).
- 2026-11-26: D23 (live visibility), D24 (AI companion always), D25 (human psychonaut sitters) added; Q20 narrowed.
- 2026-11-26: D26 (sitter accounts and badge), D27 (live protections), D28 (friend-sitter link), D29 (live mode basics) added; Q20 answered.
- 2026-11-26: D30 (languages), D31 (tools in forum section), D32 (Shulgin) added; Q3, Q16 answered; Q21, Q22 added.
- 2026-11-26: D33 (Shulgin details), D34 (translation display), D35 ("Questions & Tools" name) added; Q21, Q22 answered; Q23 to Q25 added.
- 2026-11-26: D36 (all at once), D37 (Hany + moderators), D38 (Reddit label), D39 (home page), D40 (web app, any device) added; Q1, Q2, Q23 to Q25 answered; Q26 to Q28 added.
- 2026-11-26: D41 (report button choices), D42 (installable, offline safety pages), D43 (subreddits) added; Q26 to Q28 answered.
- 2026-11-26: Design marked finished by Hany ("Let's go to the next step"). Remaining open items (data storage, Erowid permission) move to the build stage.
- 2026-11-26: D44 (substance map approved with fixes) and D45 (featured FAQs approved) added; Q29 added.
- 2026-11-26: D46 (forum upvotes) added; Q29 answered.
