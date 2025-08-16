from app.core.exceptions import EntityDoesNotExistError
from app.util.database import get_connection


def get_entity_teams_db(entityType: int, entityID: int):
    """
    Get teams for a specific entity type and ID from the database.

    Args:
        entityType (str): The type of the entity (e.g., "member", "team").
        entityID (int): The ID of the entity.

    Returns:
        list: A list containing the teams associated with the entity.
    """
    # Placeholder for actual database query
    # return [{"teamID": 1, "teamName": "Team A"}, {"teamID": 2, "teamName": "Team B"}]

    conn = get_connection()
    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            cursor.callproc("GetEntityTeams", [entityType, entityID])
            records = cursor.fetchall()
            if records is None or len(records) == 0:
                raise EntityDoesNotExistError(
                    message="No teams found for the provided entity type and ID.", name=None)
            conn.commit()
            # return format_entity_teams(records)