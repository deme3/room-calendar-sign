from flask import Flask, render_template
from flask_socketio import SocketIO
from pathlib import Path
import calendar_sign.constants as constants
import calendar_sign.app_data as app_data
from calendar_sign.logging import logger
from datetime import datetime, timezone, timedelta
import locale

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

app = Flask(__name__, static_url_path="", static_folder='static/')
socketio = SocketIO(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
FRONTEND_PATH = Path(__file__).parent.resolve() / 'frontend'

@app.context_processor
def inject_now():
  return {'now': datetime.utcnow().replace(tzinfo=timezone.utc)}

@app.route('/')
@app.route('/sign')
def sign():
  now = datetime.utcnow().replace(tzinfo=timezone.utc)
  is_occupied_now = app_data.latest_event is not None and app_data.latest_event.start_time <= now <= app_data.latest_event.end_time
  event_in_30mins = app_data.latest_event is not None and app_data.latest_event.start_time <= now + timedelta(minutes=30) <= app_data.latest_event.end_time
  event_just_finished = app_data.latest_event is not None and now - timedelta(hours=1) <= app_data.latest_event.end_time <= now

  status_class = "available"

  if is_occupied_now:
    status_class = "occupied"
  elif event_in_30mins:
    status_class = "almost-occupied"
  elif event_just_finished:
    status_class = "just-finished"

  return render_template('index.html', room_name=constants.ROOM_NAME, latest_event=app_data.latest_event, upcoming_events=app_data.upcoming_events, occupied=is_occupied_now, almost_occupied=event_in_30mins, event_just_finished=event_just_finished, status_class=status_class)


@socketio.on('connect')
def on_connect():
  logger.info('Client connected to WebSocket')


@socketio.on('disconnect')
def on_disconnect():
  logger.info('Client disconnected from WebSocket')


@socketio.on('update')
def on_update():
  logger.info('Client requested update')
  now = datetime.utcnow().replace(tzinfo=timezone.utc)
  is_occupied_now = app_data.latest_event is not None and app_data.latest_event.start_time <= now <= app_data.latest_event.end_time
  event_in_30mins = app_data.latest_event is not None and app_data.latest_event.start_time <= now + timedelta(minutes=30) <= app_data.latest_event.end_time
  event_just_finished = app_data.latest_event is not None and now - timedelta(hours=1) <= app_data.latest_event.end_time <= now

  output = {
    'latest_event': app_data.latest_event.__dict__() if app_data.latest_event is not None else None,
    'upcoming_events': [x.__dict__() for x in app_data.upcoming_events] if len(app_data.upcoming_events) > 0 else [],
    'occupied': is_occupied_now,
    'almost_occupied': event_in_30mins,
    'just_finished': event_just_finished,
    'available': not is_occupied_now and not event_in_30mins and not event_just_finished
  }

  logger.debug(output)

  socketio.emit('message', output)

if __name__ == '__main__':
  app.run()
