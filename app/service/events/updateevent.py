from fastapi import HTTPException
from app.util.database import connect
from app.schema.events.events import EventCreate


def update_event_db(event_id: int, body: EventCreate):
    conn = connect()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            # check event exists
            cursor.callproc("GetEvent", [event_id])
            eventRecord = cursor.fetchone()
            # if event exists
            if eventRecord is None:
                raise HTTPException(
                    status_code=404, detail="Event not found")
            args = []
            args.append(body.event_type_id)
            args.append(body.name.en)
            args.append(body.name.ar)
            args.append(body.location)
            args.append(body.start_date)
            args.append(body.end_date)
            args.append(1 if body.is_multi_team== True else 0)
            args.append(body.team_id)
            cursor.callproc("UpdateEvent", args)
            conn.commit()
            return {"message": "Event updated"}
