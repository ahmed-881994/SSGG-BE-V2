from app.schema.members.member import MemberAddUpdate
from app.util.database import get_connection


def add_member_db(member: MemberAddUpdate):
    """adds a new member to the database.
    This method allows you to add a new member to the database.

    Args:
        member (dict[str, Any]): _description_

    Returns:
        _type_: _description_
    """
    conn = get_connection()

    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            args = [
                member.member_id,
                member.name.en if member.name and hasattr(
                    member.name, 'en') else None,
                member.name.en if member.name and hasattr(
                    member.name, 'ar') else None,
                member.place_of_birth,
                member.date_of_birth,
                member.address,
                str(member.national_id_no),
                str(member.club_id_no),
                member.passport_no,
                member.date_joined,
                member.mobile_no,
                member.home_contact,
                member.email,
                member.facebook_url,
                member.school_name,
                member.education_type,
                member.father_name,
                member.father_contact,
                member.father_job,
                member.mother_name,
                member.mother_contact,
                member.mother_job,
                member.guardian_name,
                member.guardian_contact,
                member.guardian_relationship,
                member.hobbies,
                member.health_issues,
                member.medications,
                member.qr_code_url,
                member.image_url,
                member.national_id_url,
                member.parent_national_id_url,
                member.club_id_url,
                member.passport_url,
                member.birth_certificate_url,
                1 if member.photo_consent == True else 0,
                1 if member.conditions_consent == True else 0,
            ]
            cursor.callproc("AddMember", args)
            conn.commit()
            return {"message": "Member added", "MemberDetails": member}
