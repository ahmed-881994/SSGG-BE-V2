from typing import Optional
from fastapi import HTTPException
from app.database.connectionmanager import connect
from app.service.logging import insert_log


def search_members_db(name: Optional[str] = None, teamID: Optional[int] = None):
    """Search for members based on name or teamID.
    This method allows you to search for members in the database by their name or teamID.
    If both parameters are provided, it will search for members that match either one.
    Args:
        name (str, optional): The name of the member to search for. Defaults to None.
        teamID (int, optional): The teamID of the member to search for. Defaults to None.
    Raises:
        HTTPException: _description_
    Returns:
        List[Dict]: A list of members that match the search criteria.
    """
    conn = connect()

    if conn is not None:
        with conn as conn:
            try:
                cursor = conn.cursor()
                cursor.callproc("SearchMembers", [teamID, name])
                records = cursor.fetchall()
                return records
            except Exception as error:
                raise HTTPException(status_code=500, detail=error.args)
            finally:
                # insert_log(cursor, event, response, "SearchMembers")
                conn.commit()


def format_member_records(records):
    formatted_entries = []

    for record in records:
        member_id = record.get("member_id")

        # Check if an entry for this member already exists
        existing_entry = next(
            (
                entry
                for entry in formatted_entries
                if entry.get("MemberID") == member_id
            ),
            None,
        )

        if existing_entry:
            # Add team details to the existing entry's 'Teams' list
            team_entry = {
                "TeamID": record.get("team_id"),
                "IsTeamLeader": record.get("is_leader"),
                "IsTeamLeader": True if record.get("is_leader") == 1 else False,
                "DateJoined": record.get("team_join_date"),
                "DateTransferred": record.get("team_transfer_date"),
                "IsCurrentTeam": True if record.get("team_transfer_date") is None and record.get("is_leader") == 0 else False,
                "TeamName": {
                    "EN": record.get("team_name_en"),
                    "AR": record.get("team_name_ar"),
                },
            }
            existing_entry.get("Teams").append(team_entry)
        else:
            # Create a new entry for this member
            entry = {
                "MemberID": member_id,
                "Name": {"EN": record.get("name_en"), "AR": record.get("name_ar")},
                "Teams": [
                    {
                        "TeamID": record.get("team_id"),
                        "IsTeamLeader": record.get("is_leader"),
                        "IsTeamLeader": True if record.get("is_leader") == 1 else False,
                        "DateJoined": record.get("team_join_date"),
                        "DateTransferred": record.get("team_transfer_date"),
                        "IsCurrentTeam": True if record.get("team_transfer_date") is None and record.get("is_leader") == 0 else False,
                        "TeamName": {
                            "EN": record.get("team_name_en"),
                            "AR": record.get("team_name_ar"),
                        },
                    }
                ],
                "PlaceOfBirth": record.get("place_of_birth"),
                "DateOfBirth": record.get("date_of_birth"),
                "Address": record.get("address"),
                "NationalIdNo": record.get("national_id_no"),
                "ClubIdNo": record.get("club_id_no"),
                "PassportNo": record.get("passport_no"),
                "DateJoined": record.get("date_joined"),
                "MobileNo": record.get("mobile_number"),
                "HomeContact": record.get("home_contact"),
                "Email": record.get("email"),
                "FacebookURL": record.get("facebook_url"),
                "SchoolName": record.get("school_name"),
                "EducationType": record.get("education_type"),
                "FatherName": record.get("father_name"),
                "FatherContact": record.get("father_contact"),
                "FatherJob": record.get("father_job"),
                "MotherName": record.get("mother_name"),
                "MotherContact": record.get("mother_contact"),
                "MotherJob": record.get("mother_job"),
                "GuardianName": record.get("guardian_name"),
                "GuardianContact": record.get("guardian_contact"),
                "GuardianRelationship": record.get("guardian_relationship"),
                "Hobbies": record.get("hobbies"),
                "HealthIssues": record.get("health_issues"),
                "Medications": record.get("medications"),
                "QRCodeURL": record.get("qr_code_url"),
                "ImageURL": record.get("image_url"),
                "NationalIdURL": record.get("national_id_url"),
                "ParentNationalIdURL": record.get("parent_national_id_url"),
                "ClubIdURL": record.get("club_id_url"),
                "PassportURL": record.get("passport_url"),
                "BirthCertificateURL": record.get("birth_certificate_url"),
                "PhotoConsent": record.get("photo_consent"),
                "ConditionsConsent": record.get("conditions_consent"),
            }
            formatted_entries.append(entry)

    return formatted_entries
