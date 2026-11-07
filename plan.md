# Clinic.exe — Hackathon Build Plan

NatHacks 2026 · ValueMed problem · as of 2026-11-06

## The calls

Build one thing that works end to end: a doctor describes their clinic, the AI returns a room-by-room equipment list, they edit it, and they submit a quote request. Everything else is cut.

**AI provider: build against both, start on Gemini free.** Write one Python function, `generate_plan(intake)`, that hides which API is behind it. Gemini's free tier costs nothing and is fine for building. Dev Report #3 lists the Claude API as the key resource, so if anyone can put $5–10 of credit on an Anthropic account, switch to it for the demo — a full weekend of testing costs a few dollars at most.

- Gemini free-tier limits are low and no longer published per model; check your project's limits in Google AI Studio. Rate limits apply per project, not per key, so extra keys don't help.
- Free-tier inputs may be used by Google to improve its models. Fine for a demo with made-up clinics; never put real patient or client data through it.
- Put the model name in `.env` (`MODEL=...`). Don't hard-code it; pick the current Flash model from the Gemini docs.

**Stack: Flask + plain HTML/CSS/JS.** No React, no database, no login. One Python server, two or three HTML pages, a JSON file for the catalog. Four people can all understand it by Saturday morning.

**Prices come from a catalog, not the AI.** If the model invents prices, a judge from ValueMed will spot it in seconds. The AI only picks item IDs and quantities from a product catalog JSON you write; Python looks up names and prices. This also fixes the weakest score in Dev Report #2 (Maintainability = 1): ValueMed updates a JSON file, not a prompt.

**Truth check:** the concept-screening score said the AI assistant wins on ease of use. That only holds if the output is reliable. A demo where the AI returns broken JSON or a $40 exam table loses to a boring checklist. Spend effort on reliability, not features.

## What the demo does

Three screens, one flow. If a feature is not on this list, it is not built this weekend.

| Screen | What the user does | What it shows |
| --- | --- | --- |
| 1. Intake | Picks clinic type, rooms, services, budget tier; adds a free-text description | A short form, one page |
| 2. Plan | Reviews the AI's list, changes quantities, removes items, adds from catalog | Items grouped by room, each with a one-line reason, a subtotal per room and an estimated total |
| 3. Quote request | Enters name, email, clinic name, opening date; clicks Submit | A confirmation with a reference number; the request saved as a JSON file a sales rep could open |

**Cut — do not start these:**

- Maintenance reminders, irregularity reporting, "upload your old list" (Dev Report #1 add-ons)
- Team collaboration, accounts, login, a database
- Clinic visualization
- Real email sending (show the saved request instead; say "in production this emails ValueMed")
- Chat-style back-and-forth with the AI. One request in, one structured plan out.

**Stretch, only after Saturday's checkpoint passes:** a "Why this item?" tooltip, a printable/PDF view of the plan, a second AI call that flags missing essentials ("no sharps container in exam room 2").

## Architecture and the contract

Agree on the JSON below tonight, before anyone writes real code. Once it is fixed, frontend and backend can build in parallel against fake data and plug together Saturday morning without a fight.

**Request flow** — the AI picks items; Python owns the prices:

```
Intake page ──► POST /api/plan ──► ai.py ──► Gemini / Claude
(doctor fills     (Flask, app.py)   (prompt +    (returns IDs + qty)
 form)                               catalog IDs)        │
                                                         ▼ AI reply
Saved quote ◄── POST /api/quote ◄── Plan page ◄──── Validate
(quotes/          (Flask, app.py)   (edit, totals    (prices from catalog;
 ref-id.json)                        live)            invalid twice → serve
                                                      mock_plan.json)
```

The model never sees prices and never writes final totals; anything it returns passes through catalog validation before the plan page shows it.

**Repo layout** (one GitHub repo, everyone pushes to branches, one person merges):

```
clinic-exe/
  app.py              # Flask routes
  ai.py               # generate_plan(): prompt, API call, JSON parsing, retry
  catalog.json        # ~40-60 products: id, name, category, price, rooms it fits
  mock_plan.json      # a hand-written perfect response, used until the AI works
  quotes/             # submitted quote requests saved here
  templates/
    index.html        # intake form
    plan.html         # editable plan
    submitted.html    # confirmation
  static/
    style.css
    plan.js           # edit quantities, recalc totals, submit
  .env                # API keys + MODEL. NEVER committed
  .gitignore          # includes .env
  requirements.txt    # flask, python-dotenv, google-genai and/or anthropic
```

**Endpoints:**

| Method | Route | Does |
| --- | --- | --- |
| GET | `/` | Intake form |
| POST | `/api/plan` | Takes intake JSON, returns plan JSON |
| GET | `/api/catalog` | Full catalog, for the "add item" picker |
| POST | `/api/quote` | Takes the edited plan + contact info, saves to `quotes/`, returns a reference number |

**Request to `/api/plan`:**

```json
{
  "clinic_type": "family_practice",
  "exam_rooms": 3,
  "procedure_rooms": 1,
  "services": ["pap_tests", "ecg", "minor_procedures"],
  "budget": "mid",
  "notes": "Opening in a strip mall, mostly pediatric patients"
}
```

**Response from `/api/plan`** (the AI produces only `item_id`, `qty`, `reason`; Python fills `name` and `unit_price` from `catalog.json` and drops any ID that is not in the catalog):

```json
{
  "rooms": [
    {
      "room": "Exam Room 1",
      "items": [
        {"item_id": "EXAM-TBL-01", "name": "Power exam table", "qty": 1, "unit_price": 4200, "reason": "Core exam surface"}
      ]
    }
  ],
  "total_estimate": 4200,
  "warnings": ["Budget tier is low for 3 exam rooms"]
}
```

**How `ai.py` must work** — this is where demos die, so follow it exactly:

1. Build the prompt: system rules + the full catalog (IDs, names, categories only — no prices) + the intake.
2. Ask for JSON only. Use the API's structured-output / JSON mode if available.
3. Parse with `json.loads`. On failure, retry once with "Your last reply was not valid JSON. Return only JSON."
4. Validate: drop unknown IDs, clamp quantities to 1–20, attach prices from the catalog, compute totals in Python.
5. If both attempts fail or the API errors, return `mock_plan.json` and log it. The demo never shows a stack trace.

## Roles

One owner per area. Owners decide in their area without a team vote; anything crossing the JSON contract gets a 2-minute huddle. Fill in names tonight.

| Role | Owns | Name |
| --- | --- | --- |
| A — Backend + AI | `app.py`, `ai.py`, the prompt, validation, fallback, repo + merges | |
| B — Frontend | All three HTML pages, `style.css`, `plan.js` | |
| C — Catalog + domain | `catalog.json`, `mock_plan.json`, clinic test cases, checking the AI's output makes medical sense | |
| D — Product + pitch | Quote flow copy, demo script, slides, backup video, judging Q&A, keeps everyone on the timeline | |

**A — Backend + AI**

- [ ] Repo, `.gitignore` with `.env`, Flask hello-world running on everyone's machine (tonight)
- [ ] `/api/plan` returning `mock_plan.json` (tonight — this unblocks B)
- [ ] `generate_plan()` calling Gemini; same function with a Claude branch behind an env flag
- [ ] JSON parsing, one retry, catalog validation, totals in Python, fallback to mock
- [ ] `/api/catalog` and `/api/quote` (save to `quotes/<ref>.json`)

**B — Frontend**

- [ ] Intake form posting the exact request JSON above
- [ ] Plan page rendered from `mock_plan.json` first; rooms as cards, items as rows
- [ ] Quantity +/−, remove, "add from catalog" dropdown; room subtotals and grand total recalc live
- [ ] Loading state for the AI call (it takes 5–20 seconds; a frozen button looks broken)
- [ ] Submit page + confirmation; looks clean on a laptop projector

**C — Catalog + domain**

- [ ] 40–60 real products from ValueMed's site (or realistic ones if their site lacks them): id, name, category, price, `fits` (exam, procedure, reception, lab, sterilization)
- [ ] One hand-written "perfect" plan for a 3-exam-room family practice → `mock_plan.json` (deliver by midnight tonight)
- [ ] 5 test intakes: family practice, pediatrics, physio, dermatology, walk-in. Run each through the AI Saturday and mark what is wrong.
- [ ] Write the prompt's rules with A: must-haves per room type, no duplicates, quantities per room

**D — Product + pitch**

- [ ] Ask ValueMed's contact one question tonight/tomorrow AM: "What items do customers most often forget?" Use the answer in the prompt and the pitch.
- [ ] Demo script (below), 5-slide deck: problem, who, demo, how it works, what's next
- [ ] Record a backup screen video Sunday morning
- [ ] Owns the clock: calls each checkpoint and enforces the feature freeze
- [ ] When free, helps B with CSS or C with testing — never starts a new feature

## Timeline and checkpoints

Each checkpoint has a pass test. If it fails, the next block goes to fixing it — not to new features. Open question: confirm the exact judging time and shift the freeze to 12 hours before it.

1. **Friday night (now → midnight): Contract + skeleton.**
    - Agree on the JSON contract above. Fill in names. Everyone clones the repo and runs Flask locally.
    - A: `/api/plan` returns mock. C: `mock_plan.json` + first 20 catalog items. B: intake form layout. D: message ValueMed, draft demo story.
    - **Pass:** submitting the form shows the mock plan on screen (ugly is fine).
2. **Saturday morning: Real AI, end to end.**
    - A wires Gemini with validation + fallback. C finishes the catalog. B builds editing + totals on mock data.
    - **Pass (noon):** a real intake → real AI plan → displayed → edited → submitted → JSON file in `quotes/`. One clinic type is enough.
3. **Saturday afternoon: Quality.**
    - C runs all 5 test clinics; A and C fix the prompt until 4 of 5 produce a list a clinic owner wouldn't laugh at.
    - B polishes the plan page and loading state. D builds slides.
    - **Pass (6 pm):** 5 test clinics run with no crash and no invented items.
4. **Saturday night: Stretch or hardening.** Only if checkpoint 3 passed: one stretch item. Otherwise: fix bugs, then sleep. Exhausted teams demo badly.
5. **Sunday morning: FEATURE FREEZE.**
    - No new code except bug fixes approved by A. Merge to `main`, tag it.
    - Run the demo on the presenting laptop, on the venue Wi-Fi, 3 times. Record the backup video.
    - **Pass:** two clean full run-throughs in a row, under 3 minutes.

## Risks, rules, and the demo

| Risk | What happens | Prevention |
| --- | --- | --- |
| AI returns bad JSON or hallucinated items | Demo breaks live | Catalog-only IDs, Python validation, one retry, mock fallback |
| Free-tier rate limit hit during judging | Request fails on stage | Don't hammer the API while testing; have a Claude key or a second Google project ready; mock fallback |
| API key pushed to GitHub | Key gets scraped and revoked within minutes | `.env` in `.gitignore` from the first commit; never paste keys in Discord |
| Merge conflicts Sunday morning | Lost hours | Separate files per role; A is the only one merging to `main` |
| Venue Wi-Fi dies | No AI call | Hotspot from a phone + backup video |
| Scope creep ("let's just add…") | Nothing finished | D says no. Stretch list only after checkpoint 3 |

**Team rules**

- Commit small, push often, pull before you start.
- Stuck more than 30 minutes? Say so in the group chat. Don't silently burn the afternoon.
- Medical claims stay modest: "a suggested starting list for a sales rep to confirm", never "everything you need".

**3-minute demo script** (D presents, B drives the laptop)

1. **Problem (30 s):** New clinic owners don't know what to buy. ValueMed's site shows a catalog and a basic quote form, so lists get built over days of email and phone, and some never finish.
2. **Live demo (90 s):** Fill the intake for a 3-exam-room family practice with ECG and Pap tests. Show the plan by room with reasons. Change one quantity, remove one item, add one. Submit. Show the saved quote request a sales rep would receive.
3. **How it works (30 s):** AI picks only from ValueMed's real catalog; prices come from the catalog, not the AI; ValueMed updates a JSON file, not code.
4. **What's next (30 s):** Connect to ValueMed's live product data and CRM, add the stretch features, pilot with their sales team.