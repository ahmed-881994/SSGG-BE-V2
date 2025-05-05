from fastapi import HTTPException
from app.database.connectionmanager import connect
from app.service.logging import insert_log

def get_team_attendance_db(team_id: int):
    conn = connect()

    if conn is not None:
        with conn as conn:
            # try:
                cursor = conn.cursor()
                args = [team_id]
                cursor.callproc("GetTeamAttendance", args)
                team_attendance = cursor.fetchall()
                if len(team_attendance) == 0:
                    raise HTTPException(status_code=404, detail="Attendance no found")
                else:
                    data = format_team_attendance_records(team_attendance)
                    return data
            # except Exception as error:
            #     raise HTTPException(status_code=500, detail=error.args)
            # finally:
                # insert_log(cursor, event, response, "GetMemberAttendance")
                conn.commit()

def format_team_attendance_records(records):
    result = []
    
    for record in records:
        # Check if an entry for this member already exists
        existing_entry = next(
            (
                entry
                for entry in result
                if entry.get("EventID") == record.get("event_id")
            ),
            None,
        )
        if existing_entry:
            # If it exists, append the attendance to the existing entry
            existing_entry["Attendance"].append({
                "MemberID": record.get('member_id'),
                "MemberNameEN": record.get('name_en'),
                "MemberNameAR": record.get('name_ar'),
                "AttendanceID": record.get('attendance_id'),
                "AttendanceStateID": record.get("attendance_state_id"),
                "AttendanceStateNameEN": record.get("attendance_state_name_en"),
                "AttendanceStateNameAR": record.get("attendance_state_name_ar")
            })
        else:
            # If it doesn't exist, create a new entry
            row = {
                "EventID": record.get('event_id'),
                "EventNameEN": record.get('event_name_en'),
                "EventNameAR": record.get('event_name_ar'),
                "EventStartDate": record.get("event_start_date"),
                "EventEndDate": record.get("event_end_date"),
                "EventTypeID": record.get("event_type_id"),
                "EventTypeNameEN": record.get("event_type_name_en"),
                "EventTypeNameAR": record.get("event_type_name_ar"),
                "Attendance": []
            }
            # Add attendance details to the new entry
            row["Attendance"].append({
                "MemberID": record.get('member_id'),
                "MemberNameEN": record.get('name_en'),
                "MemberNameAR": record.get('name_ar'),
                "AttendanceID": record.get('attendance_id'),
                "AttendanceStateID": record.get("attendance_state_id"),
                "AttendanceStateNameEN": record.get("attendance_state_name_en"),
                "AttendanceStateNameAR": record.get("attendance_state_name_ar")
            })
            # Append the new entry to the result list
            result.append(row)
    return result