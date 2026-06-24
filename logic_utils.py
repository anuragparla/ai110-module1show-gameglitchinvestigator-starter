"""Pure game logic for the Glitchy Guesser number-guessing game.

These helpers contain no Streamlit/UI code, so they can be unit tested in
isolation. ``app.py`` imports them and wires them to the interface.
"""

import json


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.

    Returns:
        A ``(low, high)`` tuple of ints. Unknown values default to
        ``(1, 100)``.
    """
    if difficulty == "Easy":
        return 1, 20
    # FIX: Normal/Hard ranges were swapped — AI identified the inversion by diffing the if-branches against expected UX; verified with pytest test_ranges and by switching difficulty in the running app.
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str):
    """Parse raw user input into an integer guess.

    Only whole numbers are accepted; decimals such as ``"1.9"`` are
    rejected rather than silently truncated.

    Args:
        raw: The raw string from the input box (may be ``None`` or ``""``).

    Returns:
        A ``(ok, guess_int, error_message)`` tuple. On success ``ok`` is
        ``True``, ``guess_int`` is the parsed int, and ``error_message`` is
        ``None``. On failure ``ok`` is ``False``, ``guess_int`` is ``None``,
        and ``error_message`` explains the problem.
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    # FIX: int(float(raw)) silently truncated "1.9" to 1 — AI flagged silent truncation as misleading UX; verified by running parse_guess("1.9") in pytest and confirming it now returns an error.
    try:
        value = int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """Compare a guess against the secret number and build a hint.

    Args:
        guess: The player's integer guess.
        secret: The secret integer to be found.

    Returns:
        A ``(outcome, message)`` tuple. ``outcome`` is ``"Win"``,
        ``"Too High"``, or ``"Too Low"``; ``message`` is the hint shown to
        the player.
    """
    # FIX: hint messages and emojis were inverted (too-high said "Go HIGHER") — AI caught the logic inversion; verified with pytest test_secret_of_one_guessing_higher_says_go_lower and by playing the game manually.
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        # Guess was too high -> the player should aim LOWER next.
        return "Too High", "📉 Go LOWER!"

    # Guess was too low -> the player should aim HIGHER next.
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Return the new score after applying one guess outcome.

    Args:
        current_score: The score before this guess.
        outcome: ``"Win"``, ``"Too High"``, or ``"Too Low"``.
        attempt_number: The 1-based attempt the outcome occurred on;
            winning on the first attempt scores the most points.

    Returns:
        The updated integer score.
    """
    # FIX: win formula used (attempt_number + 1) causing a double off-by-one — AI spotted it by tracing where attempts is incremented before calling update_score; verified with pytest test_win_on_first_attempt_scores_100.
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX: "Too High" rewarded +5 on even attempts (wrong guess earned points) — AI identified the branch during code inspection; verified with pytest test_too_high_always_penalises.
    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


# ---------------------------------------------------------------------------
# CHALLENGE 2: High Score tracker
# Persist the best score per difficulty to a JSON file. The pure comparison
# lives here (testable); app.py wires it to the file and the UI.
# ---------------------------------------------------------------------------

def update_high_score(current_best, new_score):
    """Compare a new score against the prior best for a difficulty.

    Args:
        current_best: The previous best score, or ``None`` if none has been
            recorded yet.
        new_score: The score just achieved.

    Returns:
        A ``(best_score, is_new_record)`` tuple. A tie does not count as a
        new record.
    """
    if current_best is None or new_score > current_best:
        return new_score, True
    return current_best, False


def load_high_scores(path):
    """Load the ``{difficulty: best_score}`` map from a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        The parsed dict, or an empty dict if the file is missing or
        unreadable, so a fresh install or corrupt file never crashes the
        game.
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_high_scores(path, scores):
    """Write the ``{difficulty: best_score}`` map to a JSON file.

    Args:
        path: Path to the JSON file to write.
        scores: The ``{difficulty: best_score}`` dict to persist.
    """
    with open(path, "w") as f:
        json.dump(scores, f)
