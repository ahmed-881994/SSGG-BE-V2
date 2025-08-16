from typing import Optional

from app.core.database_connection_pool import db_pool
from app.core.exceptions import EntityDoesNotExistError


def search_events_db(team_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, event_name: Optional[str] = None):
    conn = db_pool.get_connection()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            cursor.callproc("SearchEvents", [
                            team_id, event_name, start_date, end_date])
            records = cursor.fetchall()

            if records is None or len(records) == 0:
                raise EntityDoesNotExistError(
                    message="No events found", name=None)

            conn.commit()
            return format_events_records(records)


def format_events_records(records):
    formatted_entries = []

    for record in records:
        entry = {
            "EventID": record.get("event_id"),
            "EventTypeID": record.get("event_type_id"),
            "Name": {
                "EN": record.get("event_name_en"),
                "AR": record.get("event_name_ar"),
            },
            "Location": record.get("event_location"),
            "StartDate": str(record.get("event_start_date")),
            "EndDate": str(record.get("event_end_date")),
            "IsMultiTeam": True if record.get("is_multi_team") == 1 else False,
            "TeamID": record.get("team_id"),
        }
        formatted_entries.append(entry)

    return formatted_entries
