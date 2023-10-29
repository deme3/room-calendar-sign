from datetime import datetime, timedelta, timezone
from calendar_sign.calendar_event import CalendarEvent

def is_occurring(event: CalendarEvent) -> bool:
  if event is None: return False
  now = datetime.utcnow().replace(tzinfo=timezone.utc)
  return event.start_time <= now <= event.end_time

def is_upcoming(event: CalendarEvent) -> bool:
  if event is None: return False
  now = datetime.utcnow().replace(tzinfo=timezone.utc)
  return event.start_time <= now + timedelta(minutes=30) <= event.end_time

def just_finished(event: CalendarEvent) -> bool:
  if event is None: return False
  now = datetime.utcnow().replace(tzinfo=timezone.utc)
  return now - timedelta(hours=1) <= event.end_time <= now