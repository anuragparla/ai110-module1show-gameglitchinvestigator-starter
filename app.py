import random
import streamlit as st

# FIX: Refactored pure-logic functions into logic_utils.py using agent mode — AI read both files, identified the untestable coupling, and moved get_range_for_difficulty, parse_guess, check_guess, and update_score out of app.py so pytest could reach them.
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
    update_high_score,
    load_high_scores,
    save_high_scores,
)

# CHALLENGE 2: where per-difficulty best scores persist between runs.
HIGH_SCORE_FILE = "high_scores.json"

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

# FIX: Easy/Normal attempt limits were swapped — AI spotted the inversion by comparing the dict values to the README spec; verified manually by selecting each difficulty and confirming the sidebar counter.
attempt_limit_map = {
    "Easy": 8,
    "Normal": 6,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    # FIX: attempts initialized to 1 (showed n-1 left on load) — AI flagged the off-by-one; confirmed by opening the app fresh and watching "Attempts left" match the full limit.
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# CHALLENGE 2: load the saved best scores once per session, then show the
# best score for the current difficulty in the sidebar.
if "high_scores" not in st.session_state:
    st.session_state.high_scores = load_high_scores(HIGH_SCORE_FILE)

best_score = st.session_state.high_scores.get(difficulty)
st.sidebar.caption(
    f"🏆 Best ({difficulty}): {best_score if best_score is not None else '—'}"
)


def record_high_score(final_score):
    """Persist final_score as the new best for this difficulty if it beats it.

    Returns True when a new record was set.
    """
    previous_best = st.session_state.high_scores.get(difficulty)
    new_best, is_record = update_high_score(previous_best, final_score)
    st.session_state.high_scores[difficulty] = new_best
    save_high_scores(HIGH_SCORE_FILE, st.session_state.high_scores)
    return is_record


st.subheader("Make a guess")

# FIX: banner was hardcoded "1-100" for all difficulties — AI caught it during a code scan; verified by switching to Easy and confirming the banner updated to "1 to 20".
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIX: New Game left status/score/history stale and drew the secret from a hardcoded range — AI identified all four missing resets; verified by winning, clicking New Game on Hard, and confirming a fresh playable game started with a secret inside 1-100.
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # FIX: secret was cast to str on even attempts, making check_guess always miss — AI traced the TypeError to the cast; I confirmed by guessing the exact secret on attempt 2 (failed before fix, won after).
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            # CHALLENGE 2: record the score and celebrate a new best.
            is_record = record_high_score(st.session_state.score)
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
            if is_record:
                st.success(f"🏆 New high score for {difficulty}!")
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                # CHALLENGE 2: a finished game still counts as a score.
                record_high_score(st.session_state.score)
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
