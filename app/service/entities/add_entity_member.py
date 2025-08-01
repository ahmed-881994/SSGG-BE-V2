from typing import List

from app.config.logging_config import logger
from app.exceptions.exceptions import (EntityAlreadyExistsError,
                                       EntityDoesNotExistError, ServiceError)
from app.schema.entities.add_entity_member import AddEntityMemberRequest
from app.util.pymysql_pool import db_pool


def add_entity_member_db(body: List[AddEntityMemberRequest], entity_id: int):
    """
    Add a member to an entity in the database.
    """
    print(f"input: {body}")
    conn = db_pool.get_connection()
    if conn is None:
        logger.error(
            "Failed to get database connection for user retrieval")
        raise ServiceError(message="Database connection error", name="Database Error")
    with conn.cursor() as cursor:
        for item in body:
            cursor.callproc("CheckMemberInEntity", [
                            item.member_id, entity_id, item.role])
            result = cursor.fetchone()
            if result is not None:
                if result.get('in_entity') == 1:
                    raise EntityAlreadyExistsError(
                        message=f"Member {item.member_id} already in the entity", name=None)
                elif result.get('in_entity') == -1:
                    raise EntityDoesNotExistError(
                        message=f"Member {item.member_id} does not exist", name=None)
                else:
                    args = [
                        entity_id,
                        item.member_id,
                        item.role,
                        item.from_date,
                    ]
                    cursor.callproc("AddMemberToEntity", args)
                    conn.commit()
    db_pool.return_connection(conn)
    return {"message": "Members added successfully"}
