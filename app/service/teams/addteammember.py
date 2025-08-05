from typing import List

from app.exceptions.exceptions import (EntityAlreadyExistsError,
                                       EntityDoesNotExistError)
from app.schema.teams.teams import TeamAdd
from app.util.database import get_connection


def add_team_member_db(team_id: int, body: List[TeamAdd]):
    conn = get_connection()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            for item in body:
                cursor.callproc("CheckMemberInTeam", [
                                item.member_id, team_id, 1 if item.is_leader == True else 0])
                result = cursor.fetchone()
                if result is not None:
                    if result.get('in_team') == 1:
                        raise EntityAlreadyExistsError(
                            message=f"Member {item.member_id} already in the team", name=None)
                    elif result.get('in_team') == -1:
                        raise EntityDoesNotExistError(
                            message=f"Member {item.member_id} does not exist", name=None)
                    else:
                        is_leader = 1 if item.is_leader == True else 0
                        from_date = item.from_date
                        args = [
                            item.member_id,
                            team_id,
                            from_date,
                            is_leader
                        ]
                        cursor.callproc("AddMemberToTeam", args)
                        conn.commit()
    return {"message": "Members added successfully"}
