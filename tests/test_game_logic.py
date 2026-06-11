# FIX: I asked the AI to generate pytest cases covering every bug we fixed; each test below documents one.
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)


# ---------------------------------------------------------------------------
# get_range_for_difficulty
# Bug: Normal and Hard ranges were swapped (Normal returned 1-100,
# Hard returned 1-50).
# ---------------------------------------------------------------------------

def test_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_range_normal_is_1_to_50():
    # Was incorrectly 1-100.
    assert get_range_for_difficulty("Normal") == (1, 50)


def test_range_hard_is_1_to_100():
    # Was incorrectly 1-50.
    assert get_range_for_difficulty("Hard") == (1, 100)


def test_range_unknown_difficulty_defaults_to_1_to_100():
    assert get_range_for_difficulty("Impossible") == (1, 100)


# ---------------------------------------------------------------------------
# parse_guess
# Bug: decimal input like "1.9" was silently truncated to 1 instead of
# being rejected.
# ---------------------------------------------------------------------------

def test_parse_valid_integer():
    assert parse_guess("42") == (True, 42, None)


def test_parse_negative_integer():
    assert parse_guess("-5") == (True, -5, None)


def test_parse_empty_string_is_rejected():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_parse_none_is_rejected():
    ok, value, err = parse_guess(None)
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_parse_non_numeric_is_rejected():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_parse_decimal_is_rejected_not_truncated():
    # The bug truncated "1.9" -> 1. A decimal is not a valid whole guess.
    ok, value, err = parse_guess("1.9")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


# ---------------------------------------------------------------------------
# check_guess
# Bug: hint messages were inverted -- "Too High" told the player to
# "Go HIGHER" and "Too Low" told them to "Go LOWER".
# Note: check_guess returns a (outcome, message) tuple.
# ---------------------------------------------------------------------------

def test_winning_guess():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


def test_guess_too_high_outcome():
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low_outcome():
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


def test_too_high_hint_tells_player_to_go_lower():
    # Guessing above the secret must steer the player DOWN.
    _, message = check_guess(60, 50)
    assert "LOWER" in message.upper()
    assert "HIGHER" not in message.upper()


def test_too_low_hint_tells_player_to_go_higher():
    # Guessing below the secret must steer the player UP.
    _, message = check_guess(40, 50)
    assert "HIGHER" in message.upper()
    assert "LOWER" not in message.upper()


def test_secret_of_one_guessing_higher_says_go_lower():
    # Reproduces the "when the number is 1" report: guessing above 1
    # should say LOWER, not HIGHER.
    outcome, message = check_guess(5, 1)
    assert outcome == "Too High"
    assert "LOWER" in message.upper()


# ---------------------------------------------------------------------------
# update_score
# Bugs: (1) Win formula used (attempt_number + 1), penalising early wins;
# (2) "Too High" awarded +5 on even attempts, rewarding wrong guesses.
# ---------------------------------------------------------------------------

def test_win_on_first_attempt_scores_full_points():
    # Winning on attempt 1 should add the maximum 100 points.
    assert update_score(0, "Win", 1) == 100


def test_win_points_decrease_with_attempts():
    # Each later attempt is worth 10 fewer points.
    assert update_score(0, "Win", 2) == 90
    assert update_score(0, "Win", 3) == 80


def test_win_points_floored_at_ten():
    # Even a very late win never drops below 10 points.
    assert update_score(0, "Win", 50) == 10


def test_too_high_always_penalises():
    # Was +5 on even attempts. A wrong guess must never increase the score.
    assert update_score(100, "Too High", 1) == 95
    assert update_score(100, "Too High", 2) == 95  # even attempt: still -5


def test_too_low_penalises():
    assert update_score(100, "Too Low", 3) == 95


def test_unknown_outcome_leaves_score_unchanged():
    assert update_score(100, "Pending", 1) == 100
