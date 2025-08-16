from app.core.exceptions import (EntityAlreadyExistsError,
                                       EntityDoesNotExistError)
from app.schema.entities.transfer_entity_members import EntityTransfer
from app.core.database_connection_pool import db_pool


def transfer_entity_members_db(body: list[EntityTransfer]):
    """Transfer a member to another entity.
    This method allows you to transfer a member from one entity to another.
    Args:
        body (list[dict]): A list of dictionaries containing the member details.
            Each dictionary should contain the following keys:
                - MemberID: The ID of the member to be transferred.
                - FromEntityID: The ID of the entity from which the member is being transferred.
                - ToEntityID: The ID of the entity to which the member is being transferred.
                - TransferDate: The date of transfer.
    Raises:
        EntityDoesNotExistError: If the member is not found
        EntityAlreadyExistsError: if the member is already in the target entity.
    Returns:
        dict: A dictionary containing a success message if all members are transferred successfully.
    """
    conn = db_pool.get_connection()
    if conn is not None:
        with conn.cursor() as cursor:
            for item in body:
                member_id = item.member_id
                from_entity_id = item.from_entity_id
                to_entity_id = item.to_entity_id
                transfer_date = item.transfer_date
                cursor.callproc("GetMember", [member_id])
                member_object = cursor.fetchone()
                if member_object is None:
                    raise EntityDoesNotExistError(
                        message=f"Member {member_id} not found", name=None)
                if member_object.get("entity_id") == to_entity_id:
                    raise EntityAlreadyExistsError(
                        message=f"Member {member_id} already in the entity", name=None)

                cursor.callproc("TransferEntityMember", [
                                member_id, from_entity_id, to_entity_id, transfer_date],)
                conn.commit()
        db_pool.return_connection(conn)
        return {"message": "Members transferred successfully"}