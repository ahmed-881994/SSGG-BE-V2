"""
Consolidated team services
"""
from typing import List, Optional, Dict, Any
from app.core.exceptions import EntityDoesNotExistError
from app.core.config import logger
from app.core.database import get_connection
from app.core.database_connection_pool import db_pool
from app.schemas.teams import Team, TeamCreate, TeamAdd, TeamTransfer, TeamAttendance


def search_teams_db(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search teams based on criteria"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("SearchTeams", [criteria])
            records = cursor.fetchall()
            return [format_team_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def transfer_team_members_db(transfers: List[TeamTransfer]) -> Dict[str, Any]:
    """Transfer members between teams"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        for transfer in transfers:
            args = [
                transfer.member_id,
                transfer.from_team_id,
                transfer.to_team_id,
                transfer.transfer_date
            ]
            cursor.callproc("TransferTeamMember", args)
        
        result = {"message": "Transfers completed successfully"}
        return result


def get_team_members_db(team_id: int) -> List[Dict[str, Any]]:
    """Get members of a team"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("GetTeamMembers", [team_id])
            records = cursor.fetchall()
            return [format_member_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def add_team_member_db(team_id: int, members: List[TeamAdd]) -> Dict[str, Any]:
    """Add members to a team"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        for member in members:
            args = [
                team_id,
                member.member_id,
                member.date_joined
            ]
            cursor.callproc("AddTeamMember", args)
        
        result = {"message": "Members added successfully"}
        return result


def get_team_attendance_db(team_id: int) -> List[Dict[str, Any]]:
    """Get team attendance records"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("GetTeamAttendance", [team_id])
            records = cursor.fetchall()
            return [format_attendance_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def format_team_record(record) -> Dict[str, Any]:
    """Format a single team record"""
    return {
        'TeamID': record.get('TeamID'),
        'TeamName': {
            'EN': record.get('TeamNameEN'),
            'AR': record.get('TeamNameAR')
        },
        'Description': record.get('Description')
    }


def format_member_record(record) -> Dict[str, Any]:
    """Format a member record"""
    return {
        'MemberID': record.get('MemberID'),
        'Name': {
            'EN': record.get('MemberNameEN'),
            'AR': record.get('MemberNameAR')
        },
        'DateJoined': record.get('DateJoined'),
        'DateTransferred': record.get('DateTransferred'),
        'IsCurrentTeam': record.get('IsCurrentTeam')
    }


def format_attendance_record(record) -> Dict[str, Any]:
    """Format attendance record"""
    return {
        'MemberID': record.get('MemberID'),
        'MemberName': {
            'EN': record.get('MemberNameEN'),
            'AR': record.get('MemberNameAR')
        },
        'AttendanceCount': record.get('AttendanceCount'),
        'TotalEvents': record.get('TotalEvents')
    }
