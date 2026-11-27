/* Mazhar v2 shared code: data loading, glossary, emergency panel, on-device storage, interactions.
   Substance data: PsychonautWiki (CC BY-SA 4.0), via the Mazhar knowledge base. */
(function () {
"use strict";
const M = (window.M = {});
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
M.$ = $; M.$$ = $$; M.esc = esc;
M.param = (k) => new URLSearchParams(location.search).get(k);
M.reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ---------- backdrop (same as the map, calmer) ---------- */
M.backdrop = function () {
  const c = document.getElementById("bg"); if (!c) return;
  const x = c.getContext("2d");
  const blobs = [["#7b3cff", .9], ["#ff3fa4", .6], ["#00c2d1", .5], ["#ff8a00", .35], ["#2f5bff", .6]];
  let W, H;
  function size() { W = c.width = Math.max(160, innerWidth / 6 | 0); H = c.height = Math.max(160, innerHeight / 6 | 0); }
  function draw(t) {
    x.globalCompositeOperation = "source-over"; x.fillStyle = "#0b0716"; x.fillRect(0, 0, W, H);
    x.globalCompositeOperation = "lighter";
    blobs.forEach(([col, a], i) => {
      const px = W * (.5 + .42 * Math.sin(t * .00008 * (i + 2) + i * 1.7)), py = H * (.5 + .42 * Math.cos(t * .0001 * (i + 1.3) + i));
      const r = Math.max(W, H) * (.38 + .1 * Math.sin(t * .00015 + i));
      const g = x.createRadialGradient(px, py, 0, px, py, r);
      g.addColorStop(0, col + Math.round(a * .7 * 255).toString(16).padStart(2, "0")); g.addColorStop(1, col + "00");
      x.fillStyle = g; x.fillRect(0, 0, W, H);
    });
  }
  function loop(ts) { draw(ts + 5e4); if (!M.reduce && !document.hidden) requestAnimationFrame(loop); }
  size(); addEventListener("resize", () => { size(); draw(performance.now()); });
  document.addEventListener("visibilitychange", () => { if (!document.hidden && !M.reduce) requestAnimationFrame(loop); });
  M.reduce ? draw(1e5) : requestAnimationFrame(loop);
};

/* ---------- top bar + footer ---------- */
M.chrome = function (current) {
  const top = document.createElement("header");
  top.className = "topbar";
  top.innerHTML = `<div class="wrap">
    <a class="logo" href="./"><svg viewBox="0 0 52 52" aria-hidden="true"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff8ad8"/><stop offset=".5" stop-color="#c9a7ff"/><stop offset="1" stop-color="#7fe7ff"/></linearGradient></defs><circle cx="26" cy="26" r="23" fill="none" stroke="url(#lg)" stroke-width="3"/><circle cx="26" cy="26" r="14" fill="none" stroke="url(#lg)" stroke-width="2.5" opacity=".7"/><circle cx="26" cy="26" r="6" fill="url(#lg)"/></svg><span>Mazhar</span></a>
    <nav class="nav" aria-label="Main">
      <a href="./" ${current === "map" ? 'aria-current="page"' : ""}>Map</a>
      <a href="report.html" ${current === "report" ? 'aria-current="page"' : ""}>Write a report</a>
      <a href="tools.html" ${current === "tools" ? 'aria-current="page"' : ""}>Tools</a>
    </nav>
    <button class="sos" id="sosbtn" aria-haspopup="dialog">SOS</button>
  </div>`;
  document.body.prepend(top);
  const f = document.createElement("footer");
  f.className = "site wrap";
  f.innerHTML = `<div class="card"><div><b>Information, not advice.</b> Mazhar shows what is reported about substances. It can't tell you what is safe for you. If someone is in danger, call your local emergency number.</div>
  <div>Substance, effect and safety data from <a href="https://psychonautwiki.org" target="_blank" rel="noopener">PsychonautWiki</a>, licensed <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>. Adaptations by the Mazhar project, shared under the same licence.</div></div>`;
  document.body.append(f);
  $("#sosbtn").onclick = () => M.sos();
};

/* ---------- data ---------- */
const FAMC = { Psychedelics: "#9887ef", Stimulants: "#e76624", Depressants: "#338ced", Opioids: "#eb6263", Dissociatives: "#00a888", Cannabinoids: "#0aac23", Entactogens: "#e24d8b", Nootropics: "#d28e05" };
M.famColor = (f) => FAMC[f] || "#8a8fa3";
// Approved map fixes (design log D44), same as the map page
const UNCL = { "Flunitrazepam": ["Depressants", "Benzodiazepine"], "Kava": ["Depressants", "Kavalactone"], "1,3-Butanediol": ["Depressants", "Alkanediol"], "Trihexyphenidyl": ["Deliriants", "Anticholinergic"], "Perazin": ["Prescription medicines", "Phenothiazine"], "Cocoa": ["Stimulants", "Xanthine"], "AET": ["Entactogens", "Tryptamine"], "Blue lotus": ["Other", "Chemical class not given"], "Grayanotoxin": ["Other", "Chemical class not given"], "Inhalants": ["Other", "Chemical class not given"], "Tryptamine (compound)": ["Other", "Arylethylamine"] };
const MERGE = { "Substituted amphetamines": "Substituted amphetamine", "Amphetamine": "Substituted amphetamine", "Arylcyclohexylamines": "Arylcyclohexylamine", "Indole alkaloids": "Indole alkaloid", "Substituted cathinone": "Cathinone", "Substituted phenethylamine": "Phenethylamine", "substituted piperazine": "Substituted piperazine", "1": "Carbamate", "cholinergic": "Choline ester" };
const RX = new Set(["Antipsychotics", "Antidepressants", "Anxiolytics"]);

const cache = {};
M.json = (p) => (cache[p] ||= fetch(p).then((r) => { if (!r.ok) throw new Error(p); return r.json(); }));

M.load = async function () {
  if (M.SUBS) return;
  const [map, det, eff] = await Promise.all([M.json("../design/substance-map/substance-map-data.json"), M.json("data/substances.json"), M.json("data/effects.json")]);
  const detail = new Map(det.data.map((d) => [d.n, d]));
  M.EFF = eff.data.map((e, i) => ({ ...e, i }));
  M.SUBS = [];
  for (const s of map.s) {
    const iss = s.iss || [];
    if (iss.includes("preparations")) continue;
    let f = s.f, c = s.c || "Chemical class not given";
    if (iss.includes("thc-in-stimulants")) { f = "Cannabinoids"; c = "Cannabinoid"; }
    if (iss.includes("opioids-in-depressants")) f = "Opioids";
    if (UNCL[s.n]) [f, c] = UNCL[s.n];
    if (f === "Unclassified") f = "Other";
    if (RX.has(f)) f = "Prescription medicines";
    if (MERGE[c]) c = MERGE[c];
    const also = [...new Set((s.also || []).map((a) => (RX.has(a) ? "Prescription medicines" : a)).filter((a) => a !== f))];
    const d = detail.get(s.n) || {};
    M.SUBS.push({ n: s.n, f, c, also, u: s.u, sh: s.sh || [], hasDose: !!s.d, e: s.e || [], aka: d.aka || [], common: d.common || "", routes: d.routes || {}, ix: d.ix || [], intro: d.intro || "", dep: d.dep || "", key: s.n.toLowerCase() });
  }
  M.SUBS.sort((a, b) => a.n.localeCompare(b.n));
  M.byName = new Map(M.SUBS.map((s) => [s.n, s]));
  // search index: names, aliases, common names
  M.SEARCH = [];
  for (const s of M.SUBS) {
    const names = new Set([s.n, ...s.aka, ...s.common.split(",").map((x) => x.trim()).filter(Boolean)]);
    for (const n of names) M.SEARCH.push({ k: n.toLowerCase(), label: n, s });
  }
};
M.find = function (q) {
  if (!q) return null;
  const k = q.trim().toLowerCase();
  return (M.SEARCH.find((x) => x.k === k) || {}).s || null;
};
M.search = function (q, n = 8) {
  const k = q.trim().toLowerCase(); if (!k) return [];
  const seen = new Set(), out = [];
  const rank = (x) => (x.k === k ? 0 : x.k.startsWith(k) ? 1 : 2);
  for (const x of M.SEARCH.filter((x) => x.k.includes(k)).sort((a, b) => rank(a) - rank(b) || a.k.length - b.k.length)) {
    if (seen.has(x.s.n)) continue; seen.add(x.s.n); out.push(x); if (out.length >= n) break;
  }
  return out;
};
/* Substance search box with suggestions. onPick(substance) */
M.suggestBox = function (input, onPick) {
  const wrap = input.parentElement; wrap.classList.add("suggest");
  const list = document.createElement("div"); list.className = "list"; list.hidden = true; list.setAttribute("role", "listbox"); wrap.append(list);
  let items = [], on = -1;
  function render() {
    items = M.search(input.value);
    on = items.length ? 0 : -1;
    list.innerHTML = items.map((x, i) => `<button type="button" role="option" data-i="${i}" class="${i === on ? "on" : ""}">${esc(x.s.n)}${x.label !== x.s.n ? `<small>also called ${esc(x.label)}</small>` : ""}<small>${esc(x.s.f)}</small></button>`).join("");
    list.hidden = !items.length;
  }
  function pick(i) { const x = items[i]; if (!x) return; list.hidden = true; input.value = x.s.n; onPick(x.s); }
  input.addEventListener("input", render);
  input.addEventListener("keydown", (e) => {
    if (list.hidden) return;
    if (e.key === "ArrowDown") { on = Math.min(items.length - 1, on + 1); e.preventDefault(); }
    else if (e.key === "ArrowUp") { on = Math.max(0, on - 1); e.preventDefault(); }
    else if (e.key === "Enter") { e.preventDefault(); pick(on); return; }
    else if (e.key === "Escape") { list.hidden = true; return; }
    else return;
    $$("button", list).forEach((b, i) => b.classList.toggle("on", i === on));
  });
  list.addEventListener("mousedown", (e) => { const b = e.target.closest("button"); if (b) { e.preventDefault(); pick(+b.dataset.i); } });
  input.addEventListener("blur", () => setTimeout(() => (list.hidden = true), 150));
};

/* ---------- time ranges & phases ---------- */
// "45 - 90 minutes" -> [45, 90] (minutes). "1.5 - 2.5 hours" -> [90,150]. "150 mg +" style not relevant here.
M.range = function (v) {
  if (!v) return null;
  const s = String(v).toLowerCase().replace(/–/g, "-");
  const nums = (s.match(/\d+(?:\.\d+)?/g) || []).map(Number);
  if (!nums.length) return null;
  const mult = /day/.test(s) ? 1440 : /hour|hr/.test(s) ? 60 : /second/.test(s) ? 1 / 60 : 1;
  const lo = nums[0] * mult, hi = (nums[1] ?? nums[0]) * mult;
  return [lo, hi];
};
M.ROUTE_NAMES = { oral: "Oral", sublingual: "Sublingual", buccal: "Buccal", insufflated: "Insufflated (snorted)", rectal: "Rectal", transdermal: "Transdermal", subcutaneous: "Subcutaneous", intramuscular: "Intramuscular", intravenous: "Intravenous", smoked: "Smoked", vaporized: "Vaporized", inhaled: "Inhaled", intranasal: "Intranasal" };
M.routeName = (r) => M.ROUTE_NAMES[r] || r.charAt(0).toUpperCase() + r.slice(1);
M.PHASES = [["onset", "Onset", "p-onset"], ["comeup", "Come-up", "p-comeup"], ["peak", "Peak", "p-peak"], ["offset", "Comedown", "p-offset"], ["aftereffects", "After-effects", "p-after"]];
M.PHASE_COL = { onset: "#9fb6ff", comeup: "#c9a7ff", peak: "#ff8ad8", offset: "#ffd36b", aftereffects: "#8a8fa3" };
/* Mid-point phase boundaries in minutes for a route. Returns [{k,label,from,to}] or null. */
M.phaseSpans = function (r) {
  if (!r) return null;
  let t = 0; const out = [];
  for (const [k, label] of M.PHASES) {
    const g = M.range(r[k]); if (!g) continue;
    const mid = (g[0] + g[1]) / 2;
    out.push({ k, label, from: t, to: t + mid }); t += mid;
  }
  return out.length >= 2 ? out : null;
};
M.phaseAt = function (r, minutes) {
  const sp = M.phaseSpans(r); if (!sp || minutes == null) return null;
  if (minutes < 0) return null;
  for (const p of sp) if (minutes < p.to) return p;
  return { k: "after", label: "After the expected end", from: sp[sp.length - 1].to, to: Infinity };
};
M.fmtMin = function (m) {
  if (m == null || isNaN(m)) return "";
  const h = Math.floor(m / 60), mm = Math.round(m % 60);
  return `T+${h}:${String(mm).padStart(2, "0")}`;
};
M.timelineBar = function (r) {
  const sp = M.phaseSpans(r); if (!sp) return "";
  const total = sp[sp.length - 1].to;
  return `<div class="tl" role="img" aria-label="Timeline: ${sp.map((p) => `${p.label} ${esc(r[p.k])}`).join(", ")}">${sp.map((p) => `<span class="${M.PHASES.find((x) => x[0] === p.k)[2]}" style="flex:${(p.to - p.from) / total}" title="${esc(p.label)}: ${esc(r[p.k])}">${(p.to - p.from) / total > .1 ? esc(p.label) : ""}</span>`).join("")}</div><p class="small faint">Bar widths use the middle of each range. Real timing varies with dose, body and setting.</p>`;
};

/* ---------- glossary (terms explained along the way, D5.4) ---------- */
M.GLOSS = {
  "onset": ["Onset", "The time between taking a substance and first feeling it."],
  "comeup": ["Come-up", "The period when effects are rising toward their strongest. It can bring nervousness, nausea or restlessness before things settle."],
  "peak": ["Peak", "The time when effects are at their strongest."],
  "offset": ["Comedown (offset)", "The time when effects fade from their peak back toward sober."],
  "aftereffects": ["After-effects", "What lingers after the main effects end: tiredness, low mood, trouble sleeping, or an 'afterglow'. Also called the hangover or afterglow."],
  "duration": ["Total duration", "How long the main effects last from onset to the end of the comedown."],
  "threshold": ["Threshold dose", "The smallest amount that produces a noticeable effect."],
  "light": ["Light dose", "Clear but manageable effects. A sensible first dose with anything new."],
  "common": ["Common dose", "The range most people take for the full effect."],
  "strong": ["Strong dose", "Intense effects with much higher risk of a difficult experience or side effects."],
  "heavy": ["Heavy dose", "Overwhelming effects and a high risk of harm. Not recommended."],
  "redose": ["Redose", "Taking more after the first dose. Redosing before the first dose has peaked is a common cause of overwhelming or dangerous experiences."],
  "tolerance": ["Tolerance", "When the same dose has less effect because you took it (or something similar) recently. Tolerance to effects can build faster than tolerance to harms."],
  "set": ["Set", "Your state of mind and body going in: mood, expectations, stress, health."],
  "setting": ["Setting", "Where you are and who you're with."],
  "sitter": ["Trip sitter", "A sober, trusted person who stays with you, keeps you safe, and helps if things get hard."],
  "route": ["Route of administration", "How a substance is taken: by mouth (oral), under the tongue (sublingual), snorted (insufflated), smoked, and so on. The route changes the dose, the speed and the length of effects."],
  "bioavailability": ["Bioavailability", "How much of a dose actually reaches your bloodstream by that route."],
  "tplus": ["T+ time", "Time since your first dose. T+1:30 means one and a half hours after the first dose."],
  "intensity": ["Intensity", "How strong an effect felt, from 1 (barely there) to 4 (overwhelming)."],
};
M.term = (key, label) => `<button type="button" class="term" data-term="${key}">${esc(label || M.GLOSS[key][0])}</button>`;
let pop;
function closePop() { pop?.remove(); pop = null; }
M.popover = function (anchor, html) {
  closePop();
  pop = document.createElement("div"); pop.className = "pop"; pop.setAttribute("role", "dialog"); pop.innerHTML = html;
  document.body.append(pop);
  const r = anchor.getBoundingClientRect();
  const w = pop.offsetWidth, h = pop.offsetHeight;
  let x = Math.min(Math.max(8, r.left), innerWidth - w - 8), y = r.bottom + 8;
  if (y + h > innerHeight - 8) y = Math.max(8, r.top - h - 8);
  pop.style.left = x + "px"; pop.style.top = y + "px";
};
document.addEventListener("click", (e) => {
  const t = e.target.closest(".term");
  if (t) {
    e.preventDefault();
    if (t.dataset.term) { const [n, d] = M.GLOSS[t.dataset.term]; M.popover(t, `<b>${esc(n)}</b>${esc(d)}`); }
    else if (t.dataset.effect !== undefined) { const ef = M.EFF[+t.dataset.effect]; M.popover(t, `<b>${esc(ef.n)}</b>${esc(ef.d || "No description yet.")}<br><a href="${esc(ef.u)}" target="_blank" rel="noopener">Read more on PsychonautWiki ↗</a>`); }
    return;
  }
  if (pop && !e.target.closest(".pop")) closePop();
});
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closePop(); });
addEventListener("scroll", closePop, { passive: true });
M.effTerm = (i) => `<button type="button" class="term" data-effect="${i}">${esc(M.EFF[i].n)}</button>`;

/* ---------- emergency (SOS) ---------- */
const EMERGENCY = { US: "911", CA: "911", MX: "911", GB: "999", IE: "112", AU: "000", NZ: "111", EG: "123", SA: "997", AE: "998", QA: "999", KW: "112", JO: "911", LB: "140", MA: "15", TN: "190", DZ: "14", IN: "112", PK: "1122", JP: "119", KR: "119", CN: "120", HK: "999", SG: "995", BR: "192", AR: "107", CO: "123", ZA: "10177", NG: "112", KE: "999", IR: "115", IL: "101", TR: "112" };
M.emergencyNumber = function () {
  try { const s = localStorage.getItem("mazhar.emergency"); if (s) return s; } catch (e) {}
  const langs = navigator.languages || [navigator.language || ""];
  for (const l of langs) { const m = /[-_]([A-Za-z]{2})\b/.exec(l); if (m && EMERGENCY[m[1].toUpperCase()]) return EMERGENCY[m[1].toUpperCase()]; }
  return "112";
};
M.OVERDOSE = {
  Opioids: "Very slow, shallow or no breathing, sometimes a snoring or gurgling sound. Also unresponsiveness, blue or grey lips and fingertips, pinpoint pupils and a slow pulse. Naloxone reverses an opioid overdose. Give it if you have it, and still call for help.",
  Stimulants: "Racing or irregular heartbeat, overheating, extreme anxiety or panic, paranoia, shaking, confusion, seizures.",
  Entactogens: "Racing or irregular heartbeat, overheating, extreme anxiety or panic, paranoia, shaking, confusion, seizures.",
  Depressants: "Confusion, vomiting, slow breathing, cold skin, being unable to stand, passing out.",
};
M.OVERDOSE_LABEL = { Opioids: "Opioids", Stimulants: "Stimulants", Entactogens: "Stimulants (MDMA-like substances share these signs)", Depressants: "Alcohol and other depressants" };
M.RECOVERY = ["Kneel beside them while they lie on their back.", "Put the arm nearest you at a right angle to their body, palm up.", "Tuck their other hand under their cheek, back of the hand against the face.", "Bend the knee farthest from you to a right angle.", "Roll them towards you onto their side by pulling that knee.", "Tilt the head back gently and lift the chin to open the airway.", "Stay with them and keep checking that they are breathing."];
M.sos = function () {
  let m = $("#sosmodal");
  if (!m) { m = document.createElement("div"); m.id = "sosmodal"; m.className = "modal"; m.setAttribute("role", "dialog"); m.setAttribute("aria-modal", "true"); m.setAttribute("aria-labelledby", "sosh"); document.body.append(m); }
  const num = M.emergencyNumber();
  m.innerHTML = `<div class="box sos-box"><button class="x" aria-label="Close">✕</button>
    <h2 id="sosh">Emergency</h2>
    <p>If you are unsure whether someone is overdosing, call emergency services now. Tell them what was taken and roughly when.</p>
    <a class="callbig" href="tel:${esc(num)}">Call ${esc(num)}</a>
    <p class="small muted">Number guessed from your device language. <button class="term" id="sosnum">Change it</button>. 112 works from most mobile phones in many countries.</p>
    <h3>Signs of overdose</h3>
    ${Object.keys(M.OVERDOSE).filter((k) => k !== "Entactogens").map((k) => `<p><b>${esc(M.OVERDOSE_LABEL[k])}:</b> ${esc(M.OVERDOSE[k])}</p>`).join("")}
    <p>While you wait: stay with the person, keep them cool if overheating, and if they are unconscious but breathing, put them in the recovery position.</p>
    <h3>Recovery position</h3>
    <ol>${M.RECOVERY.map((s) => `<li>${esc(s)}</li>`).join("")}</ol>
    <p class="small faint">From Mazhar's featured answers, adapted from PsychonautWiki (Substance overdose, Recovery position), CC BY-SA 4.0.</p></div>`;
  m.hidden = false;
  const close = () => { m.hidden = true; };
  $(".x", m).onclick = close; $(".x", m).focus();
  m.onclick = (e) => { if (e.target === m) close(); };
  m.onkeydown = (e) => { if (e.key === "Escape") close(); };
  $("#sosnum", m).onclick = () => {
    const v = prompt("Your local emergency number", num);
    if (v && /^[0-9+ ]{2,8}$/.test(v.trim())) { try { localStorage.setItem("mazhar.emergency", v.trim()); } catch (e) {} M.sos(); }
  };
};
/* Words that suggest an emergency happening now (D17.3). Shown at once, without waiting for replies. */
M.EMERGENCY_RX = /\b(not breathing|can'?t breathe|cannot breathe|stopped breathing|won'?t wake|not waking|unconscious|unresponsive|passed out|overdos(e|ing)|od'?ing|seizure|fitting|convuls|turning blue|blue lips|chest pain|heart (is )?racing|collapsed|choking|dying|going to die|suicid|kill (my|him|her)self)\b/i;

/* ---------- screening before posting (client-side pre-check; the AI supervisor, D17, does the real review) ---------- */
M.screen = function (text) {
  const issues = [];
  if (/\b(sell|selling|buy|buying|vendor|plug|dealer|for sale|ship(ping)?|dm me|telegram|wickr|whatsapp|signal me|price per|\$\d+ ?(a|per) ?g)\b/i.test(text)) issues.push("It looks like buying or selling. That isn't allowed.");
  if (/[\w.+-]+@[\w-]+\.[\w.]+/.test(text) || /(\+?\d[\d\s().-]{7,}\d)/.test(text) || /(^|\s)@\w{3,}/.test(text) || /\b(instagram|snapchat|facebook|tiktok|discord)\b/i.test(text)) issues.push("Remove contact details (email, phone number, social handles). They put you at risk.");
  if (/\b(i'?m|i am|im)\s*(1[0-7]|[0-9])\b(?!\s*(mg|ug|µg|g|ml|hours?|h|min))/i.test(text) || /\b(1[0-7]|[0-9]) ?(years? old|yo|y\/o)\b/i.test(text) || /\b(high school|middle school|my parents won'?t let)\b/i.test(text)) issues.push("Mazhar is for adults (18+).");
  return issues;
};

/* ---------- on-device storage. A backend can replace these functions later. ---------- */
const LS = {
  get(k, d) { try { const v = localStorage.getItem("mazhar." + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem("mazhar." + k, JSON.stringify(v)); return true; } catch (e) { return false; } },
};
M.LS = LS;
M.uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
M.store = {
  reports() { return LS.get("reports", []); },
  report(id) { return this.reports().find((r) => r.id === id) || null; },
  saveReport(r) { const all = this.reports().filter((x) => x.id !== r.id); r.updated = new Date().toISOString(); all.unshift(r); return LS.set("reports", all); },
  deleteReport(id) { return LS.set("reports", this.reports().filter((x) => x.id !== id)); },
  questions() { return LS.get("questions", []); },
  saveQuestion(q) { const all = this.questions().filter((x) => x.id !== q.id); all.unshift(q); return LS.set("questions", all); },
  deleteQuestion(id) { return LS.set("questions", this.questions().filter((x) => x.id !== id)); },
  votes() { return LS.get("votes", {}); },
  vote(id, v) { const all = this.votes(); if (all[id] === v) delete all[id]; else all[id] = v; LS.set("votes", all); return all[id]; },
};

/* ---------- interactions ---------- */
// Medications and other items that appear in PsychonautWiki interaction lists but aren't substances on the map.
M.MEDS = ["SSRIs", "SNRIs", "MAOIs", "Tricyclic antidepressants", "Lithium", "Bupropion", "Trazodone", "Antipsychotics", "Antihistamines", "Protease inhibitors (e.g. ritonavir)", "Hormonal birth control", "Anticoagulants", "Grapefruit", "St John's wort"];
const norm = (s) => String(s).toLowerCase().replace(/^[αa]-?(?=mt\b)/, "a").replace(/[^a-z0-9]+/g, "");
function famOf(s) { return [s.f, ...s.also]; }
function pcHas(s, word) { return famOf(s).some((f) => f.toLowerCase().startsWith(word)) ; }
/* Does an interaction target (as written on a PW page) cover item x? x = {kind:"sub", s} | {kind:"med", n} */
M.covers = function (target, x) {
  const t = norm(target), raw = String(target);
  if (x.kind === "med") {
    const n = norm(x.n);
    if (t === n || n.startsWith(t) || t.startsWith(n.slice(0, 5))) return true;
    if (/selectiveserotoninreuptake/.test(t) && n === "ssris") return true;
    if (t === "protease inhibitors".replace(/ /g, "") && n.startsWith("proteaseinhibitors")) return true;
    if (t === "ritonavir" && n.startsWith("proteaseinhibitors")) return true;
    if (t === "antidepressants" && /ssri|snri|maoi|tricyclic|bupropion|trazodone/.test(n)) return true;
    if ((t === "maois" || t === "harmalaalkaloids") && n === "maois") return true;
    if (t === "serotonergic" && /ssri|snri|maoi/.test(n)) return true;
    return false;
  }
  const s = x.s;
  const names = [s.n, ...s.aka].map(norm);
  if (names.includes(t)) return true;
  if (t.endsWith("s") && names.includes(t.slice(0, -1))) return true;
  // families and classes
  const fam = { stimulants: "stimulants", depressants: "depressants", opioids: "opioids", dissociatives: "dissociatives", psychedelics: "psychedelics", psychedelic: "psychedelics", deliriants: "deliriants", cannabinoids: "cannabinoids", entactogens: "entactogens" }[t];
  if (fam) { if (pcHas(s, fam)) return true; if (fam === "depressants" && pcHas(s, "opioids")) return true; }
  const cc = s.c.toLowerCase();
  if (t === "benzodiazepines" && /benzodiazepine/.test(cc)) return true;
  if ((t === "amphetamines" || t === "amphetamine") && /amphetamine/.test(cc) && pcHas(s, "stimulants")) return true;
  if (t === "barbiturates" && /barbiturate/.test(cc)) return true;
  if ((t === "maois" || t === "harmalaalkaloids") && (/maoi|harmal|β-carboline|beta-carboline/.test(cc) || /harmal|harmine|ayahuasca|syrian rue/i.test(s.n))) return true;
  if (t === "cannabis" && (s.n === "Cannabis" || /tetrahydrocannabinol/i.test(s.n))) return true;
  if (t === "mushrooms" && /psilocybin mushrooms/i.test(s.n)) return true;
  if (t === "nitrous" && /nitrous/i.test(s.n)) return true;
  if (t === "dph" && s.n === "Diphenhydramine") return true;
  // wildcard series names: DOx, 2C-x, 2C-T-x, 25x-NBOMe, 5-MeO-xxT
  const pats = { DOx: /^DO[A-Z]{1,4}$/, "2C-x": /^2C-[A-Z]/, "2C-T-x": /^2C-T(-\d+)?$/, "25x-NBOMe": /^25[A-Z]-NBOMe$/, "5-MeO-xxT": /^5-MeO-[A-Za-z]{1,4}T$/ };
  if (pats[raw] && pats[raw].test(s.n)) return true;
  if ((t === "amt" || t === "αmt") && /^(αMT|AMT|α-Methyltryptamine)$/i.test(s.n)) return true;
  return false;
};
const SEV_RANK = { dangerous: 4, unsafe: 3, uncertain: 2, caution: 1 };
M.SEV_LABEL = { dangerous: "Dangerous", unsafe: "Unsafe", uncertain: "Caution", caution: "Caution", none: "Nothing listed", general: "General rule" };
M.SEV_TEXT = {
  dangerous: "This combination can be life-threatening. Don't mix these.",
  unsafe: "This combination carries real risk. Avoid it, or take extra care.",
  uncertain: "Effects can be unpredictable or stronger. Take extra care and use lower doses.",
  caution: "PsychonautWiki notes something to know about this combination.",
};
/* Returns {sev, items:[{from, target, sev, why}], general:[...]} for a pair. */
M.pair = function (a, b) {
  const found = [];
  const add = (src, other) => {
    if (src.kind !== "sub") return;
    for (const ix of src.s.ix) if (M.covers(ix.with, other)) found.push({ from: src.s.n, target: ix.with, sev: ix.sev, why: ix.why });
  };
  add(a, b); add(b, a);
  // general rules (not from a specific page; from the Dangerous combinations page and featured answer 4)
  const general = [];
  const isDep = (x) => x.kind === "sub" && (pcHas(x.s, "depressants") || pcHas(x.s, "opioids"));
  const isSero = (x) => x.kind === "sub" ? /mdma|mda|mde|tramadol|dxm|dextromethorphan|amphetamine|cocaine/i.test(x.s.n) : /ssri|snri|maoi|lithium|st john/i.test(x.n);
  const isMaoi = (x) => x.kind === "med" ? /maoi/i.test(x.n) : M.covers("MAOIs", x);
  if (isDep(a) && isDep(b)) general.push({ sev: "dangerous", why: "Depressants together (alcohol, benzodiazepines, opioids, GHB/GBL, barbiturates): their effects multiply rather than add up, which can stop breathing. Choking on vomit while unconscious is a common cause of death." });
  if ((isSero(a) && isSero(b)) || (isMaoi(a) && (isSero(b) || (b.kind === "sub" && pcHas(b.s, "stimulants")))) || (isMaoi(b) && (isSero(a) || (a.kind === "sub" && pcHas(a.s, "stimulants"))))) general.push({ sev: "dangerous", why: "Serotonergic substances together, or with antidepressants (MAOIs, SSRIs, SNRIs), can cause serotonin syndrome, a medical emergency." });
  const isStim = (x) => x.kind === "sub" && pcHas(x.s, "stimulants");
  if ((isStim(a) && isDep(b)) || (isStim(b) && isDep(a))) general.push({ sev: "unsafe", why: "Stimulants can hide how drunk or sedated you are, so people take more than they can handle once the stimulant wears off." });
  if (isStim(a) && isStim(b)) general.push({ sev: "unsafe", why: "Stimulants together strain the heart and raise body temperature, blood pressure and anxiety." });
  const all = [...found.map((f) => f.sev), ...general.map((g) => g.sev)];
  const sev = all.sort((x, y) => SEV_RANK[y] - SEV_RANK[x])[0] || "none";
  return { sev, items: found, general };
};
M.itemName = (x) => (x.kind === "sub" ? x.s.n : x.n);

M.toast = function (msg) {
  const t = document.createElement("div"); t.className = "toast"; t.setAttribute("role", "status"); t.textContent = msg;
  document.body.append(t); setTimeout(() => t.remove(), 2600);
};
M.WARN_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="#ffb547" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18h.01"/></svg>`;
M.DANGER_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="#ff6b6b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16.5h.01"/></svg>`;
M.INFO_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="#7fe7ff" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/></svg>`;

/* Dose table for one substance */
M.doseTable = function (s) {
  const routes = Object.entries(s.routes).filter(([, r]) => r.common || r.light || r.threshold || r.strong || r.duration || M.phaseSpans(r));
  if (!routes.length || !routes.some(([, r]) => r.common || r.light || r.threshold)) return `<div class="alert warn">${M.WARN_ICON}<div><b>No reliable dose data yet.</b> Treat any amount as an unknown risk. Start low, don't mix, and don't use alone.</div></div>`;
  const cols = [["threshold"], ["light"], ["common"], ["strong"], ["heavy"]];
  return routes.map(([rn, r]) => `<h3>${M.term("route", M.routeName(rn))}${r.bioavailability ? ` <span class="small faint">· ${M.term("bioavailability", "bioavailability")} ${esc(r.bioavailability)}</span>` : ""}</h3>
    <div class="tbl-wrap"><table class="tbl"><thead><tr>${cols.map(([k]) => `<th>${M.term(k, M.GLOSS[k][0].replace(" dose", ""))}</th>`).join("")}</tr></thead>
    <tbody><tr>${cols.map(([k]) => `<td>${esc(r[k] || "–")}</td>`).join("")}</tr></tbody></table></div>
    ${r.microdose ? `<p class="small muted">Microdose: ${esc(r.microdose)}</p>` : ""}
    ${M.phaseSpans(r) ? M.timelineBar(r) : ""}
    <div class="tbl-wrap"><table class="tbl"><tbody>${[...M.PHASES.map((p) => p[0]), "duration"].filter((k) => r[k]).map((k) => `<tr><th>${M.term(k)}</th><td>${esc(r[k])}</td></tr>`).join("")}</tbody></table></div>`).join("");
};
M.ixList = function (s, limit) {
  if (!s.ix.length) return `<p class="muted">PsychonautWiki lists no specific interactions for ${esc(s.n)}. That does not mean any combination is safe. Use the interaction checker for general rules.</p>`;
  const sorted = [...s.ix].sort((a, b) => SEV_RANK[b.sev] - SEV_RANK[a.sev]);
  const list = limit ? sorted.slice(0, limit) : sorted;
  return `<div class="stack" style="gap:8px">${list.map((ix) => `<div class="row" style="align-items:flex-start;flex-wrap:nowrap"><span class="sev ${ix.sev}">${M.SEV_LABEL[ix.sev]}</span><div><b>${esc(ix.with)}</b>${ix.why ? `<div class="small muted">${esc(ix.why)}</div>` : ""}</div></div>`).join("")}</div>${limit && sorted.length > limit ? `<p class="small muted" style="margin-top:8px">${sorted.length - limit} more on the Info tab.</p>` : ""}`;
};
})();
