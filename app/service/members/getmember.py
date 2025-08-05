from app.exceptions.exceptions import EntityDoesNotExistError
from app.middleware.logging_middleware import logger
from app.util.pymysql_pool import db_pool


def get_member_db(member_id: str):
    conn = db_pool.get_connection()

    if conn is not None:
        with conn.cursor() as cursor:
            cursor.callproc("GetMember", [member_id])
            records = cursor.fetchall()
            if records is not None and len(records) > 0:
                logger.info(
                    f"Found {len(records)} records for member ID: {member_id}")
                data = format_member_records(records)
                logger.info(f"member data: {data}")
                db_pool.return_connection(conn)
                return data
            else:
                logger.info(
                    f"No records found for member ID: {member_id}")
                db_pool.return_connection(conn)
                raise EntityDoesNotExistError(
                    message="No members found with the provided criteria.", name=None)
                


def format_member_records(records):
    formatted_entry = {
        "MemberID": records[0].get("member_id"),
        "Name": {
            "EN": records[0].get("name_en"),
            "AR": records[0].get("name_ar"),
        },
        "Entities": [],
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
    
    for record in records:
        entity_entry = {
            "EntityID": record.get("entity_id"),
            "EntityName": {
                "EN": record.get("entity_name_en"),
                "AR": record.get("entity_name_ar"),
            },
            "RoleID": record.get("entity_role_id"),
            "RoleName": {
                "EN": record.get("entity_role_name_en"),
                "AR": record.get("entity_role_name_ar"),
            },
            "FromDate": record.get("date_from"),
            "ToDate": record.get("date_to"),
            "IsCurrentEntity": True if record.get("date_to") is None else False,
        }
        formatted_entry["Entities"].append(entity_entry)
    
    return formatted_entry

# def format_member_record(records):
#     formatted_entry = {
#         "MemberID": records[0].get("member_id"),
#         "Name": {
#             "EN": records[0].get("name_en"),
#             "AR": records[0].get("name_ar"),
#         },
#         "Teams": [],
#         "TeamsManaging": [],
#         "StagesManaging": [],
#         "AgeGroupsManaging": [],
#         "GenderGroupsManaging": [],
#         "PlaceOfBirth": records[0].get("place_of_birth"),
#         "DateOfBirth": records[0].get("date_of_birth"),
#         "Address": records[0].get("address"),
#         "NationalIdNo": records[0].get("national_id_no"),
#         "ClubIdNo": records[0].get("club_id_no"),
#         "PassportNo": records[0].get("passport_no"),
#         "DateJoined": None if records[0].get("date_joined") is None else str(records[0].get("date_joined")),
#         "MobileNo": records[0].get("mobile_number"),
#         "HomeContact": records[0].get("home_contact"),
#         "Email": records[0].get("email"),
#         "FacebookURL": records[0].get("facebook_url"),
#         "SchoolName": records[0].get("school_name"),
#         "EducationType": records[0].get("education_type"),
#         "FatherName": records[0].get("father_name"),
#         "FatherContact": records[0].get("father_contact"),
#         "FatherJob": records[0].get("father_job"),
#         "MotherName": records[0].get("mother_name"),
#         "MotherContact": records[0].get("mother_contact"),
#         "MotherJob": records[0].get("mother_job"),
#         "GuardianName": records[0].get("guardian_name"),
#         "GuardianContact": records[0].get("guardian_contact"),
#         "GuardianRelationship": records[0].get("guardian_relationship"),
#         "Hobbies": records[0].get("hobbies"),
#         "HealthIssues": records[0].get("health_issues"),
#         "Medications": records[0].get("medications"),
#         "QRCodeURL": records[0].get("qr_code_url"),
#         "ImageURL": records[0].get("image_url"),
#         "NationalIdURL": records[0].get("national_id_url"),
#         "ParentNationalIdURL": records[0].get("parent_national_id_url"),
#         "ClubIdURL": records[0].get("club_id_url"),
#         "PassportURL": records[0].get("passport_url"),
#         "BirthCertificateURL": records[0].get("birth_certificate_url"),
#         "PhotoConsent": True if records[0].get("photo_consent") == 1 else False,
#         "ConditionsConsent": True if records[0].get("conditions_consent") == 1 else False,
#     }
#     handled_entities = {"teams": [],
#                         "teams_managing": [],
#                         "stages_managing": [],
#                         "age_groups_managing": [],
#                         "gender_groups_managing": []}
#     for record in records:
#         if record.get("team_member_in_id") is not None and record.get("team_member_in_id") not in handled_entities["teams"]:
#             handled_entities["teams"].append(record.get("team_member_in_id"))
#             team_entry = {
#                 "TeamID": record.get("team_member_in_id"),
#                 # "IsTeamLeader": True if record.get("is_leader") == 1 else False,
#                 "DateJoined": record.get("team_join_date"),
#                 "DateTransferred": record.get("team_transfer_date"),
#                 "IsCurrentTeam": True if record.get("team_transfer_date") is None else False,
#                 "TeamName": {
#                     "EN": record.get("team_member_in_name_en"),
#                     "AR": record.get("team_member_in_name_ar"),
#                 },
#             }
#             formatted_entry["Teams"].append(team_entry)
#         if record.get("team_managing_id") is not None and record.get("team_managing_id") not in handled_entities["teams_managing"]:
#             handled_entities["teams_managing"].append(record.get("team_managing_id"))
#             team_managing_entry = {
#                 "ID": record.get("team_managing_id"),
#                 "Name": {
#                     "EN": record.get("team_managing_name_en"),
#                     "AR": record.get("team_managing_name_ar"),
#                 },
#                 "RoleID": record.get("role_in_team_managing_id"),
#                 "RoleName": {
#                     "EN": record.get("role_in_team_managing_name_en"),
#                     "AR": record.get("role_in_team_managing_name_ar"),
#                 }
#             }
#             if team_managing_entry["RoleName"]["EN"] is None:
#                 team_managing_entry["RoleName"] = None
#             formatted_entry["TeamsManaging"].append(team_managing_entry)
#         if record.get("stage_managing_id") is not None and record.get("stage_managing_id") not in handled_entities["stages_managing"]:
#             handled_entities["stages_managing"].append(record.get("stage_managing_id"))
#             stage_managing_entry = {
#                 "ID": record.get("stage_managing_id"),
#                 "Name": {
#                     "EN": record.get("stage_managing_name_en"),
#                     "AR": record.get("stage_managing_name_ar"),
#                 },
#                 "RoleID": record.get("role_in_stage_managing_id"),
#                 "RoleName": {
#                     "EN": record.get("role_in_stage_managing_name_en"),
#                     "AR": record.get("role_in_stage_managing_name_ar"),
#                 }
#             }
#             if stage_managing_entry["RoleName"]["EN"] is None:
#                 stage_managing_entry["RoleName"] = None
#             formatted_entry["StagesManaging"].append(stage_managing_entry)
#         if record.get("age_group_managing_id") is not None and record.get("age_group_managing_id") not in handled_entities["age_groups_managing"]:
#             handled_entities["age_groups_managing"].append(record.get("age_group_managing_id"))
#             age_group_managing_entry = {
#                 "ID": record.get("age_group_managing_id"),
#                 "Name": {
#                     "EN": record.get("age_group_managing_name_en"),
#                     "AR": record.get("age_group_managing_name_ar"),
#                 },
#                 "RoleID": record.get("role_in_age_group_managing_id"),
#                 "RoleName": {
#                     "EN": record.get("role_in_age_group_managing_name_en"),
#                     "AR": record.get("role_in_age_group_managing_name_ar"),
#                 }
#             }
#             if age_group_managing_entry["RoleName"]["EN"] is None:
#                 age_group_managing_entry["RoleName"] = None
#             formatted_entry["AgeGroupsManaging"].append(age_group_managing_entry)
#         if record.get("gender_group_managing_id") is not None and record.get("gender_group_managing_id") not in handled_entities["gender_groups_managing"]:
#             handled_entities["gender_groups_managing"].append(record.get("gender_group_managing_id"))
#             gender_group_managing_entry = {
#                 "ID": record.get("gender_group_managing_id"),
#                 "Name": {
#                     "EN": record.get("gender_group_managing_name_en"),
#                     "AR": record.get("gender_group_managing_name_ar"),
#                 },
#                 "RoleID": record.get("role_in_gender_group_managing_id"),
#                 "RoleName": {
#                     "EN": record.get("role_in_gender_group_managing_name_en"),
#                     "AR": record.get("role_in_gender_group_managing_name_ar"),
#                 }
#             }
#             if gender_group_managing_entry["RoleName"]["EN"] is None:
#                 gender_group_managing_entry["RoleName"]= None
#             formatted_entry["GenderGroupsManaging"].append(gender_group_managing_entry)

#     for key in ["TeamsManaging", "StagesManaging", "AgeGroupsManaging", "GenderGroupsManaging"]:
#         if not formatted_entry[key]:
#             formatted_entry[key] = None
#     return formatted_entry
