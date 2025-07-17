from app.exceptions.exceptions import EntityDoesNotExistError
from app.util.database import get_connection


def get_member_attendance_db(member_id: str):
    """Gets member attendance by ID
    This method retrieves the attendance records of a member from the database using their member ID.

    Args:
        member_id (str): _description_

    Raises:
        EntityDoesNotExistError: _description_

    Returns:
        dict: Having the attendance records of the member.
    """
    conn = get_connection()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            args = [member_id]
            cursor.callproc("GetMember", args)
            memberRecord = cursor.fetchone()
            if memberRecord is None or len(memberRecord) == 0:
                raise EntityDoesNotExistError(
                    message="Member not found.", name=None)
            cursor.callproc("GetMemberAttendance", args)
            records = cursor.fetchall()
            if records is None or len(records) == 0:
                raise EntityDoesNotExistError(
                    message="No attendance records found for the provided member ID.", name=None)
            conn.commit()
            return format_member_attendance_records(records)
            # insert_log(cursor, event, response, "GetMemberAttendance")


def format_member_attendance_records(records):
    result = []
    for record in records:
        entry = {
            "EventID": record.get('event_id'),
            "EventNameEN": record.get('event_id'),
            "EventNameEN": record.get('event_name_en'),
            "EventNameAR": record.get('event_name_ar'),
            "EventStartDate": record.get("event_start_date"),
            "EventEndDate": record.get("event_end_date"),
            "EventTypeNameEN": record.get("event_type_name_en"),
            "EventTypeNameAR": record.get("event_type_name_ar"),
            "AttendanceStateNameEN": record.get("attendance_state_name_en"),
            "AttendanceStateNameAR": record.get("attendance_state_name_ar"),
        }
        result.append(entry)
    return result
