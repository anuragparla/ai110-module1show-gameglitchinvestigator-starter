def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    # FIX: I spotted the swapped ranges; AI confirmed Normal/Hard were reversed and corrected them.
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    # FIX: AI flagged that int(float(raw)) silently truncated "1.9"->1; we agreed to reject decimals.
    # Only whole numbers are valid guesses. "1.9" must be rejected, not
    # silently truncated to 1.
    try:
        value = int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX: I reported the lying hints; AI traced the inverted messages/emojis and we swapped them back.
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        # Guess was too high -> the player should aim LOWER next.
        return "Too High", "📉 Go LOWER!"

    # Guess was too low -> the player should aim HIGHER next.
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Update score based on outcome and attempt number.

    attempt_number is the 1-based attempt on which the outcome occurred:
    winning on the first attempt scores the most points.
    """
    # FIX: AI found the (attempt_number + 1) off-by-one; we changed it to -1 so attempt 1 scores full points.
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX: AI caught that "Too High" rewarded +5 on even attempts; we made every wrong guess cost the same.
    # Any wrong guess costs the same, regardless of attempt number.
    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
