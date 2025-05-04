from typing import Any
from fastapi import HTTPException
from app.database.connectionmanager import connect
from app.schema.member import Member

def add_member_db(member: dict[str, Any]):
    """adds a new member to the database.
    This method allows you to add a new member to the database.

    Args:
        member (dict[str, Any]): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    conn = connect()

    if conn is not None:
        with conn as conn:
            try:
                cursor = conn.cursor()
                args = [
                    member.get("MemberID"),
                    member.get("Name").get("EN"),
                    member.get("Name").get("AR"),
                    member.get("PlaceOfBirth"),
                    member.get("DateOfBirth"),
                    member.get("Address"),
                    str(member.get("NationalIdNo")),
                    str(member.get("ClubIdNo")),
                    member.get("PassportNo"),
                    member.get("DateJoined"),
                    member.get("MobileNo"),
                    member.get("HomeContact"),
                    member.get("Email"),
                    member.get("FacebookURL"),
                    member.get("SchoolName"),
                    member.get("EducationType"),
                    member.get("FatherName"),
                    member.get("FatherContact"),
                    member.get("FatherJob"),
                    member.get("MotherName"),
                    member.get("MotherContact"),
                    member.get("MotherJob"),
                    member.get("GuardianName"),
                    member.get("GuardianContact"),
                    member.get("GuardianRelationship"),
                    member.get("Hobbies"),
                    member.get("HealthIssues"),
                    member.get("Medications"),
                    member.get("QRCodeURL"),
                    member.get("ImageURL"),
                    member.get("NationalIdURL"),
                    member.get("ParentNationalIdURL"),
                    member.get("ClubIdURL"),
                    member.get("PassportURL"),
                    member.get("BirthCertificateURL"),
                    1 if member.get("PhotoConsent") == True else 0,
                    1 if member.get("ConditionsConsent") == True else 0,
                ]
                cursor.callproc("AddMember", args)
                response = {"message": "Member added", "MemberDetails": member}
            except Exception as error:
                raise HTTPException(status_code=500, detail=error.args)
            finally:
                # insert_log(cursor, event, response, "AddMember")
                conn.commit()

    return response