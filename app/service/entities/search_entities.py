from collections import defaultdict
from typing import List, Optional

from app.config.logging_config import logger
from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.schema.entities.search_entities import SearchEntitiesResponse
from app.core.database_connection_pool import db_pool


def search_entities_db(entity_id: Optional[int], entity_parent_id: Optional[int], entity_name: Optional[str]):
    """
    Search for entities in the database.

    Args:
        entityID (int): The ID of the entity.
        entityParentID (int): The Parent ID of the entity.
        entityName (str): The Name of the entity.

    Returns:
        list: A list of entities matching the search criteria.
    """
    params = []
    conn = db_pool.get_connection()
    if conn is None:
        logger.error(
            "Failed to get database connection for user retrieval")
        raise ServiceError(
            message="Database connection error", name="Database Error")
    try:
        with conn.cursor() as cursor:
            cursor.callproc("SearchEntities", [
                            entity_id, entity_parent_id, entity_name])
            records = cursor.fetchall()
            if records is None or len(records) == 0:
                raise EntityDoesNotExistError(
                    message="No entities found with the provided criteria.", name=None)
            return format_entity_response(records)
    finally:
        db_pool.return_connection(conn)

def format_entity_response(records: dict) -> List[SearchEntitiesResponse]:
    """
    Format the entity response from the database records.

    Args:
        records (dict): The database records to format.

    Returns:
        List[SearchEntitiesResponse]: The formatted entity responses.
    """
    response= defaultdict(lambda: {
        "EntityID": None,
        "EntityName": {"EN": "", "AR": ""},
        "ParentID": None,
        "Children": []
    })
    
    child = defaultdict(lambda: {
        "EntityID": None,
        "EntityName": {"EN": "", "AR": ""}
    })
    
    for record in records:
        entity_id = record.get('entity_id')
        if response[entity_id]["EntityID"] is None:
            response[entity_id]["EntityID"] = entity_id
            response[entity_id]["EntityName"]["EN"] = record.get('entity_name_en', '')
            response[entity_id]["EntityName"]["AR"] = record.get('entity_name_ar', '')
            response[entity_id]["ParentID"] = record.get('parent_id')
        if record.get('child_id'):
            child_id = record.get('child_id')
            if child[child_id]["EntityID"] is None:
                child[child_id]["EntityID"] = child_id
                child[child_id]["EntityName"]["EN"] = record.get('child_name_en', '')
                child[child_id]["EntityName"]["AR"] = record.get('child_name_ar', '')
            response[entity_id]["Children"].append(child[child_id])

    return list(response.values())