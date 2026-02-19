import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Scopes required for Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Builds and returns a Google Calendar service object."""
    creds_path = 'credentials.json'
    if not os.path.exists(creds_path):
        print(f"WARNING: {creds_path} not found. Calendar integration disabled.")
        return None
    
    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"ERROR: Failed to initialize Google Calendar service: {e}")
        return None

def create_calendar_event(booking):
    """
    Creates an event on the Google Calendar.
    'booking' should be a dictionary or object with:
    full_name, car_category, pickup_date_time, return_date_time, pickup_location, dropoff_location
    """
    service = get_calendar_service()
    if not service:
        return None

    # The Calendar ID where events will be added (Primary or a specific ID)
    # Defaulting to 'primary' for the service account's own calendar
    # In a real scenario, you'd share a specific calendar with the service account email
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')

    # Convert "YYYY-MM-DD HH:MM" to ISO format
    try:
        start_dt = datetime.datetime.strptime(booking.pickup_date_time, "%Y-%m-%d %H:%M").isoformat()
        end_dt = datetime.datetime.strptime(booking.return_date_time, "%Y-%m-%d %H:%M").isoformat()
    except Exception as e:
        print(f"ERROR: Date parsing failed for calendar event: {e}")
        return None

    event = {
        'summary': f'🚗 Renta Car Booking: {booking.full_name}',
        'location': f'Pickup: {booking.pickup_location} | Dropoff: {booking.dropoff_location}',
        'description': f'Car Category: {booking.car_category}\nReference: {booking.booking_reference}\nPhone: {booking.phone_number}',
        'start': {
            'dateTime': start_dt,
            'timeZone': 'UTC', # Adjust to user's timezone if needed
        },
        'end': {
            'dateTime': end_dt,
            'timeZone': 'UTC',
        },
    }

    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except Exception as e:
        print(f"ERROR: Failed to create calendar event: {e}")
        return None
