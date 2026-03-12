from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta, timezone
from typing import Any

import caldav


@dataclass
class Event:
    summary: str
    start: datetime | None
    end: datetime | None
    location: str
    description: str
    organizer: str
    attendees: list[str]
    url: str
    _raw: Any = field(default=None, repr=False)


def _parse_dt(val) -> datetime | None:
    if val is None:
        return None
    dt = val.value
    if isinstance(dt, datetime):
        return dt
    if isinstance(dt, date):
        return datetime(dt.year, dt.month, dt.day)
    return None


def get_today_events(email: str, token: str) -> list[Event]:
    """Connect to Yandex CalDAV and return today's events across all calendars."""
    client = caldav.DAVClient(
        url="https://caldav.yandex.ru/",
        username=email,
        password=token,
    )
    principal = client.principal()
    calendars = principal.calendars()

    today = date.today()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    events: list[Event] = []

    for cal in calendars:
        try:
            results = cal.date_search(start=start, end=end, expand=True)
        except Exception:
            continue

        for item in results:
            try:
                vevent = item.vobject_instance.vevent
            except Exception:
                continue

            summary = str(vevent.summary.value) if hasattr(vevent, "summary") else "(no title)"
            location = str(vevent.location.value) if hasattr(vevent, "location") else ""
            description = str(vevent.description.value) if hasattr(vevent, "description") else ""
            ev_start = _parse_dt(vevent.dtstart) if hasattr(vevent, "dtstart") else None
            ev_end = _parse_dt(vevent.dtend) if hasattr(vevent, "dtend") else None
            url = str(vevent.url.value) if hasattr(vevent, "url") else ""

            organizer = ""
            if hasattr(vevent, "organizer"):
                org_val = vevent.organizer.value or ""
                organizer = org_val.replace("mailto:", "")

            attendees: list[str] = []
            for a in vevent.contents.get("attendee", []):
                addr = (a.value or "").replace("mailto:", "")
                if addr:
                    attendees.append(addr)

            events.append(Event(
                summary=summary, start=ev_start, end=ev_end, location=location,
                description=description, organizer=organizer, attendees=attendees, url=url,
                _raw=item,
            ))

    events.sort(key=lambda e: e.start or datetime.min)
    return events


def delete_event(event: Event) -> None:
    """Delete an event from the server."""
    event._raw.delete()


def remove_attendee(event: Event, attendee_email: str) -> None:
    """Remove an attendee from the event and save to the server."""
    vevent = event._raw.vobject_instance.vevent
    existing = vevent.contents.get("attendee", [])
    if not existing:
        return

    target = f"mailto:{attendee_email}"
    updated = [a for a in existing if (a.value or "") != target]
    vevent.contents["attendee"] = updated

    event._raw.save()
    event.attendees = [
        (a.value or "").replace("mailto:", "")
        for a in updated
        if (a.value or "").replace("mailto:", "")
    ]
