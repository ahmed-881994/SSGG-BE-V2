from app.exceptions.exceptions import EntityDoesNotExistError
from app.schema.events.events import UpdateEventAttendance
from app.util.database import get_connection


def update_event_attendance_db(event_id: int, body: UpdateEventAttendance):
    conn = get_connection()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            # check event exists
            cursor.callproc("GetEvent", [event_id])
            event_record = cursor.fetchone()

            # if event does not exists
            if event_record is None:
                raise EntityDoesNotExistError(
                    message="Event not found", name=None)

            attendance_list = body.attendance

            for attendance in attendance_list:
                member_id = attendance.member_id
                attendance_state = attendance.attendance_state_id
                cursor.callproc("GetMember", [member_id])
                member = cursor.fetchone()

                # if member does not exists
                if member is None:
                    conn.rollback()
                    raise EntityDoesNotExistError(
                        message="Member not found", name=None)

                cursor.callproc(
                    "TakeAttendance", [
                        member_id, event_id, attendance_state]
                )

            conn.commit()
            return {"message": "Attendance updated successfully"}
