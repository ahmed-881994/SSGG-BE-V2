from app.exceptions.exceptions import EntityDoesNotExistError
from app.util.database import connect


def get_event_attendance_db(event_id: int):
    conn = connect()
    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            args = [event_id]
            cursor.callproc("GetEventAttendance", args)
            records = cursor.fetchall()
            if records is None or len(records) == 0:
                raise EntityDoesNotExistError(
                    message="Attendance not found", name=None)
            conn.commit()
            return format_event_attendance_records(records)


def format_event_attendance_records(records):
    result = {}
    result['EventID'] = records[0].get('event_id')
    result['Attendance'] = []
    for record in records:
        entry = {
            "Member": {
                "MemberID": record.get("member_id"),
                "Name": {"EN": record.get("member_name_en"), "AR": record.get("member_name_ar")},
            },
            "AttendanceID": record.get("attendance_id"),
            "AttendanceStateID": record.get("attendance_state_id"),
            "AttendanceStateName": {"EN": record.get("attendance_state_name_en"), "AR": record.get("attendance_state_name_ar")},
        }
        result['Attendance'].append(entry)
    return result
