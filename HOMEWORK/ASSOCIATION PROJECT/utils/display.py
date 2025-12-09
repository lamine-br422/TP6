from models.event import Event

def display_event_details(event: Event) -> str:
    return f"{event.event_name} | {event.event_date}"
