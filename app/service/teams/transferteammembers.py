from fastapi import HTTPException
from app.database.connectionmanager import connect
from app.service.logging import insert_log


def transfer_team_members_db(body: list[dict]):
    """Transfer a member to another team.
    This method allows you to transfer a member from one team to another.
    Args:
        body (list[dict]): A list of dictionaries containing the member details.
            Each dictionary should contain the following keys:
                - MemberID: The ID of the member to be transferred.
                - FromTeamID: The ID of the team from which the member is being transferred.
                - ToTeamID: The ID of the team to which the member is being transferred.
                - TransferDate: The date of transfer.
                - IsLeader: A boolean indicating if the member is a leader in the new team.
    Raises:
        HTTPException: If the member is not found or if the member is already in the target team.
    Returns:
        dict: A dictionary containing a success message if all members are transferred successfully.
    """
    conn = connect()
    errors = []
    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            for item in body:
                member_id = item.get("Member").get("MemberID")
                is_leader = 1 if item.get("Member").get(
                    "IsLeader") == True else 0
                from_team_id = item.get("FromTeamID")
                to_team_id = item.get("ToTeamID")
                transfer_date = item.get("TransferDate")
                cursor.callproc("GetMember", [member_id])
                member_object = cursor.fetchone()
                if member_object is None:
                    raise HTTPException(
                        status_code=404, detail=f"Member {member_id} not found")
                if member_object.get("team_id") == to_team_id and member_object.get("is_leader") == is_leader:
                    raise HTTPException(
                        status_code=400, detail=f"Member {member_id} already in the team")

                cursor.callproc("TransferTeamMember", [
                                member_id, from_team_id, to_team_id, transfer_date, is_leader],)
                conn.commit()
            return {"message": "Members transferred successfully"}
