from fastapi import HTTPException
from app.util.database import connect
from app.util.logging import insert_log


def get_team_members_db(team_id: int):
    """Get team members by team ID.
    This method retrieves all members of a specific team.
    Args:
        team_id (int): The ID of the team whose members are to be retrieved.
    Raises:
        HTTPException: If the team ID is not found or if there are no members in the team.
    Returns:
        list[dict]: A list of dictionaries containing the team members' details.
    """
    conn = connect()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            cursor.callproc("GetTeamMembers", [team_id])
            records = cursor.fetchall()
            if records is not None and len(records) > 0:
                data = format_team_member_record(records)
                conn.commit()
                return data
            else:
                raise HTTPException(
                    status_code=404, detail="Team has no members or teamID is not correct")


def format_team_member_record(records):
    entry = {
        "TeamID": records[0]['team_id'],
        "TeamName": {
            "EN": records[0]['team_name_en'],
            "AR": records[0]['team_name_ar']
        },
        "StageID": records[0]['stage_id'],
        "StageName": {
            "EN": records[0]['stage_name_en'],
            "AR": records[0]['stage_name_ar']
        },
        "Leaders": [],
        "Members": []
    }

    for record in records:
        if record['member_id'] is None:
            continue
        member_entry = {
            "MemberID": record['member_id'],
            "Name": {
                "EN": record['name_en'],
                "AR": record['name_ar']
            }
        }

        if record['is_leader'] == 1:
            entry['Leaders'].append(member_entry)
        else:
            entry['Members'].append(member_entry)

    return entry
