from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_user_in_token
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.schemas.member_schema import (MemberRequest, MemberResponse,
                                       SearchMembersResponse)
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["Members"], dependencies=[Depends(get_user_in_token)])


@router.get("", tags=["Members"], response_model=SearchMembersResponse, responses={
    200: {"description": "Success", "model": SearchMembersResponse}})
def search_members(name: Optional[str] = None, entityID: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Search members by (Name, Entity)
    """
    try:
        member_service = MemberService(db)
        return member_service.search_members(name=name, entity_id=entityID)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("", status_code=201, responses={
    201: {"description": "Member created successfully", "model": MemberResponse}})
def create_member(body: MemberRequest, db: Session = Depends(get_db)):
    """
    Creates a new member
    """
    try:
        member_service = MemberService(db)
        return member_service.create_member(body.model_dump())
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{member_id}", response_model=MemberResponse, responses={
    200: {"description": "Success", "model": MemberResponse}})
def get_member(member_id: str, db: Session = Depends(get_db)):
    """
    Get Member by ID
    """
    try:
        member_service = MemberService(db)
        return member_service.get_member_by_member_id(member_id)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.put("/{member_id}", response_model=MemberResponse, responses={
    200: {"description": "Member updated successfully", "model": MemberResponse}})
def update_member(member_id: str, body: MemberRequest, db: Session = Depends(get_db)):
    """
    Updates a member
    """
    try:
        member_service = MemberService(db)
        return member_service.update_member(member_id, body.model_dump( exclude_none=True))
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

@router.delete("/{member_id}", status_code=204, responses={
    204: {"description": "No Content"}})
def delete_member(member_id: str, db: Session = Depends(get_db)):
    """
    Deletes a member
    """
    try:
        member_service = MemberService(db)
        member_service.delete_member(member_id)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{member_id}/attendance", responses={
    200: {"description": "Success", "model": dict}})
def get_member_attendance(member_id: str):
    """
    Gets member attendance by ID (To be implemented)
    """
    pass
