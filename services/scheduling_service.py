# services/scheduling_service.py
# ============================================================
# Smart Scheduling — Advanced Feature
# ============================================================
# Algorithm:
#   1. Pull all existing appointments for the physician in [start_date, end_date].
#   2. For each business day in the range, build a list of BUSY intervals.
#   3. Walk through each day in 15-minute increments; any slot that fits
#      (does not overlap busy intervals AND stays within business hours) is CANDIDATE.
#   4. Score each candidate slot using a weighted ranking function.
#   5. Return the top 5 ranked slots.
#
# Ranking factors:
#   - If preference == 'earliest': prefer earlier in the day (lower score = better)
#   - If preference == 'latest':   prefer later in the day
#   - Bonus for slots that minimize gap between adjacent appointments
#     (improves physician throughput)
# ============================================================

import datetime
from db import execute_query
from config import Config


BUSINESS_START = datetime.time(Config.BUSINESS_START_HOUR, 0)
BUSINESS_END   = datetime.time(Config.BUSINESS_END_HOUR,   0)
SLOT_STEP_MIN  = 15   # granularity for candidate generation


def _time_to_minutes(t: datetime.time) -> int:
    return t.hour * 60 + t.minute


def _minutes_to_time(m: int) -> datetime.time:
    return datetime.time(m // 60, m % 60)


def _get_busy_intervals(physician_license: str, date: datetime.date):
    """
    Fetch existing appointments for a physician on a given date.
    Returns a list of (start_min, end_min) integer tuples.
    SQL technique: simple filter query, results fed into Python interval logic.
    """
    rows = execute_query(
        """
        SELECT Time, Duration
        FROM Appointment
        WHERE Physician_License_Number = %s AND Date = %s
        ORDER BY Time
        """,
        (physician_license, date.isoformat())
    )
    intervals = []
    for row in rows:
        # TIME columns come back as timedelta from mysql.connector
        if isinstance(row['Time'], datetime.timedelta):
            total_sec = int(row['Time'].total_seconds())
            start_min = total_sec // 60
        else:
            t = row['Time']
            start_min = _time_to_minutes(t)
        end_min = start_min + int(row['Duration'])
        intervals.append((start_min, end_min))
    return intervals


def _overlaps(start: int, end: int, intervals) -> bool:
    """
    Interval overlap check: new slot [start, end) conflicts with existing
    interval [a, b) if start < b AND a < end.
    """
    for (a, b) in intervals:
        if start < b and a < end:
            return True
    return False


def _gap_score(start: int, intervals) -> float:
    """
    Compute the gap (in minutes) between the proposed slot start and the
    nearest busy interval end-time BEFORE it.
    Smaller gap = higher physician throughput = lower (better) score.
    Returns a large number if no prior appointment exists (penalize isolated slots less).
    """
    prior_ends = [b for (a, b) in intervals if b <= start]
    if not prior_ends:
        return 9999  # no prior appointment → neutral
    return start - max(prior_ends)


def find_available_slots(
    physician_license: str,
    start_date: datetime.date,
    end_date: datetime.date,
    duration_min: int,
    preference: str = 'earliest',  # 'earliest' | 'latest'
    top_n: int = 5
):
    """
    Core smart scheduling function.
    Returns a list of dicts: [{date, time, score, rank}, ...] top_n slots.
    """
    biz_start_min = _time_to_minutes(BUSINESS_START)
    biz_end_min   = _time_to_minutes(BUSINESS_END)

    candidates = []

    # Iterate over every weekday in the date range
    current = start_date
    while current <= end_date:
        # Skip weekends (0=Mon … 4=Fri, 5=Sat, 6=Sun)
        if current.weekday() < 5:
            busy = _get_busy_intervals(physician_license, current)

            # Walk through the day in SLOT_STEP_MIN increments
            slot_start = biz_start_min
            while slot_start + duration_min <= biz_end_min:
                slot_end = slot_start + duration_min

                if not _overlaps(slot_start, slot_end, busy):
                    # Valid candidate — compute ranking score
                    gap    = _gap_score(slot_start, busy)
                    # Preference score: lower = earlier; invert for 'latest'
                    if preference == 'earliest':
                        pref_score = slot_start  # smaller = earlier = better
                    else:
                        pref_score = -slot_start  # larger slot_start = later = better (negated)

                    # Combined score (lower is better after normalization in sort)
                    # Weight: 70% preference, 30% gap efficiency
                    score = 0.7 * pref_score + 0.3 * (gap if preference == 'earliest' else -gap)

                    candidates.append({
                        'date':      current.isoformat(),
                        'time':      _minutes_to_time(slot_start).strftime('%H:%M'),
                        'end_time':  _minutes_to_time(slot_end).strftime('%H:%M'),
                        'day_name':  current.strftime('%A, %B %d, %Y'),
                        'score':     round(score, 2)
                    })

                slot_start += SLOT_STEP_MIN

        current += datetime.timedelta(days=1)

    if not candidates:
        return []

    # Sort by score (ascending = best first) and return top N
    candidates.sort(key=lambda x: x['score'])
    top = candidates[:top_n]

    # Add human-readable rank
    for i, slot in enumerate(top, start=1):
        slot['rank'] = i

    return top
