"""
Represent the the API endpoint /ask/ as a key value in 
redis.
Generally used to validate incoming data to ensure
types and rules.
"""

from uuid import UUID
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class OutputRedisApiAskQuestion(BaseModel):
    """
    Represent an key value that is posted with SET Method of
    Redis db. It is used with post /ask/ endpoint
    It is posted to redis as key value to be later changed as
    an answer to the question is found.
    It will be used by someone that has to write code to retrieve the response
    from the user.
    """

    token: str = Field(
        description="The token given to you when you posted your question"
    )
    state: str = Field(default="pending", description="The state of your question")
    question_content: str = Field(
        min_length=5, description="The content of your question"
    )
    question_answer: str = Field(
        default="None", description="The answer to your question"
    )
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None

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
