from typing import List
from fastapi import HTTPException
from app.database.connectionmanager import connect
from app.schema.teams.teams import TeamAdd
from app.service.logging import insert_log


def add_team_member_db(team_id: int, body: List[TeamAdd]):
    conn = connect()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            for item in body:
                cursor.callproc("CheckMemberInTeam", [
                                item.member_id, team_id, 1 if item.is_leader == True else 0])
                result = cursor.fetchone()
                if result is not None:
                    if result.get('in_team') == 1:
                        raise HTTPException(
                            status_code=400, detail=f"Member {item.member_id} already in the team")
                    elif result.get('in_team') == -1:
                        raise HTTPException(
                            status_code=404, detail=f"Member {item.member_id} does not exist")
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
