"""A compact specification for nldate.parse based on the assignment README.

Chosen conventions: next/last weekdays are strictly in the future/past, and
month/year offsets clamp to the last valid day when needed.
"""

from datetime import date

import pytest

import nldate

REFERENCE = date(2025, 3, 12)  # Wednesday; independent of the machine's clock.


def test_days_before_named_date() -> None:
    assert nldate.parse("5 days before December 1st, 2025", today=REFERENCE) == date(
        2025, 11, 26
    )


def test_compound_offset_from_yesterday() -> None:
    assert nldate.parse("1 year and 2 months after yesterday", today=REFERENCE) == date(
        2026, 5, 11
    )


def test_next_tuesday() -> None:
    assert nldate.parse("next Tuesday", today=REFERENCE) == date(2025, 3, 18)


def test_spelled_out_weeks_from_tomorrow() -> None:
    assert nldate.parse("two weeks from tomorrow", today=REFERENCE) == date(2025, 3, 27)


def test_in_three_days() -> None:
    assert nldate.parse("in 3 days", today=REFERENCE) == date(2025, 3, 15)


def test_iso_date() -> None:
    assert nldate.parse("2025-12-01", today=REFERENCE) == date(2025, 12, 1)


def test_named_date() -> None:
    assert nldate.parse("December 1, 2025", today=REFERENCE) == date(2025, 12, 1)


def test_today_returns_date_with_positional_reference() -> None:
    result = nldate.parse("today", REFERENCE)
    assert type(result) is date
    assert result == REFERENCE


def test_yesterday() -> None:
    assert nldate.parse("yesterday", today=REFERENCE) == date(2025, 3, 11)


def test_tomorrow_crosses_year_boundary() -> None:
    assert nldate.parse("tomorrow", today=date(2025, 12, 31)) == date(2026, 1, 1)


def test_days_ago() -> None:
    assert nldate.parse("10 days ago", today=REFERENCE) == date(2025, 3, 2)


def test_next_weekday_skips_today() -> None:
    assert nldate.parse("next Wednesday", today=REFERENCE) == date(2025, 3, 19)


def test_last_weekday() -> None:
    assert nldate.parse("last Monday", today=REFERENCE) == date(2025, 3, 10)


def test_month_offset_clamps_to_month_end() -> None:
    assert nldate.parse("in 1 month", today=date(2025, 1, 31)) == date(2025, 2, 28)


def test_year_offset_from_leap_day() -> None:
    assert nldate.parse("in 1 year", today=date(2024, 2, 29)) == date(2025, 2, 28)


def test_case_and_whitespace() -> None:
    assert nldate.parse("  In   3   DAYS  ", today=REFERENCE) == date(2025, 3, 15)


def test_today_defaults_to_current_date() -> None:
    # Bracket the calls so crossing midnight does not cause a spurious failure.
    before = date.today()
    implicit = nldate.parse("today")
    explicit_none = nldate.parse("today", today=None)
    after = date.today()
    assert before <= implicit <= after
    assert before <= explicit_none <= after


def test_empty_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        nldate.parse("", today=REFERENCE)


def test_unrecognized_input_raises_value_error() -> None:
    with pytest.raises(ValueError):
        nldate.parse("not a date", today=REFERENCE)


def test_impossible_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        nldate.parse("2025-02-29", today=REFERENCE)
