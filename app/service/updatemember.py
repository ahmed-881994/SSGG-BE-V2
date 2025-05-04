from typing import Any
from fastapi import HTTPException
from app.database.connectionmanager import connect
from app.service.logging import insert_log


def update_member_db(member_id: str, member: dict[str, Any]):
    """Updates a member in the database.
    This method allows you to update an existing member's information in the database.
    It checks if the member exists and updates the relevant fields with the provided data.
    If a field is not provided in the input, it retains the existing value from the database.
    
    Args:
        member_id (str): _description_
        member (dict[str, Any]): _description_
    
    Raises:
        HTTPException: _Description_
        - status_code (int): The HTTP status code for the error.
        - detail (str): The error message.

    Returns:
        int: 0 if success, -1 if member not found
    """
    conn = connect()

    if conn is not None:
        with conn as conn:
            try:
                cursor = conn.cursor()
                # check event exists
                cursor.callproc("GetMember", [member_id])
                memberRecord = cursor.fetchone()
                # if event exists
                if memberRecord is not None:
                    args = []
                    args.append(member_id)
                    args.append(member.get("Name").get("EN") if member.get(
                        "Name", {}).get("EN") else memberRecord.get("name_en"))
                    args.append(member.get("Name").get("AR") if member.get(
                        "Name", {}).get("AR") else memberRecord.get("name_ar"))
                    args.append(member.get("PlaceOfBirth") if member.get(
                        "PlaceOfBirth") else memberRecord.get("place_of_birth"))
                    args.append(member.get("DateOfBirth") if member.get(
                        "DateOfBirth") else memberRecord.get("date_of_birth"))
                    args.append(member.get("Address") if member.get(
                        "Address") else memberRecord.get("address"))
                    args.append(member.get("NationalIdNo") if member.get(
                        "NationalIdNo") else memberRecord.get("national_id_no"))
                    args.append(member.get("ClubIdNo") if member.get(
                        "ClubIdNo") else memberRecord.get("club_id_no"))
                    args.append(member.get("PassportNo") if member.get(
                        "PassportNo") else memberRecord.get("passport_no"))
                    args.append(member.get("DateJoined") if member.get(
                        "DateJoined") else memberRecord.get("date_joined"))
                    args.append(member.get("MobileNo") if member.get(
                        "MobileNo") else memberRecord.get("mobile_number"))
                    args.append(member.get("HomeContact") if member.get(
                        "HomeContact") else memberRecord.get("home_contact"))
                    args.append(member.get("Email") if member.get(
                        "Email") else memberRecord.get("email"))
                    args.append(member.get("FacebookURL") if member.get(
                        "FacebookURL") else memberRecord.get("facebook_url"))
                    args.append(member.get("SchoolName") if member.get(
                        "SchoolName") else memberRecord.get("school_name"))
                    args.append(member.get("EducationType") if member.get(
                        "EducationType") else memberRecord.get("education_type"))
                    args.append(member.get("FatherName") if member.get(
                        "FatherName") else memberRecord.get("father_name"))
                    args.append(member.get("FatherContact") if member.get(
                        "FatherContact") else memberRecord.get("father_contact"))
                    args.append(member.get("FatherJob") if member.get(
                        "FatherJob") else memberRecord.get("father_job"))
                    args.append(member.get("MotherName") if member.get(
                        "MotherName") else memberRecord.get("mother_name"))
                    args.append(member.get("MotherContact") if member.get(
                        "MotherContact") else memberRecord.get("mother_contact"))
                    args.append(member.get("MotherJob") if member.get(
                        "MotherJob") else memberRecord.get("mother_job"))
                    args.append(member.get("GuardianName") if member.get(
                        "GuardianName") else memberRecord.get("guardian_name"))
                    args.append(member.get("GuardianContact") if member.get(
                        "GuardianContact") else memberRecord.get("guardian_contact"))
                    args.append(member.get("GuardianRelationship") if member.get(
                        "GuardianRelationship") else memberRecord.get("guardian_relationship"))
                    args.append(member.get("Hobbies") if member.get(
                        "Hobbies") else memberRecord.get("hobbies"))
                    args.append(member.get("HealthIssues") if member.get(
                        "HealthIssues") else memberRecord.get("health_issues"))
                    args.append(member.get("Medications") if member.get(
                        "Medications") else memberRecord.get("medications"))
                    args.append(member.get("QRCodeURL") if member.get(
                        "QRCodeURL") else memberRecord.get("qr_code_url"))
                    args.append(member.get("ImageURL") if member.get(
                        "ImageURL") else memberRecord.get("image_url"))
                    args.append(member.get("NationalIdURL") if member.get(
                        "NationalIdURL") else memberRecord.get("national_id_url"))
                    args.append(member.get("ParentNationalIdURL") if member.get(
                        "ParentNationalIdURL") else memberRecord.get("parent_national_id_url"))
                    args.append(member.get("ClubIdURL") if member.get(
                        "ClubIdURL") else memberRecord.get("club_id_url"))
                    args.append(member.get("PassportURL") if member.get(
                        "PassportURL") else memberRecord.get("passport_url"))
                    args.append(member.get("BirthCertificateURL") if member.get(
                        "BirthCertificateURL") else memberRecord.get("birth_certificate_url"))
                    photoConsent = member.get("PhotoConsent") if member.get(
                        "PhotoConsent") else memberRecord.get("photo_consent")
                    args.append(
                        1 if photoConsent == True else 0
                    )
                    conditionsConsent = member.get("ConditionsConsent") if member.get(
                        "ConditionsConsent") else memberRecord.get("conditions_consent")
                    args.append(
                        1 if conditionsConsent == True else 0
                    )
                    cursor.callproc("UpdateMember", args)
                    response = 0
                else:
                    response = -1
            except Exception as error:
                raise HTTPException(status_code=500, detail=error.args)
            finally:
                # insert_log(cursor, event, response, "UpdateMember")
                conn.commit()
    return response
