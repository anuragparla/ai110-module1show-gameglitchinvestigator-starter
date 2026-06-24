# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
  When i first ran the game the range of values accepted vs the difficulty level i chose
  didn't make sense. Also when I entered 1 it would ask me to go LOWER and when I entered 1000 it was asking me to go HIGHER. Also the emojis for HIGHER and LOWER are reversed. The attempts left counter started at 1 instead of 0 thus leaving me with 1 less attempt. Once the game ends the new game button didn't load a new game!

- List at least two concrete bugs you noticed at the start  
  1) The range of number within which I can guess seems to be hardcoded. It wasn't changing on the main window eventhough i was choosing a specific difficulty level, the range always remained between 1-100
  2) The number of attempts left was always 1 less than the total attempts left
  3) New Game button doesn't load a new game. It just resets the attempts left


**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Select "Normal" difficulty | Range should be 1–50 | Range is 1–100 (Normal and Hard ranges are swapped in `get_range_for_difficulty`) | None |
| Select "Hard" difficulty | Range should be 1–100 | Range is 1–50 | None |
| Select "Easy" difficulty | 8 attempts allowed | Only 6 attempts (Easy/Normal attempt limits are swapped) | None |
| Select "Normal" difficulty | 6 attempts allowed | 8 attempts | None |
| Choose any non-Normal difficulty and read the "Make a guess" banner | Banner shows the range for the chosen difficulty | Banner always says "between 1 and 100" (range is hardcoded in the f-string) | None |
| Load the game fresh (before any guess) | "Attempts left" shows n (full limit) | Shows n−1 because `attempts` is initialized to 1 instead of 0 | None |
| Guess any number that is too high (e.g. secret 50, guess 80) | Hint says "Go LOWER" | Hint says "📈 Go HIGHER!" — message is inverted | None |
| Guess any number that is too low (e.g. secret 50, guess 20) | Hint says "Go HIGHER" | Hint says "📉 Go LOWER!" — message inverted (emojis reversed too) | None |
| Submit a guess on an even-numbered attempt (2nd, 4th, …) | Guess compared to the secret normally | Secret is cast to a string, so the correct number never registers as a win and hints become lexicographic nonsense ("9" > "50") | `TypeError: '>' not supported between 'int' and 'str'` caught silently by the except branch |
| Click "New Game" after a win or game over | A fresh playable game starts | `status` is never reset, so the next guess is blocked by `st.stop()` — game won't accept input | None |
| Click "New Game" on Hard difficulty | New secret drawn from the Hard range | Secret is always drawn from `randint(1, 100)` (hardcoded), ignoring difficulty | None |
| Click "New Game" mid-game | Score and guess history reset | Score carries over and history is not cleared | None |
| Compare fresh-load attempts to post–New Game attempts | Both start at the same baseline | Startup sets `attempts = 1` but New Game sets `attempts = 0` — inconsistent | None |
| Win the game / make wrong guesses | Score updates consistently and fairly | Win points use `attempt_number + 1` after attempts already incremented (double off-by-one); "Too High" *adds* +5 on even attempts (rewards a wrong guess) | None |
| Run `pytest tests/` | All tests pass | Tests fail: `logic_utils` functions all `raise NotImplementedError`, and `check_guess` returns a tuple `("Win", "…")` while tests assert it equals the string `"Win"` | `NotImplementedError` / `AssertionError` |
| Use up all attempts so attempts left would go below 0 | "Attempts left" floors at 0 | Banner can display a negative number (no floor) | None |
| Enter a decimal guess like `1.9` | Rejected or handled clearly | Silently truncated to `1` | None |

---

## 2. How did you use AI as a teammate?

- **Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?**

  I used Claude (through the Claude Code assistant inside VS Code). I worked with it as a debugging partner: I described the broken behavior I saw while playing the game, and it read through `app.py` and `logic_utils.py`, found additional bugs I had missed, helped refactor the logic, and generated the pytest cases.

- **An AI suggestion that was CORRECT.**

  *What the AI suggested:* I had only noticed that the hint said "go lower" when the secret was 1. The AI suggested that the real root cause of the "you can never win" problem was a separate line in `app.py` that cast the secret to a string on every even-numbered attempt (`secret = str(st.session_state.secret)`). It explained that comparing an `int` guess to a `str` secret makes `guess == secret` always `False` (so a win never registers on an even attempt) and throws a `TypeError`, which then fell into a fallback branch that compared the numbers as text.

  *Was it correct?* Yes.

  *How I verified it:* I opened the "Developer Debug Info" panel to see the secret, then guessed the exact number on a 2nd/4th attempt — before the fix it refused to register as a win. After removing the string cast and letting `check_guess` always receive the integer secret, that same guess won. I also ran `pytest tests/`, and the cases for `check_guess` (including the "secret of 1" case) all passed (22 passed).

- **An AI suggestion that was INCORRECT or MISLEADING.**

  *What the AI suggested:* While first tagging the bugs, the AI marked the existing test assertions (e.g. `assert check_guess(50, 50) == "Win"`) as a bug location, implying the test was wrong because `check_guess` returns a value that doesn't equal `"Win"`.

  *Was it correct?* It was misleading about *where* the bug was. The test's intent (checking the outcome) was fine — the real issue was that `check_guess` returns a `(outcome, message)` **tuple**, not a bare string, so the assertion needed to compare against the tuple (or index `[0]`), not the function needing to return a plain string.

  *How I verified it:* I checked how `check_guess` is actually used in `app.py` and saw `outcome, message = check_guess(...)` — the app depends on the tuple, so "fixing" the function to return a string would have broken the game. I kept the tuple contract and updated the tests to unpack it (`outcome, _ = check_guess(...)`), then confirmed with `pytest` that all tests passed. This taught me to verify an AI's claim about *which* piece of code is broken, not just accept the first thing it points at.

---

## 3. Debugging and testing your fixes

- **How did you decide whether a bug was really fixed?**

  I used two checks for every fix: an automated one and a manual one. For the pure logic (ranges, hints, parsing, scoring) I relied on `pytest tests/` — a bug was only "fixed" once a test that asserted the *correct* behavior passed. For the UI/state bugs (attempts counter, banner range, New Game) I ran the app with `python -m streamlit run app.py`, opened the "Developer Debug Info" panel so I could see the real secret, and reproduced the original broken steps to confirm they now behaved correctly. I treated a fix as real only when the exact reproduction I had logged in the Bug Reproduction Log no longer happened.

- **Describe at least one test you ran (manual or using pytest) and what it showed you about your code.**

  *Automated:* I ran `pytest tests/` and got `22 passed`. One case that mattered was `test_secret_of_one_guessing_higher_says_go_lower` — it calls `check_guess(5, 1)` and asserts the message contains "LOWER". Before the fix this would have returned "Go HIGHER!", so the test proved the inverted-hint bug was actually gone, not just hidden. Another, `test_too_high_always_penalises`, checks that a "Too High" guess subtracts points on *both* odd and even attempts, which caught the old +5 reward bug.

  *Manual:* In the running app I set difficulty to Hard, opened Debug Info, and played until "Game over," then clicked **New Game**. Before the fix the game refused my next guess (the `status` was never reset). After the fix, New Game cleared the banners, reset the score to 0, and accepted a new guess — confirming the state actually resets. I also watched "Attempts left" start at the full limit (e.g. 5 on Hard) instead of one less.

- **Did AI help you design or understand any tests? How?**

  Yes. I asked the AI to generate pytest cases covering every bug we had fixed, and it wrote one test per bug with a comment naming the bug it guards against (for example, the decimal-rejection test for `parse_guess("1.9")` and the floor-at-10 test for `update_score`). It also explained *why* the original tests were failing — they asserted `check_guess(...) == "Win"` but the function returns a `(outcome, message)` tuple — which helped me understand that a test can be "red" because of a wrong expectation, not only because of broken code. I verified its tests were meaningful by reading each assertion against the behavior I expected and by confirming they all passed only after the corresponding fix was in place.

---

## 4. What did you learn about Streamlit and state?

- **How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?**

  In Streamlit, every time you interact with the page — click a button, type in a box, change a dropdown — Streamlit re-runs your *entire* Python script from the top, like refreshing a web page. That means any normal variable you create is rebuilt from scratch each time, so it forgets whatever it held a moment ago. `st.session_state` is the workaround: it's a little dictionary that *survives* those reruns, so anything you want to remember between clicks (the secret number, the attempt count, the score, whether the game is over) has to live there. This project drove the lesson home in two ways: the secret number was correctly stored in `session_state` so it persisted, but the "New Game" button looked broken because it reset some session_state values (`attempts`, `secret`) while forgetting others (`status`, `score`, `history`) — so the leftover `status = "won"` survived the rerun and kept blocking new guesses. The fix was simply to reset *all* the relevant session_state in one place. The other gotcha was order: because the script runs top-to-bottom every rerun, the "New Game" handler calls `st.rerun()` after resetting state so the page redraws cleanly with the fresh values.

---

## 5. Looking ahead: your developer habits

- **What is one habit or strategy from this project that you want to reuse in future labs or projects?**

  Writing a test for every bug *before* I call it fixed. Instead of just eyeballing the game and assuming a change worked, I wrote a pytest case that asserts the correct behavior (for example, `check_guess(5, 1)` must say "LOWER"), so the bug is locked down and can't quietly come back later. Keeping a written Bug Reproduction Log of the exact input → expected → actual steps also made it obvious when a fix was truly done, because I could re-run the same steps.

- **What is one thing you would do differently next time you work with AI on a coding task?**

  I would push back on the AI's claims about *where* the bug is, sooner. At one point the AI pointed at the test assertion as the broken code, but when I traced how `check_guess` was actually called in `app.py` (`outcome, message = check_guess(...)`), I realized the function's tuple return was correct and the test expectation was the thing that needed updating. If I had blindly "fixed" the function to return a plain string, I would have broken the app. Next time I'll trace the suspect code to its callers before accepting the AI's diagnosis.

- **In one or two sentences, describe how this project changed the way you think about AI-generated code.**

  AI-generated code can look polished and confident — this app literally claimed to be "production-ready" — while being full of subtle, interacting bugs. I now treat AI output as a fast first draft that I have to read, test, and verify myself, rather than something I can trust on sight.
