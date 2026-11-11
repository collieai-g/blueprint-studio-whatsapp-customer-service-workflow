"""Read-only settings resolver and weekly schedule checker for the V2 package."""

import argparse
import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
INTEGER_RANGES = {
    ("schedule", "interval_minutes"): (1, 1440),
    ("observation", "initial_seconds"): (0, 3600),
    ("observation", "after_reply_seconds"): (0, 3600),
    ("observation", "poll_seconds"): (1, 60),
    ("reply_limits", "max_per_conversation_per_patrol"): (1, 1000),
    ("reply_limits", "max_per_patrol"): (1, 1000),
    ("reply_limits", "max_characters"): (1, 10000),
    ("reply_limits", "max_clarifying_questions"): (0, 10),
}


def read_object(path):
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def clock_minutes(value):
    if not isinstance(value, str) or not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value):
        raise ValueError("weekly window start and end must use HH:MM (00:00 to 23:59)")
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


def validate_settings(settings):
    for (section, key), (minimum, maximum) in INTEGER_RANGES.items():
        value = settings[section][key]
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(f"{section}.{key} must be an integer from {minimum} to {maximum}")

    schedule = settings["schedule"]
    timezone = schedule["timezone"]
    if not isinstance(timezone, str) or not re.fullmatch(r"[A-Za-z0-9_+\-]+(?:/[A-Za-z0-9_+\-]+)*", timezone):
        raise ValueError("schedule.timezone must be an IANA name such as Asia/Hong_Kong or UTC")
    windows = schedule["weekly_windows"]
    if not isinstance(windows, list):
        raise ValueError("schedule.weekly_windows must be an array")
    for window in windows:
        if not isinstance(window, dict) or set(window) != {"weekdays", "start", "end"}:
            raise ValueError("each weekly window needs weekdays, start and end")
        weekdays = window["weekdays"]
        if not isinstance(weekdays, list) or not weekdays:
            raise ValueError("weekdays must be a nonempty array of ISO weekdays (Monday=1, Sunday=7)")
        if any(type(day) is not int or day not in range(1, 8) for day in weekdays):
            raise ValueError("weekdays must contain only integers from 1 to 7")
        if len(set(weekdays)) != len(weekdays):
            raise ValueError("weekdays must not repeat")
        if clock_minutes(window["start"]) == clock_minutes(window["end"]):
            raise ValueError("equal start and end are ambiguous; use [] for an unrestricted schedule")


def legacy_overrides(timing):
    if not isinstance(timing, dict):
        raise ValueError("V1 timing must be a JSON object")
    supported = {
        "patrol_interval_seconds",
        "initial_watch_seconds",
        "after_reply_watch_seconds",
        "reset_watch_after_each_reply",
        "presence_only_extends_watch",
    }
    unknown = set(timing) - supported
    if unknown:
        raise ValueError(f"unknown V1 timing keys: {', '.join(sorted(unknown))}")
    if timing.get("reset_watch_after_each_reply", True) is not True:
        raise ValueError("V2 uses a fresh observation window after each successful reply")
    if timing.get("presence_only_extends_watch", False) is not False:
        raise ValueError("V2 does not extend observation for presence alone")
    result = {"schedule": {}, "observation": {}}
    if "patrol_interval_seconds" in timing:
        seconds = timing["patrol_interval_seconds"]
        if type(seconds) is not int or seconds % 60:
            raise ValueError("V1 patrol interval must convert exactly to whole minutes")
        result["schedule"]["interval_minutes"] = seconds // 60
    for previous, current in (
        ("initial_watch_seconds", "initial_seconds"),
        ("after_reply_watch_seconds", "after_reply_seconds"),
    ):
        if previous in timing:
            result["observation"][current] = timing[previous]
    return result


def resolve_settings(profile=None):
    defaults = read_object(PACKAGE_ROOT / "settings.defaults.json")
    settings = deepcopy(defaults)
    profile = {} if profile is None else profile
    version = profile.get("schema_version")
    if version is not None and version not in ("1.0", "2.0"):
        raise ValueError("company profile schema_version must be 1.0 or 2.0")
    if "settings" in profile and "timing" in profile:
        raise ValueError("choose the V2 settings object or the V1 timing object")
    overrides = legacy_overrides(profile["timing"]) if "timing" in profile else profile.get("settings", {})
    if not isinstance(overrides, dict):
        raise ValueError("profile settings must be a JSON object")
    for section, values in overrides.items():
        if section not in settings or section == "schema_version" or not isinstance(values, dict):
            raise ValueError(f"unknown or invalid settings section: {section}")
        for key, value in values.items():
            if key not in settings[section]:
                raise ValueError(f"unknown settings key: {section}.{key}")
            settings[section][key] = value
    validate_settings(settings)
    return settings


def check_window(schedule, instant):
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("--at needs an explicit UTC offset or Z")
    try:
        zone = ZoneInfo(schedule["timezone"])
    except ZoneInfoNotFoundError as error:
        raise ValueError(
            "IANA timezone unavailable: use a valid timezone and a host with IANA data "
            "(Python can use tzdata when the operating system has no database)"
        ) from error
    local = instant.astimezone(zone)
    weekday = local.isoweekday()
    previous_day = 7 if weekday == 1 else weekday - 1
    minute = local.hour * 60 + local.minute
    windows = schedule["weekly_windows"]
    for window in windows:
        start = clock_minutes(window["start"])
        end = clock_minutes(window["end"])
        days = window["weekdays"]
        if start < end and weekday in days and start <= minute < end:
            return {"local_time": local.isoformat(), "within_window": True}
        if end < start:
            if (weekday in days and minute >= start) or (previous_day in days and minute < end):
                return {"local_time": local.isoformat(), "within_window": True}
    return {"local_time": local.isoformat(), "within_window": not windows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, help="optional private V1 or V2 company profile")
    parser.add_argument("--at", help="evaluate the operating window at an ISO-8601 instant")
    args = parser.parse_args()
    try:
        settings = resolve_settings(read_object(args.profile) if args.profile else None)
        result = {"settings": settings, "timezone_check": "not_checked"}
        if args.at:
            instant_text = args.at[:-1] + "+00:00" if args.at.endswith("Z") else args.at
            instant = datetime.fromisoformat(instant_text)
            result["schedule_check"] = check_window(settings["schedule"], instant)
            result["timezone_check"] = "resolved"
    except (OSError, ValueError) as error:
        parser.exit(2, f"Settings error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
