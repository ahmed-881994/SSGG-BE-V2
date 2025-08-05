from app.exceptions.exceptions import (EntityAlreadyExistsError,
                                       EntityDoesNotExistError)
from app.schema.entities.update_entity_member_role import \
    UpdateEntityMemberRoleRequest
from app.util.pymysql_pool import db_pool


def update_entity_member_role_db(entityID: int, body: UpdateEntityMemberRoleRequest):
    """
    Update the role of a member in an entity.
    """
    conn = db_pool.get_connection()
    if conn is not None:
        with conn.cursor() as cursor:
            cursor.callproc("GetMember", [body.member_id])
            member_records = cursor.fetchall()
            if not member_records:
                raise EntityDoesNotExistError(
                    message=f"Member {body.member_id} not found", name=None)
            for member_record in member_records:
                if member_record.get("entity_id") == entityID and member_record.get("entity_role_id") == body.role:
                    raise EntityAlreadyExistsError(
                        message=f"Member {body.member_id} already has this role {body.role} in entity {entityID}", name=None)

            cursor.callproc("UpdateEntityMemberRole", [
                            entityID, body.member_id, body.role],)
            conn.commit()
        db_pool.return_connection(conn)
        return {"message": "Member role updated successfully"}
