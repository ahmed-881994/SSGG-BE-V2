from fastapi import APIRouter, Depends
from pymysql import MySQLError

from app.exceptions.exceptions import ServiceError
from app.schema.lookups.lookups import Lookup
from app.service.auth.users import get_current_active_user
from app.service.lookups.getlookups import get_lookups as get_lookups_service

router = APIRouter(prefix="/lookups", tags=["Lookups"], dependencies=[Depends(get_current_active_user)])


@router.get("", tags=["Lookups"], responses={
    200: {"description": "Success", "model": Lookup}})
def get_lookups():
    """
    Get all lookup tables and their values.
    
    Returns:
        List[Dict]: A list of dictionaries containing lookup table names, descriptions, and their values.
    """
    try:
        return get_lookups_service()
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )