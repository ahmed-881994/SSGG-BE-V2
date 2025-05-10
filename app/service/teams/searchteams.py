from collections import defaultdict
from typing import Optional

from app.exceptions.exceptions import EntityDoesNotExistError
from app.util.database import connect


def search_teams_db(team_name: Optional[str] = None, stage_id: Optional[int] = None, leader_id: Optional[str] = None):
    """Search for teams based on name or teamID.
    This method allows you to search for teams in the database by their name or teamID.
    If both parameters are provided, it will search for teams that match either one.
    Args:
        name (str, optional): The name of the team to search for. Defaults to None.
        teamID (int, optional): The teamID of the team to search for. Defaults to None.
    Raises:
        EntityDoesNotExistError: _description_
    Returns:
        List[Dict]: A list of teams that match the search criteria.
    """
    conn = connect()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            cursor.callproc("SearchTeams", [stage_id, leader_id, team_name])
            records = cursor.fetchall()
            if records is None or len(records) == 0:
                raise EntityDoesNotExistError(
                    message="No teams found with the provided criteria.", name=None)
            conn.commit()
            return format_team_records(records)
            # insert_log(cursor, event, response, "SearchTeams")


def format_team_records(records):
    teams = defaultdict(lambda: {
        "TeamID": None,
        "TeamName": {"EN": "", "AR": ""},
        "StageID": None,
        "StageName": {"EN": "", "AR": ""},
        "Leaders": [],
        "Members": []
    })

    for entry in records:
        team_id = entry.get('team_id')
        if teams[team_id]["TeamID"] is None:
            teams[team_id]["TeamID"] = team_id
            teams[team_id]["TeamName"]["EN"] = entry.get('team_name_en')
            teams[team_id]["TeamName"]["AR"] = entry.get('team_name_ar')
            teams[team_id]["StageID"] = entry.get('stage_id')
            teams[team_id]["StageName"]["EN"] = entry.get('stage_name_en')
            teams[team_id]["StageName"]["AR"] = entry.get('stage_name_ar')

        member = {
            # the condition should be removed
            "MemberID": entry.get('member_id') if entry.get('member_id') else "",
            "Name": {
                "EN": entry.get('name_en'),
                "AR": entry.get('name_ar')
            }
        }

        if entry.get('is_leader'):
            teams[team_id]["Leaders"].append(member)
        else:
            teams[team_id]["Members"].append(member)

    return list(teams.values())
