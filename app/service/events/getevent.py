from app.core.database_connection_pool import db_pool
from app.core.exceptions import EntityDoesNotExistError


def get_event_db(event_id: int):
    conn = db_pool.get_connection()
    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            args = [event_id]
            cursor.callproc("GetEvent", args)
            records = cursor.fetchone()
            if records is None or len(records) == 0:
                raise EntityDoesNotExistError(
                    message="Event not found", name=None)
            conn.commit()
            return format_event_record(records)


def format_event_record(record):
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
    return entry
