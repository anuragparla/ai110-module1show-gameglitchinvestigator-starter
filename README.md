# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.**

  Glitchy Guesser is a single-player number-guessing game built with Streamlit. The player picks a difficulty (Easy/Normal/Hard), which sets the number range and how many attempts they get. Each guess returns a hint ("Go HIGHER" / "Go LOWER") and updates a running score, and the game ends on a correct guess or when attempts run out.

- [x] **Detail which bugs you found.**

  - **Difficulty ranges swapped** — Normal returned 1–100 and Hard returned 1–50 (should be Normal 1–50, Hard 1–100).
  - **Attempt limits swapped** — Easy gave 6 and Normal gave 8 (should be Easy 8, Normal 6; Hard 5 was correct).
  - **Banner range hardcoded** — the "Make a guess" banner always said "between 1 and 100" regardless of difficulty.
  - **Attempts counter started at 1** — so "Attempts left" showed one less than the real limit on first load.
  - **Inverted hints** — "Too High" told the player to "Go HIGHER" and "Too Low" said "Go LOWER" (arrows reversed too).
  - **Unwinnable game** — the secret was cast to a string on every even-numbered attempt, so a correct guess never registered and comparisons threw `TypeError`.
  - **New Game didn't restart** — it never reset `status`, `score`, or `history`, so after a win/loss the next guess was blocked; it also drew the new secret from 1–100 instead of the chosen range.
  - **Scoring bugs** — winning used `100 - 10*(attempt + 1)` (penalised early wins), and "Too High" *added* +5 on even attempts (rewarded wrong guesses).
  - **Loose input parsing** — `"1.9"` was silently truncated to `1` instead of being rejected.
  - **Logic mixed into UI** — the core functions lived in `app.py` instead of `logic_utils.py`.

- [x] **Explain what fixes you applied.**

  - Corrected the difficulty ranges and attempt limits.
  - Replaced the hardcoded banner text with the live `{low}`–`{high}` range and started the attempts counter at 0.
  - Un-inverted the hint messages and emojis in `check_guess`.
  - Removed the even-attempt `str(secret)` cast so guesses are always compared as integers (the game is now winnable).
  - Made New Game reset `attempts`, `secret`, `score`, `status`, and `history`, drawing the secret from the active difficulty range.
  - Fixed scoring: a first-attempt win now scores the full 100 points, and every wrong guess consistently costs 5 points.
  - Made `parse_guess` reject decimals instead of truncating them.
  - Refactored `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` into `logic_utils.py` and added 31 pytest cases (including the Challenge 1 edge-case suite).

## 📸 Demo Walkthrough

A text-based run through one full game so you can follow the fixed behavior end-to-end without running it. This example uses **Normal** difficulty (range **1–50**, **6 attempts**) with a secret of **37** (revealed via the "Developer Debug Info" panel for the demo).

1. **Start the game.** The sidebar shows "Range: 1 to 50" and "Attempts allowed: 6". The banner reads *"Guess a number between 1 and 50. Attempts left: 6"* — the full limit, not 5.
2. **Guess 25 → "Too Low".** The hint correctly says *"📈 Go HIGHER!"*. Attempts left drops to 5. Score: **−5** (a wrong guess costs 5).
3. **Guess 45 → "Too High".** The hint correctly says *"📉 Go LOWER!"*. Attempts left drops to 4. Score: **−10**.
4. **Guess 37 → "Correct!".** Balloons appear and the game shows *"You won! The secret was 37."* Winning on the 3rd attempt scores `100 − 10×(3−1) = 80` points, so the **final score is 70** (−10 + 80).
5. **Game ends.** With the game won, the status is "won" and further guesses are blocked until a new game starts.
6. **Click "New Game 🔁".** The win banner clears, score resets to 0, attempts reset to 6, and a fresh secret is drawn from the **1–50** range. The next guess is accepted immediately — confirming the game actually restarts.

*Edge cases also handled:* entering `1.9` is rejected as "That is not a number." (no silent truncation), entering letters shows "That is not a number.", and running out of all 6 attempts ends the game with "Out of attempts!".

## 🧪 Test Results

I completed **Challenge 1: Advanced Edge-Case Testing** — the suite has **39 pytest cases** in `tests/test_game_logic.py`: at least one test per fixed bug (swapped ranges, inverted hints, decimal input, scoring floor/penalties, the "secret of 1" hint case), a dedicated edge-case suite covering **negative numbers, decimals, and extremely large values**, and the **Challenge 2 high-score tracker** tests (comparison + JSON save/load).

```
$ pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /Users/anuragparla/Documents/ai110-module1show-gameglitchinvestigator-starter
collected 39 items

tests/test_game_logic.py::test_range_easy PASSED                         [  2%]
tests/test_game_logic.py::test_range_normal_is_1_to_50 PASSED            [  5%]
tests/test_game_logic.py::test_range_hard_is_1_to_100 PASSED             [  7%]
tests/test_game_logic.py::test_range_unknown_difficulty_defaults_to_1_to_100 PASSED [ 10%]
tests/test_game_logic.py::test_parse_valid_integer PASSED                [ 12%]
tests/test_game_logic.py::test_parse_negative_integer PASSED             [ 15%]
tests/test_game_logic.py::test_parse_empty_string_is_rejected PASSED     [ 17%]
tests/test_game_logic.py::test_parse_none_is_rejected PASSED             [ 20%]
tests/test_game_logic.py::test_parse_non_numeric_is_rejected PASSED      [ 23%]
tests/test_game_logic.py::test_parse_decimal_is_rejected_not_truncated PASSED [ 25%]
tests/test_game_logic.py::test_winning_guess PASSED                      [ 28%]
tests/test_game_logic.py::test_guess_too_high_outcome PASSED             [ 30%]
tests/test_game_logic.py::test_guess_too_low_outcome PASSED              [ 33%]
tests/test_game_logic.py::test_too_high_hint_tells_player_to_go_lower PASSED [ 35%]
tests/test_game_logic.py::test_too_low_hint_tells_player_to_go_higher PASSED [ 38%]
tests/test_game_logic.py::test_secret_of_one_guessing_higher_says_go_lower PASSED [ 41%]
tests/test_game_logic.py::test_win_on_first_attempt_scores_full_points PASSED [ 43%]
tests/test_game_logic.py::test_win_points_decrease_with_attempts PASSED  [ 46%]
tests/test_game_logic.py::test_win_points_floored_at_ten PASSED          [ 48%]
tests/test_game_logic.py::test_too_high_always_penalises PASSED          [ 51%]
tests/test_game_logic.py::test_too_low_penalises PASSED                  [ 53%]
tests/test_game_logic.py::test_unknown_outcome_leaves_score_unchanged PASSED [ 56%]
tests/test_game_logic.py::test_negative_number_parses_as_valid_int PASSED [ 58%]
tests/test_game_logic.py::test_negative_guess_is_handled_as_too_low PASSED [ 61%]
tests/test_game_logic.py::test_negative_guess_scores_without_crashing PASSED [ 64%]
tests/test_game_logic.py::test_positive_decimal_is_rejected PASSED       [ 66%]
tests/test_game_logic.py::test_whole_number_decimal_is_still_rejected PASSED [ 69%]
tests/test_game_logic.py::test_negative_decimal_is_rejected PASSED       [ 71%]
tests/test_game_logic.py::test_extremely_large_value_parses PASSED       [ 74%]
tests/test_game_logic.py::test_extremely_large_guess_is_too_high PASSED  [ 76%]
tests/test_game_logic.py::test_extremely_large_guess_scores_without_crashing PASSED [ 79%]
tests/test_game_logic.py::test_first_score_is_always_a_record PASSED     [ 82%]
tests/test_game_logic.py::test_higher_score_sets_a_new_record PASSED     [ 84%]
tests/test_game_logic.py::test_lower_score_does_not_beat_the_record PASSED [ 87%]
tests/test_game_logic.py::test_tied_score_is_not_a_new_record PASSED     [ 89%]
tests/test_game_logic.py::test_negative_scores_compare_correctly PASSED  [ 92%]
tests/test_game_logic.py::test_high_scores_save_and_load_roundtrip PASSED [ 94%]
tests/test_game_logic.py::test_load_missing_file_returns_empty_dict PASSED [ 97%]
tests/test_game_logic.py::test_load_corrupt_file_returns_empty_dict PASSED [100%]

============================== 39 passed in 0.02s ==============================
```

## 🚀 Stretch Features

- [x] **Challenge 2 — High Score tracker.** The game now saves the **best score per difficulty** to a local `high_scores.json` file, so records persist across sessions. The sidebar shows `🏆 Best (<difficulty>): <score>`, and winning with a score that beats the saved best shows a `🏆 New high score!` celebration. The comparison logic (`update_high_score`) and the JSON `load_high_scores`/`save_high_scores` helpers live in `logic_utils.py` and are covered by 8 pytest cases.
