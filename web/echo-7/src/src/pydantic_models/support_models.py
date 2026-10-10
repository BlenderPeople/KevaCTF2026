from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SupportMessage(BaseModel):
    topic: str = Field(..., min_length=1, max_length=100, description="Support topic")
    description: str = Field(
        ..., min_length=10, max_length=2000, description="Problem description"
    )
    email: Optional[str] = Field(None, max_length=50, description="Contact email")

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v):
        if not v or not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Description must contain at least 10 characters")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return v.strip() if v else v
