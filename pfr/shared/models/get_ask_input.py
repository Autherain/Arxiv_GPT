from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

from uuid import UUID


class GetAskInput(BaseModel):
    """
    Schema for the input data required for getting a response to a question at
    the endpoint GET /ask/<token>

    Attributes
    ----------
    token : str
        The token associated with the question.
    """

    token: str = Field(description="The token given to you when you asked a question")

    @validator("token")
    def validate_token(cls, v):
        # Check if the token starts with /ask/
        if not v.startswith("/ask/"):
            raise HTTPException(status_code=422, detail="Token must start with /ask/")

        # Extract the UUID part of the token
        uuid_part = v.split("/ask/")[1]

        # Validate that the UUID part is a valid UUID
        try:
            UUID(uuid_part)
        except ValueError:
            raise HTTPException(
                status_code=422, detail="Token must contain a valid UUID after /ask/"
            )

        return v
