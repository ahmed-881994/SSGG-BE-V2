from fastapi import HTTPException
from app.database.connectionmanager import connect


def update_event_attendance_db(event_id: int, body: dict):
    conn = connect()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            # check event exists
            cursor.callproc("GetEvent", [event_id])
            event_record = cursor.fetchone()
            
            # if event does not exists
            if event_record is None:
                raise HTTPException(
                    status_code=404, detail="Event not found")

            attendance_list = body.get("Attendance")

            for attendance in attendance_list:
                member_id = attendance.get("MemberID")
                attendance_state = attendance.get("AttendanceStateID")
                cursor.callproc("GetMember", [member_id])
                member = cursor.fetchone()
                
                # if member does not exists
                if member is None:
                    conn.rollback()
                    raise HTTPException(
                        status_code=404, detail="Event not found")

                cursor.callproc(
                    "TakeAttendance", [
                        member_id, event_id, attendance_state]
                )

            conn.commit()
            return {"message": "Attendance updated successfully"}
