from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.schemas.member_schema import (MemberAttendanceResponse, MemberCreateRequest, MemberUpdateRequest,
                                       MemberResponse, SearchMembersResponse)
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["Members"], dependencies=[Depends(get_user_in_token)])


@router.get("", tags=["Members"], response_model=SearchMembersResponse, responses={
    200: {"description": "Success", "model": SearchMembersResponse}})
def search_members(name: Optional[str] = None, entityID: Optional[int] = None, db: Session = Depends(get_db_session)):
    """
    Search members by (Name, Entity)
    """
    try:
        member_service = MemberService(db)
        return member_service.search_members(name=name, entity_id=entityID)
    except EntityDoesNotExistError as e:
        logger.error(f"No members found matching criteria: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='No members found matching criteria')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')


@router.post("", status_code=201, responses={
    201: {"description": "Member created successfully", "model": MemberResponse}})
def create_member(body: MemberCreateRequest, db: Session = Depends(get_db_session)):
    """
    Creates a new member
    """
    try:
        member_service = MemberService(db)
        return member_service.create_member(body.model_dump())
    except EntityAlreadyExistsError as e:
        logger.error(f"Member already exists: {e.message}", exc_info=True)
        raise HTTPException(status_code=400, detail='Member already exists')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')


@router.get("/{member_id}", response_model=MemberResponse, responses={
    200: {"description": "Success", "model": MemberResponse}})
def get_member(member_id: str, db: Session = Depends(get_db_session)):
    """
    Get Member by ID
    """
    try:
        member_service = MemberService(db)
        return member_service.get_member_by_member_id(member_id)
    except EntityDoesNotExistError as e:
        logger.error(f"Member not found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Member not found')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')


@router.put("/{member_id}", response_model=MemberResponse, responses={
    200: {"description": "Member updated successfully", "model": MemberResponse}})
def update_member(member_id: str, body: MemberUpdateRequest, db: Session = Depends(get_db_session)):
    """
    Updates a member
    """
    try:
        member_service = MemberService(db)
        return member_service.update_member(member_id, body.model_dump( exclude_none=True))
    except EntityDoesNotExistError as e:
        logger.error(f"Member not found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Member not found')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')
    

@router.delete("/{member_id}", status_code=204, responses={
    204: {"description": "No Content"}})
def delete_member(member_id: str, db: Session = Depends(get_db_session)):
    """
    Deletes a member
    """
    try:
        member_service = MemberService(db)
        member_service.delete_member(member_id)
    except EntityDoesNotExistError as e:
        logger.error(f"Member not found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Member not found')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')


@router.get("/{member_id}/attendance",response_model=MemberAttendanceResponse)
def get_member_attendance(member_id: str, db: Session = Depends(get_db_session)):
    """
    Gets member attendance by ID
    """
    try:
        member_service = MemberService(db)
        return member_service.get_member_attendance(member_id)
    except EntityDoesNotExistError as e:
        logger.error(f"Member not found: {e.message}", exc_info=True)
        raise HTTPException(status_code=404, detail='Member not found')
    except ServiceError as e:
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail='Service error')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Unexpected error')
