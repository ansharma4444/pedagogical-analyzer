# 📊 Pedagogical Alignment Dashboard

A Streamlit tool that checks whether educational content (an app, a lesson,
a textbook passage) is actually written at the reading level and cognitive
demand it claims to target.

**Problem it solves:** EdTech content is often labeled with a grade level
("Grade 4 Science") without anyone verifying that the *actual text* matches
that level. A passage full of Grade 12 vocabulary shown to 8-year-olds is a
common, hard-to-spot failure mode. This tool quantifies that mismatch.

---

## How it works

For each piece of lesson text, the tool computes three things:

1. **Reading Grade** — via the [Flesch-Kincaid](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests)
   formula (using the `textstat` library), capped at grade 12 so extreme
   outliers don't distort the dashboard's scale.
2. **Cognitive Level** — matches the text against verb lists from
   [Bloom's Taxonomy](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)
   (Remembering → Understanding → Applying → Analyzing → Evaluating →
   Creating), scoring **all** levels and picking the one with the most
   verb hits, rather than just the first keyword it happens to find.
3. **Alignment Score** — a 0–100 score based on how far the actual Reading
   Grade is from the content's stated Target Grade (100 = perfect match,
   −10 points per grade level of mismatch).

Every analysis is saved to a local CSV so results persist across sessions,
and the dashboard plots all saved results on a scatter chart (Target Grade
vs. Reading Grade) with a "perfect alignment" reference line.

---

## Project structure

```
pedagogical_analyzer/
├── app.py                  # Streamlit UI — layout & user interaction only
├── analyzer.py              # Core scoring logic (readability, Bloom's, alignment)
├── storage.py                # CSV persistence layer
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt        # + pytest, for running tests
├── tests/
│   └── test_analyzer.py        # Unit tests for analyzer.py
├── sample_data/
│   └── sample_lessons.md        # Ready-to-paste demo texts, grades 1–12
└── data/
    └── results.csv               # Auto-created on first run (gitignored)
```

The analysis logic (`analyzer.py`) and persistence (`storage.py`) are kept
separate from the UI (`app.py`) on purpose: they don't import Streamlit at
all, which is what makes them independently unit-testable and reusable
(e.g. from a CLI script or an API) without spinning up a web app.

---

## Running it locally

```bash
git clone <this-repo>
cd pedagogical_analyzer
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

### Try it with sample data
Open `sample_data/sample_lessons.md` and paste any of the example texts in,
setting the slider to the listed Target Grade. Example #9 ("Science for
Kids") is a deliberately mismatched case — Grade 12 vocabulary shown to a
Grade 3 audience — and is the clearest way to demo a *low* Alignment Score.

---

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests cover the readability capping logic, the alignment scoring formula,
and — most importantly — the Bloom's Taxonomy classifier's tie-breaking
behavior, since that's the part most prone to silent bugs (see "Design
decisions" below).

---

## Design decisions worth knowing (and mentioning in an interview)

- **Bloom's classification counts verbs, it doesn't just find the first
  one.** An earlier version of this tool returned whichever taxonomy level
  it checked first that had *any* matching verb — so a passage with both
  "list" (Remembering) and "design" (Creating) would silently be scored as
  "Remembering" purely because of dictionary iteration order. The current
  version scores every level and picks the level with the most verb hits,
  breaking ties toward the higher cognitive level (Bloom's levels are
  cumulative, so that's the more defensible default).
- **Reading grade is capped, not clipped silently.** Very short or very
  dense passages can produce nonsensical Flesch-Kincaid scores (negative or
  100+); capping at 0–12 keeps the dashboard's scale meaningful without
  hiding the underlying computation.
- **Persistence is a plain CSV, not a database.** For a single-user tool
  this is enough to survive a refresh, and it keeps the project runnable
  with zero setup. `storage.py` isolates this choice so it could be swapped
  for SQLite/Postgres later without touching `analyzer.py` or `app.py`.

## Known limitations / next steps

- Bloom's verb matching is still keyword-based, so it can be fooled by verbs
  used outside their taxonomic sense (e.g. "test" as a noun rather than an
  analytical verb). A production version could use POS tagging or a small
  classifier instead of regex matching.
- Readability alone doesn't capture *conceptual* difficulty — a short
  sentence can still describe a hard idea. Combining Flesch-Kincaid with a
  vocabulary-difficulty or concept-density signal would strengthen this.
- No multi-user auth or database — fine for a portfolio/demo tool, not yet
  for a shared classroom deployment.

---

## Tech stack
Python · Streamlit · pandas · Plotly · textstat · pytest
