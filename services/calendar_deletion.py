from calendar_setup import get_calendar_service



service = get_calendar_service()

list_of_calendars = service.calendarList().list().execute()

print(list_of_calendars)

def delete_all_events(calendar_id):
    page_token = None

    while True:
        events = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
        for event in events.get('items', []):
            try:
                service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
                print(f"Deleted event: {event['summary'] if 'summary' in event else event['id']}")
            except Exception as e:
                print(f"Failed to delete event {event['id']}: {e}")

        page_token = events.get('nextPageToken')
        if not page_token:
            break


for calendar in list_of_calendars.get('items', []):
    calendar_id = calendar['id']

    print(f"deleting calendar {calendar.get('summary')}")
    try:
        service.calendars().delete(calendarId=calendar_id).execute()
        delete_all_events(calendar_id)
        print('haha')
    except Exception as e:
        print(e)




