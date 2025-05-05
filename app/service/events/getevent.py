from fastapi import HTTPException
from app.database.connectionmanager import connect


def get_event_db(event_id: int):
    conn = connect()
    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            args = [event_id]
            cursor.callproc("GetEvent", args)
            records = cursor.fetchone()
            if records is None or len(records) == 0:
                raise HTTPException(status_code=404, detail="Event not found")
            conn.commit()
            return format_event_record(records)


def format_event_record(record):
    entry = {
        "EventID": record.get("event_id"),
        "EventName": {
            "EN": record.get("event_name_en"),
            "AR": record.get("event_name_ar"),
        },
        "EventLocation": record.get("event_location"),
        "EventStartDate": record.get("event_start_date"),
        "EventEndDate": record.get("event_end_date"),
        "IsMultiTeam": True if record.get("is_multi_team") == 1 else False,
        "TeamID": record.get("team_id"),
    }
    return entry
