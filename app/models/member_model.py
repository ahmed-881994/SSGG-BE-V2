from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Unique member identifier - This is the business key used throughout the system
    # Indexed for fast lookups, unique constraint ensures no duplicates
    member_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    # Member names in English and Arabic
    # Supports bilingual member management
    name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    name_ar: Mapped[str] = mapped_column(String(255), nullable=True)

    # Personal information fields
    place_of_birth: Mapped[str] = mapped_column(String(255), nullable=True)  # Birth location
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=True)          # Birth date for age calculations
    address: Mapped[str] = mapped_column(Text, nullable=True)                # Residential address (can be long)

    # Identity document numbers
    national_id_no: Mapped[str] = mapped_column(String(50), nullable=True)   # National ID number
    club_id_no: Mapped[str] = mapped_column(String(50), nullable=True)       # Club membership ID
    passport_no: Mapped[str] = mapped_column(String(50), nullable=True)      # Passport number
    
    # Membership information
    date_joined: Mapped[str] = mapped_column(String(4), nullable=True)       # Year as string (based on existing schema)

    # Contact information
    mobile_number: Mapped[str] = mapped_column(String(20), nullable=True)    # Primary mobile contact
    home_contact: Mapped[str] = mapped_column(String(20), nullable=True)     # Home/landline contact
    email: Mapped[str] = mapped_column(String(255), nullable=True)           # Email address
    facebook_url: Mapped[str] = mapped_column(String(500), nullable=True)    # Social media profile
    
    # Educational information
    school_name: Mapped[str] = mapped_column(String(255), nullable=True)     # Current/last school
    education_type: Mapped[str] = mapped_column(String(100), nullable=True)  # Education level/type

    # Family information - Father details
    father_name: Mapped[str] = mapped_column(String(255), nullable=True)     # Father's full name
    father_contact: Mapped[str] = mapped_column(String(20), nullable=True)   # Father's contact number
    father_job: Mapped[str] = mapped_column(String(255), nullable=True)      # Father's occupation

    # Family information - Mother details
    mother_name: Mapped[str] = mapped_column(String(255), nullable=True)     # Mother's full name
    mother_contact: Mapped[str] = mapped_column(String(20), nullable=True)   # Mother's contact number
    mother_job: Mapped[str] = mapped_column(String(255), nullable=True)      # Mother's occupation

    # Guardian information (for cases where parents are not available)
    guardian_name: Mapped[str] = mapped_column(String(255), nullable=True)           # Guardian's full name
    guardian_contact: Mapped[str] = mapped_column(String(20), nullable=True)         # Guardian's contact
    guardian_relationship: Mapped[str] = mapped_column(String(100), nullable=True)   # Relationship to member

    # Personal interests and health information
    hobbies: Mapped[str] = mapped_column(Text, nullable=True)           # Member's hobbies and interests
    health_issues: Mapped[str] = mapped_column(Text, nullable=True)     # Any health conditions to be aware of
    medications: Mapped[str] = mapped_column(Text, nullable=True)       # Current medications

    # Document and media URLs
    # These store file paths/URLs for various documents and photos
    qr_code_url: Mapped[str] = mapped_column(String(500), nullable=True)           # QR code for quick identification
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)             # Profile photo
    national_id_url: Mapped[str] = mapped_column(String(500), nullable=True)       # Scanned national ID document
    parent_national_id_url: Mapped[str] = mapped_column(String(500), nullable=True) # Parent's national ID document
    club_id_url: Mapped[str] = mapped_column(String(500), nullable=True)           # Club ID card image
    passport_url: Mapped[str] = mapped_column(String(500), nullable=True)          # Passport scan
    birth_certificate_url: Mapped[str] = mapped_column(String(500), nullable=True) # Birth certificate scan

    # Consent and agreement flags
    # Boolean fields to track various permissions and agreements
    photo_consent: Mapped[bool] = mapped_column(Boolean, default=False)      # Permission to use photos
    conditions_consent: Mapped[bool] = mapped_column(Boolean, default=False) # Agreement to terms/conditions
    
    
    # Relationships to other tables
    # These define how this table relates to other entities in the database
    
    # One-to-many relationship with entity_members table
    # A member can be part of multiple entities (teams, groups, etc.)
    entity_memberships = relationship("EntityMember", back_populates="member")
    
    # One-to-many relationship with attendance table
    # A member can have multiple attendance records
    # attendance_records = relationship("Attendance", back_populates="member")
    
    def __repr__(self):
        return f"<Member(member_id={self.member_id}, name_en={self.name_en})>"

    def to_dict(self) -> dict:
        """
        Convert member to dictionary.
        
        Returns:
            dict: A dictionary representation of the member.
        """
        return {
            "member_id": self.member_id,
            "name": {
                "en": self.name_en,
                "ar": self.name_ar
            },
            # "entities": [self.entity.to_dict() for self in self.entity_memberships],
            "place_of_birth": self.place_of_birth,
            "date_of_birth": self.date_of_birth,
            "address": self.address,
            "national_id_no": self.national_id_no,
            "club_id_no": self.club_id_no,
            "passport_no": self.passport_no,
            "date_joined": self.date_joined,
            "mobile_number": self.mobile_number,
            "home_contact": self.home_contact,
            "email": self.email,
            "facebook_url": self.facebook_url,
            "school_name": self.school_name,
            "education_type": self.education_type,
            "father_name": self.father_name,
            "father_contact": self.father_contact,
            "father_job": self.father_job,
            "mother_name": self.mother_name,
            "mother_contact": self.mother_contact,
            "mother_job": self.mother_job,
            "guardian_name": self.guardian_name,
            "guardian_contact": self.guardian_contact,
            "guardian_relationship": self.guardian_relationship,
            "hobbies": self.hobbies,
            "health_issues": self.health_issues,
            "medications": self.medications,
            "qr_code_url": self.qr_code_url,
            "image_url": self.image_url,
            "national_id_url": self.national_id_url,
            "parent_national_id_url": self.parent_national_id_url,
            "club_id_url": self.club_id_url,
            "passport_url": self.passport_url,
            "birth_certificate_url": self.birth_certificate_url,
            "photo_consent": self.photo_consent,
            "conditions_consent": self.conditions_consent
        }

    def to_dict_brief(self) -> dict:
        """
        Convert member to a brief dictionary representation.
        """
        return {
            "member_id": self.member_id,
            "name_en": self.name_en,
            "name_ar": self.name_ar,
        }