from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_user_in_token
from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.schemas.lookup_schema import LookupResponseSchema
from app.services.lookup_service import LookupService

router = APIRouter(prefix="/lookups", tags=["Lookups"], dependencies=[Depends(get_user_in_token)])


@router.get("", tags=["Lookups"], response_model=LookupResponseSchema)
def get_lookups(db: Session = Depends(get_db)):
    """
    Get all lookup tables and their values.
    """
    try:
        lookup_service = LookupService(db)
        return lookup_service.get_all_lookups()
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e.message))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")