from pydantic import BaseModel, Field


class EntityTransfer(BaseModel):

    member_id: str = Field(alias='MemberID')
    from_entity_id: int = Field(alias='FromEntityID')
    to_entity_id: int = Field(alias='ToEntityID')
    transfer_date: str = Field(alias='TransferDate')
