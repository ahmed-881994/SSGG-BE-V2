from app.config.logging_config import logger
from app.core.exceptions import EntityDoesNotExistError, ServiceError
from app.core.database_connection_pool import db_pool


def get_entity_members_db(entity_id: int):
    """
    Get members of an entity from the database.

    Args:
        entityID (int): The ID of the entity.

    Returns:
        List[Dict]: A list of members belonging to the entity.
    """
    conn = db_pool.get_connection()
    if conn is None:
        logger.error(
            "Failed to get database connection for entity members retrieval")
        raise ServiceError(
            message="Database connection error", name="Database Error")

    with conn.cursor() as cursor:
        cursor.callproc("SearchEntities", [entity_id, None, None])
        entity_record = cursor.fetchone()
        if entity_record is None:
            logger.error(f"Entity with ID {entity_id} does not exist")
            db_pool.return_connection(conn)
            raise EntityDoesNotExistError(
                message="No teams found for the provided entity type and ID.", name=None)

        cursor.callproc("GetEntityMembers", [entity_id])

        members = cursor.fetchall()
        if members is None or len(members) == 0:
            logger.warning(f"No members found for entity ID {entity_id}")
            db_pool.return_connection(conn)
            raise EntityDoesNotExistError(
                message="No members found for the entity", name=None)

        list_of_members = [{'MemberID': member['member_id'], 'Name': {'EN': member['name_en'],
                                                                      'AR': member['name_ar']}, 'MemberRole': {'EN': member['entity_role_name_en'], 'AR': member['entity_role_name_ar']}} for member in members]
        logger.info(
            f"Retrieved {len(list_of_members)} members for entity ID {entity_id}")
    db_pool.return_connection(conn)
    return list_of_members
