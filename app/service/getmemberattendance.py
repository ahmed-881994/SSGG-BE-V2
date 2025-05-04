from typing import Any
from fastapi import HTTPException
from app.database.connectionmanager import connect
from app.service.logging import insert_log


def get_member_attendance_db(member_id: str):
    """Gets member attendance by ID
    This method retrieves the attendance records of a member from the database using their member ID.

    Args:
        member_id (str): _description_

    Raises:
        HTTPException: _description_

    Returns:
        tuple: A tuple containing result code and the attendance records of the member if found.

    """
    conn = connect()

    if conn is not None:
        with conn as conn:
            try:
                cursor = conn.cursor()
                args = [member_id]
                cursor.callproc("GetMember", args)
                memberRecord = cursor.fetchone()
                if memberRecord:
                    cursor.callproc("GetMemberAttendance", args)
                    records = cursor.fetchall()
                    if len(records) == 0:
                        return (-2, None)
                    else:
                        return (0, records)
                else:
                    return (-1, None)
            except Exception as error:
                raise HTTPException(status_code=500, detail=error.args)
            finally:
                # insert_log(cursor, event, response, "GetMemberAttendance")
                conn.commit()


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
