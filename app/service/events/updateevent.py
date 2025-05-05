from fastapi import HTTPException
from app.database.connectionmanager import connect


def update_event_db(event_id: int, body: dict):
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
            args.append(event_id)
            args.append(body.get("EventTypeID"))
            args.append(body.get("EventName").get("EN"))
            args.append(body.get("EventName").get("AR"))
            args.append(body.get("EventLocation"))
            args.append(body.get("EventStartDate"))
            args.append(body.get("EventEndDate"))
            args.append(1 if body.get("IsMultiTeam") == True else 0)
            args.append(body.get("TeamID"))
            cursor.callproc("UpdateEvent", args)
            conn.commit()
            return {"message": "Event updated"}
