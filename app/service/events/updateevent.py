from app.core.database_connection_pool import db_pool
from app.core.exceptions import EntityDoesNotExistError
from app.schema.events.events import EventCreate


def update_event_db(event_id: int, body: EventCreate):
    conn = db_pool.get_connection()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            # check event exists
            cursor.callproc("GetEvent", [event_id])
            eventRecord = cursor.fetchone()
            # if event exists
            if eventRecord is None:
                raise EntityDoesNotExistError(
                    message="Event not found", name=None)
            args = []
            args.append(body.event_type_id)
            args.append(body.name.en)
            args.append(body.name.ar)
            args.append(body.location)
            args.append(body.start_date)
            args.append(body.end_date)
            args.append(1 if body.is_multi_team == True else 0)
            args.append(body.team_id)
            cursor.callproc("UpdateEvent", args)
            conn.commit()
            return {"message": "Event updated"}
