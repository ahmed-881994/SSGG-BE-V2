from app.exceptions.exceptions import EntityDoesNotExistError
from app.schema.members.member import MemberAddUpdate
from app.util.database import get_connection


def update_member_db(member_id: str, member: MemberAddUpdate):
    """Updates a member in the database.
    This method allows you to update an existing member's information in the database.
    It checks if the member exists and updates the relevant fields with the provided data.
    If a field is not provided in the input, it retains the existing value from the database.

    Args:
        member_id (str): _description_
        member (dict[str, Any]): _description_

    Raises:
        EntityDoesNotExistError: _Description_

    Returns:
        dict: A dictionary indicating the result of the update operation.
    """
    conn = get_connection()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            # check event exists
            cursor.callproc("GetMember", [member_id])
            memberRecord = cursor.fetchone()
            # if event exists
            if memberRecord is not None:
                args = []
                args.append(member_id)
                args.append(member.name.en if member.name and hasattr(
                    member.name, 'en') else memberRecord.get("name_en"))
                args.append(member.name.en if member.name and hasattr(
                    member.name, 'ar') else memberRecord.get("name_ar"))
                args.append(member.place_of_birth if member.place_of_birth else memberRecord.get(
                    "place_of_birth"))
                args.append(member.date_of_birth if member.date_of_birth else memberRecord.get(
                    "date_of_birth"))
                args.append(
                    member.address if member.address else memberRecord.get("address"))
                args.append(member.national_id_no if member.national_id_no else memberRecord.get(
                    "national_id_no"))
                args.append(
                    member.club_id_no if member.club_id_no else memberRecord.get("club_id_no"))
                args.append(
                    member.passport_no if member.passport_no else memberRecord.get("passport_no"))
                args.append(
                    member.date_joined if member.date_joined else memberRecord.get("date_joined"))
                args.append(
                    member.mobile_no if member.mobile_no else memberRecord.get("mobile_number"))
                args.append(member.home_contact if member.home_contact else memberRecord.get(
                    "home_contact"))
                args.append(
                    member.email if member.email else memberRecord.get("email"))
                args.append(member.facebook_url if member.facebook_url else memberRecord.get(
                    "facebook_url"))
                args.append(
                    member.school_name if member.school_name else memberRecord.get("school_name"))
                args.append(member.education_type if member.education_type else memberRecord.get(
                    "education_type"))
                args.append(
                    member.father_name if member.father_name else memberRecord.get("father_name"))
                args.append(member.father_contact if member.father_contact else memberRecord.get(
                    "father_contact"))
                args.append(
                    member.father_job if member.father_job else memberRecord.get("father_job"))
                args.append(
                    member.mother_name if member.mother_name else memberRecord.get("mother_name"))
                args.append(member.mother_contact if member.mother_contact else memberRecord.get(
                    "mother_contact"))
                args.append(
                    member.mother_job if member.mother_job else memberRecord.get("mother_job"))
                args.append(member.guardian_name if member.guardian_name else memberRecord.get(
                    "guardian_name"))
                args.append(member.guardian_contact if member.guardian_contact else memberRecord.get(
                    "guardian_contact"))
                args.append(member.guardian_relationship if member.guardian_relationship else memberRecord.get(
                    "guardian_relationship"))
                args.append(
                    member.hobbies if member.hobbies else memberRecord.get("hobbies"))
                args.append(member.health_issues if member.health_issues else memberRecord.get(
                    "health_issues"))
                args.append(
                    member.medications if member.medications else memberRecord.get("medications"))
                args.append(
                    member.qr_code_url if member.qr_code_url else memberRecord.get("qr_code_url"))
                args.append(
                    member.image_url if member.image_url else memberRecord.get("image_url"))
                args.append(member.national_id_url if member.national_id_url else memberRecord.get(
                    "national_id_url"))
                args.append(member.parent_national_id_url if member.parent_national_id_url else memberRecord.get(
                    "parent_national_id_url"))
                args.append(
                    member.club_id_url if member.club_id_url else memberRecord.get("club_id_url"))
                args.append(member.passport_url if member.passport_url else memberRecord.get(
                    "passport_url"))
                args.append(member.birth_certificate_url if member.birth_certificate_url else memberRecord.get(
                    "birth_certificate_url"))
                photoConsent = member.photo_consent if member.photo_consent else memberRecord.get(
                    "photo_consent")
                args.append(
                    1 if photoConsent == True else 0
                )
                conditionsConsent = member.photo_consent if member.photo_consent else memberRecord.get(
                    "conditions_consent")
                args.append(
                    1 if conditionsConsent == True else 0
                )
                cursor.callproc("UpdateMember", args)
                conn.commit()
                return {"message": "Member updated Successfully"}
            else:
                raise EntityDoesNotExistError(
                    message="Member not found", name=None)
