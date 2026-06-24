# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

### Challenge 2: Feature Expansion — High Score tracker

**What task did you give the agent?**

I asked the agent (Claude, via Claude Code) to plan and implement a meaningful new feature: a **High Score tracker** that saves the best score per difficulty to a file, displays it in the sidebar, and celebrates when the player sets a new record — while keeping the testable logic in `logic_utils.py`.

**Files modified:**

| File | Change |
|------|--------|
| `logic_utils.py` | Added `update_high_score(current_best, new_score)` (pure comparison) plus `load_high_scores(path)` / `save_high_scores(path, scores)` JSON helpers; added `import json`. |
| `app.py` | Imported the new functions, defined `HIGH_SCORE_FILE`, loaded saved scores into `session_state`, added the sidebar `🏆 Best (...)` caption, and a `record_high_score()` helper called on both win and loss (with a `🏆 New high score!` message on a win record). |
| `tests/test_game_logic.py` | Added 8 pytest cases: best-score comparison (first score, higher, lower, tie, negative) and JSON save/load round-trip (including missing- and corrupt-file handling using `tmp_path`). |
| `.gitignore` | Added `high_scores.json` so the local runtime data file is not committed. |
| `README.md` | Marked the stretch feature done and refreshed the pytest output (now 39 passing). |

**What did the agent do?**

1. Planned the split: pure logic + file I/O in `logic_utils.py`, UI/persistence wiring in `app.py`.
2. Implemented the functions and wired the load/display/record flow into the Streamlit app.
3. Wrote tests and ran `pytest`, confirming **39 passed**.
4. Verified the files parse and updated the docs.

**What did you have to verify or fix manually?**

- **Design decision the agent flagged for me:** whether a *lost* game should still update the high score. I decided yes — the best score so far should count even from a losing game — so the agent calls `record_high_score()` on both outcomes.
- **Edge cases I checked:** scores can be **negative** in this game, so I confirmed the agent compared with `>` (not assuming positive scores) and added a test for it (`-5` beats `-10`).
- **Persistence safety:** I made sure a missing or corrupt `high_scores.json` returns `{}` instead of crashing on startup, and added a corrupt-file test to prove it.
- **Repo hygiene:** I had the agent add the data file to `.gitignore` so per-machine scores don't get committed.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

### Challenge 1: Advanced Edge-Case Testing

**Prompts I used to generate the tests:**

```
1. "Look at parse_guess, check_guess, and update_score in logic_utils.py.
    Identify three edge-case inputs a player could enter that might still
    break the game even though the obvious bugs are fixed."

2. "Generate a suite of pytest cases for those three edge cases. For each one,
    test the full pipeline (parse_guess -> check_guess -> update_score) and
    assert the game responds gracefully instead of crashing or behaving wrong.
    Add them to tests/test_game_logic.py with comments explaining each case."

3. "Run pytest -v and show me the full passing output."
```

**Edge cases chosen (one-line reason each):**

| Edge Case | Why this case was chosen | AI-Suggested Test(s) | Did It Pass? |
|-----------|--------------------------|----------------------|--------------|
| **Negative numbers** (`"-5"`) | There is no lower-bound validation, so a negative guess must still parse and be treated as "Too Low" instead of crashing. | `test_negative_number_parses_as_valid_int`, `test_negative_guess_is_handled_as_too_low`, `test_negative_guess_scores_without_crashing` | ✅ Pass |
| **Decimals** (`"3.14"`, `"5.0"`, `"-2.5"`) | This was the original silent-truncation bug (`"1.9"` → `1`); decimals must be rejected cleanly, including `"5.0"`. | `test_positive_decimal_is_rejected`, `test_whole_number_decimal_is_still_rejected`, `test_negative_decimal_is_rejected` | ✅ Pass |
| **Extremely large values** (`"99999999999999999999"`, `10**100`) | Python ints are unbounded, so a giant number must register as "Too High" without overflow or error. | `test_extremely_large_value_parses`, `test_extremely_large_guess_is_too_high`, `test_extremely_large_guess_scores_without_crashing` | ✅ Pass |

**Result:** All 31 tests pass (`31 passed in 0.03s`). See the full terminal output in `README.md`.

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

### Challenge 3: Professional Documentation and Linting

**Prompts used:**

```
1. "Add professional-grade docstrings to every function in logic_utils.py.
    Use a consistent style with Args and Returns sections, and add a module
    docstring."

2. "Review app.py, logic_utils.py, and tests/test_game_logic.py for PEP 8
    style compliance. Run flake8 and apply fixes for anything it reports
    (line length, naming, formatting)."

3. "Re-run flake8 and pytest to confirm zero style issues and that all tests
    still pass."
```

**Linting output BEFORE (flake8, default PEP 8 / 79-char limit):**

```
$ flake8 logic_utils.py app.py tests/test_game_logic.py
logic_utils.py:8:80: E501 line too long (99 > 79 characters)
logic_utils.py:28:80: E501 line too long (101 > 79 characters)
logic_utils.py:45:80: E501 line too long (103 > 79 characters)
logic_utils.py:64:80: E501 line too long (109 > 79 characters)
logic_utils.py:71:80: E501 line too long (107 > 79 characters)
app.py:4:80: E501 line too long (101 > 79 characters)
app.py:31:80: E501 line too long (111 > 79 characters)
app.py:48:80: E501 line too long (108 > 79 characters)
app.py:84:80: E501 line too long (106 > 79 characters)
app.py:110:80: E501 line too long (102 > 79 characters)
app.py:111:80: E501 line too long (93 > 79 characters)
app.py:138:80: E501 line too long (101 > 79 characters)
app.py:165:80: E501 line too long (82 > 79 characters)
tests/test_game_logic.py:1:80: E501 line too long (106 > 79 characters)
```

**Linting output AFTER (all fixes applied):**

```
$ flake8 logic_utils.py app.py tests/test_game_logic.py
(no output — 0 issues)
```

**What the AI suggested and what I applied:**

| AI suggestion | Applied? | Note |
|---------------|----------|------|
| Add a module docstring + `Args:`/`Returns:` docstrings to all 7 functions in `logic_utils.py` | ✅ Yes | Every function now has a professional docstring describing its arguments and return value. |
| Fix all `E501` line-too-long warnings (14 lines) | ✅ Yes | These were almost entirely the verbose `# FIX:` collaboration comments I added earlier; I shortened/wrapped them to fit 79 chars, and moved one trailing inline comment onto its own line. |
| Keep the existing function/variable names | ✅ Yes (no change needed) | flake8 reported **no** naming (`N8xx`) issues — names like `get_range_for_difficulty` and `update_high_score` were already PEP 8 snake_case, so nothing was renamed. |

**Result:** `flake8` now reports **0 issues** across all three files, and `pytest` still shows **39 passed**. The only style category flagged was line length (`E501`); there were no naming or other formatting violations to fix.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
