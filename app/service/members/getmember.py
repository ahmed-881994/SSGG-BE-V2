from app.exceptions.exceptions import EntityDoesNotExistError
from app.util.database import connect


def get_member_db(member_id: str):
    conn = connect()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            cursor.callproc("GetMember", [member_id])
            records = cursor.fetchall()
            if records is not None and len(records) > 0:
                data = format_member_record(records)
                conn.commit()
                return data
            else:
                raise EntityDoesNotExistError(
                    message="No members found with the provided criteria.", name=None)


def format_member_record(records):
    formatted_entry = {
        "MemberID": records[0].get("member_id"),
        "Name": {
            "EN": records[0].get("name_en"),
            "AR": records[0].get("name_ar"),
        },
        "Teams": [],
        "TeamsManaging": [],
        "StagesManaging": [],
        "AgeGroupsManaging": [],
        "GenderGroupsManaging": [],
        "PlaceOfBirth": records[0].get("place_of_birth"),
        "DateOfBirth": records[0].get("date_of_birth"),
        "Address": records[0].get("address"),
        "NationalIdNo": records[0].get("national_id_no"),
        "ClubIdNo": records[0].get("club_id_no"),
        "PassportNo": records[0].get("passport_no"),
        "DateJoined": None if records[0].get("date_joined") is None else str(records[0].get("date_joined")),
        "MobileNo": records[0].get("mobile_number"),
        "HomeContact": records[0].get("home_contact"),
        "Email": records[0].get("email"),
        "FacebookURL": records[0].get("facebook_url"),
        "SchoolName": records[0].get("school_name"),
        "EducationType": records[0].get("education_type"),
        "FatherName": records[0].get("father_name"),
        "FatherContact": records[0].get("father_contact"),
        "FatherJob": records[0].get("father_job"),
        "MotherName": records[0].get("mother_name"),
        "MotherContact": records[0].get("mother_contact"),
        "MotherJob": records[0].get("mother_job"),
        "GuardianName": records[0].get("guardian_name"),
        "GuardianContact": records[0].get("guardian_contact"),
        "GuardianRelationship": records[0].get("guardian_relationship"),
        "Hobbies": records[0].get("hobbies"),
        "HealthIssues": records[0].get("health_issues"),
        "Medications": records[0].get("medications"),
        "QRCodeURL": records[0].get("qr_code_url"),
        "ImageURL": records[0].get("image_url"),
        "NationalIdURL": records[0].get("national_id_url"),
        "ParentNationalIdURL": records[0].get("parent_national_id_url"),
        "ClubIdURL": records[0].get("club_id_url"),
        "PassportURL": records[0].get("passport_url"),
        "BirthCertificateURL": records[0].get("birth_certificate_url"),
        "PhotoConsent": True if records[0].get("photo_consent") == 1 else False,
        "ConditionsConsent": True if records[0].get("conditions_consent") == 1 else False,
    }
    handled_entities = {"teams": [],
                        "teams_managing": [],
                        "stages_managing": [],
                        "age_groups_managing": [],
                        "gender_groups_managing": []}
    for record in records:
        if record.get("team_member_in_id") is not None and record.get("team_member_in_id") not in handled_entities["teams"]:
            team_entry = {
                "TeamID": record.get("team_member_in_id"),
                # "IsTeamLeader": True if record.get("is_leader") == 1 else False,
                "DateJoined": record.get("team_join_date"),
                "DateTransferred": record.get("team_transfer_date"),
                "IsCurrentTeam": True if record.get("team_transfer_date") is None else False,
                "TeamName": {
                    "EN": record.get("team_member_in_name_en"),
                    "AR": record.get("team_member_in_name_ar"),
                },
            }
            formatted_entry["Teams"].append(team_entry)
        if record.get("team_managing_id") is not None:
            team_managing_entry = {
                "ID": record.get("team_managing_id"),
                "Name": {
                    "EN": record.get("team_managing_name_en"),
                    "AR": record.get("team_managing_name_ar"),
                },
                "RoleID": record.get("role_in_team_managing_id"),
                "RoleName": {
                    "EN": record.get("role_in_team_managing_name_en"),
                    "AR": record.get("role_in_team_managing_name_ar"),
                }
            }
            formatted_entry["TeamsManaging"].append(team_managing_entry)
        if record.get("stage_managing_id") is not None:
            stage_managing_entry = {
                "ID": record.get("stage_managing_id"),
                "Name": {
                    "EN": record.get("stage_managing_name_en"),
                    "AR": record.get("stage_managing_name_ar"),
                },
                "RoleID": record.get("role_in_stage_managing_id"),
                "RoleName": {
                    "EN": record.get("role_in_stage_managing_name_en"),
                    "AR": record.get("role_in_stage_managing_name_ar"),
                }
            }
            formatted_entry["StagesManaging"].append(stage_managing_entry)
        if record.get("age_group_managing_id") is not None:
            age_group_managing_entry = {
                "ID": record.get("age_group_managing_id"),
                "Name": {
                    "EN": record.get("age_group_managing_name_en"),
                    "AR": record.get("age_group_managing_name_ar"),
                },
                "ID": record.get("role_in_age_group_managing_id"),
                "Name": {
                    "EN": record.get("role_in_age_group_managing_name_en"),
                    "AR": record.get("role_in_age_group_managing_name_ar"),
                }
            }
            formatted_entry["AgeGroupsManaging"].append(age_group_managing_entry)
        if record.get("gender_group_managing_id") is not None:
            gender_group_managing_entry = {
                "ID": record.get("gender_group_managing_id"),
                "Name": {
                    "EN": record.get("gender_group_managing_name_en"),
                    "AR": record.get("gender_group_managing_name_ar"),
                },
                "RoleID": record.get("role_in_gender_group_managing_id"),
                "RoleName": {
                    "EN": record.get("role_in_gender_group_managing_name_en"),
                    "AR": record.get("role_in_gender_group_managing_name_ar"),
                }
            }
            formatted_entry["GenderGroupsManaging"].append(gender_group_managing_entry)

    return formatted_entry
