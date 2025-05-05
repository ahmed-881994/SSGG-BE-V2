from fastapi import HTTPException
from app.database.connectionmanager import connect


def create_event_db(body: dict):
    conn = connect()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            args = []
            args.append(body.get("EventTypeID"))
            args.append(body.get("EventName").get("EN"))
            args.append(body.get("EventName").get("AR"))
            args.append(body.get("EventLocation"))
            args.append(body.get("EventStartDate"))
            args.append(body.get("EventEndDate"))
            args.append(1 if body.get("IsMultiTeam") == True else 0)
            args.append(body.get("TeamID"))

            cursor.callproc("CreateEvent", args)
            conn.commit()
            event_record = cursor.fetchone()
            if event_record is None or event_record.get("event_id") is None:
                raise HTTPException(
                    status_code=500, detail="Error creating event")
            return {"EventID": event_record.get("event_id")}
