"""Parse common English date expressions into calendar dates."""

import re
from calendar import monthrange
from datetime import date, timedelta

_MONTHS = {
    name: number
    for number, name in enumerate(
        (
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ),
        start=1,
    )
}
_MONTHS.update({name[:3]: number for name, number in _MONTHS.items()})
_WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)
_NUMBERS = {
    word: number
    for number, word in enumerate(
        (
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
        )
    )
}
_NUMBERS.update(
    twenty=20,
    thirty=30,
    forty=40,
    fifty=50,
    sixty=60,
    seventy=70,
    eighty=80,
    ninety=90,
    a=1,
    an=1,
)
_OFFSET = re.compile(r"(\d+|[a-z]+(?:[ -][a-z]+)?) (years?|months?|weeks?|days?)")


def _number(text: str) -> int:
    if text.isdecimal():
        return int(text)
    if text in _NUMBERS:
        return _NUMBERS[text]
    parts = text.replace("-", " ").split()
    if (
        len(parts) == 2
        and _NUMBERS.get(parts[0], 0) >= 20
        and 1 <= _NUMBERS.get(parts[1], 0) <= 9
    ):
        return _NUMBERS[parts[0]] + _NUMBERS[parts[1]]
    raise ValueError(f"Unrecognized number: {text!r}")


def _apply_offset(text: str, base: date, direction: int) -> date:
    """Apply calendar months first, clamping the day, then weeks and days."""
    months = days = 0
    remaining = text
    while remaining:
        match = _OFFSET.match(remaining)
        if match is None:
            raise ValueError(f"Unrecognized date offset: {text!r}")
        amount = _number(match[1]) * direction
        unit = match[2].rstrip("s")
        if unit == "year":
            months += 12 * amount
        elif unit == "month":
            months += amount
        else:
            days += amount * (7 if unit == "week" else 1)
        remaining = remaining[match.end() :]
        if remaining:
            separator = re.match(r"(?: and |, *(?:and )?)", remaining)
            if separator is None:
                raise ValueError(f"Unrecognized date offset: {text!r}")
            remaining = remaining[separator.end() :]
            if not remaining:
                raise ValueError(f"Unrecognized date offset: {text!r}")

    year, month_index = divmod(base.year * 12 + base.month - 1 + months, 12)
    month = month_index + 1
    day = min(base.day, monthrange(year, month)[1])
    return date(year, month, day) + timedelta(days=days)


def parse(s: str, today: date | None = None) -> date:
    """Parse a date using ``today`` as the reference for relative expressions.

    Accept ISO dates, YYYY/M/D dates (with optional zero padding), English
    month/day/year dates (full or three-letter months, with an optional period),
    today/now/yesterday/tomorrow, next/last weekdays, and day/week/month/year
    offsets joined by commas and/or "and". ``now`` refers to the reference
    date, just like ``today``.
    Unknown expressions and invalid dates raise ValueError.
    """
    reference = date.today() if today is None else today
    text = " ".join(s.lower().split())

    try:
        if text in ("today", "now", "yesterday", "tomorrow"):
            return reference + timedelta(
                days={"today": 0, "now": 0, "yesterday": -1, "tomorrow": 1}[text]
            )

        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return date.fromisoformat(text)

        if match := re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", text):
            return date(int(match[1]), int(match[2]), int(match[3]))

        if match := re.fullmatch(
            r"([a-z]+)\.? (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})", text
        ):
            month = _MONTHS.get(match[1])
            if month is not None:
                return date(int(match[3]), month, int(match[2]))

        if (match := re.fullmatch(r"(next|last) ([a-z]+)", text)) and match[
            2
        ] in _WEEKDAYS:
            direction = 1 if match[1] == "next" else -1
            distance = (
                direction * (_WEEKDAYS.index(match[2]) - reference.weekday())
            ) % 7 or 7
            return reference + timedelta(days=direction * distance)

        if text.startswith("in "):
            return _apply_offset(text[3:], reference, 1)

        if text.endswith(" ago"):
            return _apply_offset(text[:-4], reference, -1)

        if match := re.fullmatch(r"(.+?) (before|after|from) (.+)", text):
            base = parse(match[3], reference)
            direction = -1 if match[2] == "before" else 1
            return _apply_offset(match[1], base, direction)
    except OverflowError as error:
        raise ValueError(f"Date is out of range: {s!r}") from error

    raise ValueError(f"Unrecognized date: {s!r}")


def main() -> None:
    print("Hello from nldate!")
