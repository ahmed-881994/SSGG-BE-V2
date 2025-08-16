"""
Consolidated entity services
"""
from typing import List, Optional, Dict, Any
from app.core.exceptions import EntityDoesNotExistError
from app.core.config import logger
from app.core.database import get_connection
from app.core.database_connection_pool import db_pool
from app.schemas.entities import (
    Entity, EntityCreate, EntityUpdate, SearchEntitiesResponse,
    CreateEntityRequest, AddEntityMemberRequest, EntityTransfer,
    UpdateEntityMemberRoleRequest
)


def search_entities_db(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search entities based on criteria"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("SearchEntities", [criteria])
            records = cursor.fetchall()
            return [format_entity_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def create_entity_db(entity: CreateEntityRequest) -> Dict[str, Any]:
    """Create a new entity in the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        args = [
            entity.entity_name.en if entity.entity_name else None,
            entity.entity_name.ar if entity.entity_name else None,
            entity.parent_entity_id,
            entity.entity_type_id
        ]
        
        cursor.callproc("CreateEntity", args)
        result = cursor.fetchone()
        return result


def transfer_entity_members_db(transfers: List[EntityTransfer]) -> Dict[str, Any]:
    """Transfer members between entities"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        for transfer in transfers:
            args = [
                transfer.member_id,
                transfer.from_entity_id,
                transfer.to_entity_id,
                transfer.transfer_date
            ]
            cursor.callproc("TransferEntityMember", args)
        
        result = {"message": "Transfers completed successfully"}
        return result


def get_entity_members_db(entity_id: int) -> List[Dict[str, Any]]:
    """Get members of an entity"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("GetEntityMembers", [entity_id])
            records = cursor.fetchall()
            return [format_member_record(record) for record in records]
    finally:
        db_pool.return_connection(conn)


def add_entity_member_db(members: List[AddEntityMemberRequest], entity_id: int) -> Dict[str, Any]:
    """Add members to an entity"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        for member in members:
            args = [
                entity_id,
                member.member_id,
                member.role_id,
                member.from_date,
                member.to_date
            ]
            cursor.callproc("AddEntityMember", args)
        
        result = {"message": "Members added successfully"}
        return result


def update_entity_member_role_db(entity_id: int, update_request: UpdateEntityMemberRoleRequest) -> Dict[str, Any]:
    """Update entity member role"""
    with get_connection() as conn:
        cursor = conn.cursor()
        args = [
            entity_id,
            update_request.member_id,
            update_request.role_id,
            update_request.from_date,
            update_request.to_date
        ]
        
        cursor.callproc("UpdateEntityMemberRole", args)
        result = cursor.fetchone()
        return result


def format_entity_record(record) -> Dict[str, Any]:
    """Format a single entity record"""
    return {
        'EntityID': record.get('EntityID'),
        'EntityName': {
            'EN': record.get('EntityNameEN'),
            'AR': record.get('EntityNameAR')
        },
        'ParentEntityID': record.get('ParentEntityID'),
        'EntityTypeID': record.get('EntityTypeID')
    }


def format_member_record(record) -> Dict[str, Any]:
    """Format a member record"""
    return {
        'MemberID': record.get('MemberID'),
        'Name': {
            'EN': record.get('MemberNameEN'),
            'AR': record.get('MemberNameAR')
        },
        'MemberRole': {
            'EN': record.get('RoleNameEN'),
            'AR': record.get('RoleNameAR')
        }
    }
