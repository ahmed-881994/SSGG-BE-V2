"""
Consolidated event services
"""
from typing import List, Optional, Dict, Any
from app.core.exceptions import EntityDoesNotExistError
from app.core.config import logger
from app.core.database import get_connection
from app.core.database_connection_pool import db_pool
from app.schemas.events import Event, EventCreate, EventUpdate, EventAttendance, UpdateEventAttendance


def create_event_db(event: EventCreate) -> Dict[str, Any]:
    """Create a new event in the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        args = [
            event.event_type_id,
            event.name.en if event.name else None,
            event.name.ar if event.name else None,
            event.location,
            event.start_date,
            event.end_date,
            event.is_multi_team,
            event.team_id
        ]
        
        cursor.callproc("CreateEvent", args)
        result = cursor.fetchone()
        return result


def get_event_db(event_id: int) -> Dict[str, Any]:
    """Get event by ID from database"""
    conn = db_pool.get_connection()

    if conn is not None:
        try:
            with conn.cursor() as cursor:
                cursor.callproc("GetEvent", [event_id])
                records = cursor.fetchall()
                if records is not None and len(records) > 0:
                    logger.info(f"Found {len(records)} records for event ID: {event_id}")
                    data = format_event_records(records)
                    return data
                else:
                    logger.info(f"No records found for event ID: {event_id}")
                    raise EntityDoesNotExistError(
                        message="No events found with the provided criteria.", name=None)
        finally:
            db_pool.return_connection(conn)
    else:
        raise EntityDoesNotExistError(
            message="Database connection failed.", name=None)


def search_events_db(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search events based on criteria"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            # Implementation depends on your search stored procedure
            cursor.callproc("SearchEvents", [criteria])
            records = cursor.fetchall()
            return [format_event_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def update_event_db(event_id: int, event: EventCreate) -> Dict[str, Any]:
    """Update an existing event in the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        args = [
            event_id,
            event.event_type_id,
            event.name.en if event.name else None,
            event.name.ar if event.name else None,
            event.location,
            event.start_date,
            event.end_date,
            event.is_multi_team,
            event.team_id
        ]
        
        cursor.callproc("UpdateEvent", args)
        result = cursor.fetchone()
        return result


def get_event_attendance_db(event_id: int) -> List[Dict[str, Any]]:
    """Get event attendance records"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("GetEventAttendance", [event_id])
            records = cursor.fetchall()
            return [format_attendance_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def update_event_attendance_db(event_id: int, attendance: UpdateEventAttendance) -> Dict[str, Any]:
    """Update event attendance"""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Implementation depends on your stored procedure
        # This is a simplified example
        for item in attendance.attendance:
            args = [event_id, item.member_id, item.attendance_state_id]
            cursor.callproc("UpdateEventAttendance", args)
        
        result = {"message": "Attendance updated successfully"}
        return result


def format_event_records(records) -> Dict[str, Any]:
    """Format event records from database"""
    if not records:
        return {}
    
    main_record = records[0]
    formatted_entry = {
        'EventID': main_record.get('EventID'),
        'EventTypeID': main_record.get('EventTypeID'),
        'Name': {
            'EN': main_record.get('NameEN'),
            'AR': main_record.get('NameAR')
        },
        'Location': main_record.get('Location'),
        'StartDate': main_record.get('StartDate'),
        'EndDate': main_record.get('EndDate'),
        'IsMultiTeam': main_record.get('IsMultiTeam'),
        'TeamID': main_record.get('TeamID')
    }
    
    return formatted_entry


def format_event_record(record) -> Dict[str, Any]:
    """Format a single event record"""
    return {
        'EventID': record.get('EventID'),
        'EventTypeID': record.get('EventTypeID'),
        'Name': {
            'EN': record.get('NameEN'),
            'AR': record.get('NameAR')
        },
        'Location': record.get('Location'),
        'StartDate': record.get('StartDate'),
        'EndDate': record.get('EndDate'),
        'IsMultiTeam': record.get('IsMultiTeam'),
        'TeamID': record.get('TeamID')
    }


def format_attendance_record(record) -> Dict[str, Any]:
    """Format attendance record"""
    return {
        'Member': {
            'MemberID': record.get('MemberID'),
            'Name': {
                'EN': record.get('MemberNameEN'),
                'AR': record.get('MemberNameAR')
            }
        },
        'AttendanceID': record.get('AttendanceID'),
        'AttendanceStateID': record.get('AttendanceStateID'),
        'AttendanceStateName': {
            'EN': record.get('AttendanceStateNameEN'),
            'AR': record.get('AttendanceStateNameAR')
        }
    }
