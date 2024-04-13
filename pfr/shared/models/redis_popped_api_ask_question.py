from pydantic import BaseModel, Field, validator
from uuid import UUID


class RedisPoppedApiAskQuestion(BaseModel):
    """
    Represents data popped from a Redis list in the context of the API's "ask" functionality.
    Used to validate incoming data to ensure types and rules.
    """

    token: str
    question_content: str = Field(min_length=5)

    @validator("token")
    def validate_token(cls, v):
        # Check if the token starts with /ask/
        if not v.startswith("/ask/"):
            raise ValueError("Token must start with /ask/")

        # Extract the UUID part of the token
        uuid_part = v.split("/ask/")[1]

        # Validate that the UUID part is a valid UUID
        try:
            UUID(uuid_part)
        except ValueError:
            raise ValueError("Token must contain a valid UUID after /ask/")

        return v
