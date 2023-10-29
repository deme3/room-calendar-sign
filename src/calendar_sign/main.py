from __future__ import print_function
from pathlib import Path

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from calendar_sign.calendar_event import CalendarEvent
import calendar_sign.calendar_event as calendar_utils
import calendar_sign.web_server as web_server
import calendar_sign.app_data as app_data
from calendar_sign.logging import logger
import calendar_sign.utils as utils

import threading
import atexit

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

THIS_SCRIPT_DIR = Path(__file__).parent.resolve()
CREDENTIALS_PATH = str(THIS_SCRIPT_DIR / 'credentials.json')
TOKEN_PATH = str(THIS_SCRIPT_DIR / 'token.json')

active_service = None
latest_events = []

def initialise_service():
    """Initialises the Google Calendar API service.

    Returns:
        service: The Google Calendar API service.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    
    logger.info('Successfully authenticated with Google Calendar API.')
    return build('calendar', 'v3', credentials=creds)


def update_calendar_data(use_service=None):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    try:
        service = initialise_service() if use_service is None else use_service

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        now = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        oneyearago = (datetime.datetime.utcnow() - datetime.timedelta(days=365)).isoformat() + 'Z'
        
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        # Create a list of CalendarEvent objects
        calendar_events = []
        for event in events:
            start = calendar_utils.datetime_from_calendar(event['start'])
            end = calendar_utils.datetime_from_calendar(event['end'])
            calendar_events.append(CalendarEvent(event['summary'], start, end))
        
        calendar_events = sorted(calendar_events, key=lambda event: event.start_time)

        app_data.latest_event = calendar_events[0] if len(calendar_events) > 0 else None
        
        if not utils.is_occurring(app_data.latest_event):
            app_data.upcoming_events = calendar_events
        else:
            app_data.upcoming_events = calendar_events[1:] if len(calendar_events) > 1 else []
        logger.info('Upcoming events: %s' % app_data.upcoming_events)

        web_server.on_update()
        return calendar_events
    except HttpError as error:
        logger.error('An error occurred: %s' % error)


def main():
    active_service = initialise_service()

    def update_calendar_data_thread():
        update_calendar_data(use_service=active_service)
        logger.info('Fetched calendar data.')

        threading.Timer(10.0, update_calendar_data_thread).start()

    update_calendar_data_thread()
    web_server.socketio.run(web_server.app, port=8080, host='0.0.0.0')


if __name__ == '__main__':
    main()
