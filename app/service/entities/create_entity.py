
from app.config.logging_config import logger
from app.core.exceptions import ServiceError
from app.schema.entities.create_entity import CreateEntityRequest
from app.core.database_connection_pool import db_pool


def create_entity_db(body: CreateEntityRequest):
    conn = db_pool.get_connection()
    if conn is None:
        logger.error(
            "Failed to get database connection for user retrieval")
        raise ServiceError(message="Database connection error", name="Database Error")
    with conn.cursor() as cursor:
        args = []
        args.append(body.entity_name.en)
        args.append(body.entity_name.ar)
        args.append(body.parent_id)
        args.append(body.entity_type)
        cursor.callproc("CreateEntity", args)
        conn.commit()
        entity_record = cursor.fetchone()
        if entity_record is None or entity_record.get("entity_id") is None:
            raise ServiceError(message="Error creating entity", name=None)
    db_pool.return_connection(conn)
    return {"message": f"Entity id {entity_record.get('entity_id')}"}

# entityTypes = {
#     1: "teams",
#     2: "stages",
#     3: "age_groups",
#     4: "gender_groups"
# }

# def create_entity_db(body: CreateEntityRequest):
#     conn = db_pool.get_connection()

#     if conn is not None:
#         with conn as conn:
#             cursor = conn.cursor()
#             args = []
#             args.append(entityTypes.get(body.entity_type))
#             args.append(body.entity_name.en)
#             args.append(body.entity_name.ar)
#             args.append(entityTypes.get(body.entity_type+1))
#             args.append(body.parent_id)
#             cursor.callproc("CreateEntity", args)
#             conn.commit()
#             entity_record = cursor.fetchone()
#             if entity_record is None or entity_record.get("entity_id") is None:
#                 raise ServiceError(message="Error creating entity", name=None)
#             return {"message": f"Entity id {entity_record.get('entity_id')}"}