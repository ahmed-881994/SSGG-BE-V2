"""
Consolidated member services
"""
from typing import List, Optional, Dict, Any
from app.core.exceptions import EntityDoesNotExistError
from app.core.config import logger
from app.core.database import get_connection
from app.core.database_connection_pool import db_pool
from app.schemas.members import MemberGet, MemberCreate, MemberUpdate, MemberAttendance


def get_member_db(member_id: str) -> Dict[str, Any]:
    """Get member by ID from database"""
    conn = db_pool.get_connection()

    if conn is not None:
        try:
            with conn.cursor() as cursor:
                cursor.callproc("GetMember", [member_id])
                records = cursor.fetchall()
                if records is not None and len(records) > 0:
                    logger.info(f"Found {len(records)} records for member ID: {member_id}")
                    data = format_member_records(records)
                    logger.info(f"member data: {data}")
                    return data
                else:
                    logger.info(f"No records found for member ID: {member_id}")
                    raise EntityDoesNotExistError(
                        message="No members found with the provided criteria.", name=None)
        finally:
            db_pool.return_connection(conn)
    else:
        raise EntityDoesNotExistError(
            message="Database connection failed.", name=None)


def add_member_db(member: MemberCreate) -> Dict[str, Any]:
    """Add a new member to the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        args = [
            member.member_id,
            member.name.en if member.name and hasattr(member.name, 'en') else None,
            member.name.ar if member.name and hasattr(member.name, 'ar') else None,
            member.place_of_birth,
            member.date_of_birth,
            member.address,
            str(member.national_id_no) if member.national_id_no else None,
            str(member.club_id_no) if member.club_id_no else None,
            str(member.passport_no) if member.passport_no else None,
            member.date_joined,
            str(member.mobile_no) if member.mobile_no else None,
            str(member.home_contact) if member.home_contact else None,
            member.email,
            member.facebook_url,
            member.school_name,
            member.education_type,
            member.father_name,
            str(member.father_contact) if member.father_contact else None,
            member.father_job,
            member.mother_name,
            str(member.mother_contact) if member.mother_contact else None,
            member.mother_job,
            member.guardian_name,
            str(member.guardian_contact) if member.guardian_contact else None,
            member.guardian_relationship,
            member.hobbies,
            member.health_issues,
            member.medications,
            member.qr_code_url,
            member.image_url,
            member.national_id_url,
            member.parent_national_id_url,
            member.club_id_url,
            member.passport_url,
            member.birth_certificate_url,
            member.photo_consent,
            member.conditions_consent
        ]
        
        cursor.callproc("AddMember", args)
        result = cursor.fetchone()
        return result


def update_member_db(member_id: str, member: MemberUpdate) -> Dict[str, Any]:
    """Update an existing member in the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Similar implementation to add_member_db but for updates
        # Implementation would depend on your stored procedure
        cursor.callproc("UpdateMember", [member_id, ...])
        result = cursor.fetchone()
        return result


def search_members_db(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search members based on criteria"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            # Implementation depends on your search stored procedure
            cursor.callproc("SearchMembers", [criteria])
            records = cursor.fetchall()
            return [format_member_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def get_member_attendance_db(member_id: str) -> List[Dict[str, Any]]:
    """Get member attendance records"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("GetMemberAttendance", [member_id])
            records = cursor.fetchall()
            return [format_attendance_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def format_member_records(records) -> Dict[str, Any]:
    """Format member records from database"""
    # Implementation would depend on your database structure
    # This is a placeholder - you'd need to implement based on your actual data format
    if not records:
        return {}
    
    # Assuming the first record contains the main member data
    main_record = records[0]
    formatted_entry = {
        'MemberID': main_record.get('MemberID'),
        'Name': {
            'EN': main_record.get('NameEN'),
            'AR': main_record.get('NameAR')
        },
        # ... other fields based on your database structure
    }
    
    return formatted_entry


def format_member_record(record) -> Dict[str, Any]:
    """Format a single member record"""
    return {
        'MemberID': record.get('MemberID'),
        'Name': {
            'EN': record.get('NameEN'),
            'AR': record.get('NameAR')
        },
        # ... other fields
    }


def format_attendance_record(record) -> Dict[str, Any]:
    """Format attendance record"""
    return {
        'EventID': record.get('EventID'),
        'EventName': {
            'EN': record.get('EventNameEN'),
            'AR': record.get('EventNameAR')
        },
        # ... other fields
    }
