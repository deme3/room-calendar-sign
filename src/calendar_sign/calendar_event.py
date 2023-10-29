from datetime import datetime
from dataclasses import dataclass

@dataclass
class CalendarEvent:
  event_name: str
  start_time: datetime
  end_time: datetime

  def __dict__(self):
    return {
      'event_name': self.event_name,
      'start_time': self.start_time.isoformat(),
      'end_time': self.end_time.isoformat()
    }


def datetime_from_calendar(calendar_datetime: object):
  return datetime.strptime(calendar_datetime['dateTime'], '%Y-%m-%dT%H:%M:%S%z')