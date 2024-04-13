"""
Represent an output response from the API endpoint /ask/.
Generally used to validate incoming data to ensure
types and rules.
"""

from pydantic import BaseModel, Field, UUID4, validator


class PostOutputApiAskQuestion(BaseModel):
    """
    Represents an entry retrieved from arXiv.
    Generally used to validate incoming data to ensure
    types and rules. It is put in the redis queue used to post
    question from the API. It is given also as a reponse to the user
    who asked a question.

    Parameters
    ----------
    token: UUID4
        Unique identifier of the record

    state: str, optional
        State of the question (default is "pending")

    question_content: str
        Content of the question, must be at least 5 characters long

    Returns
    -------
    None
    """

    token: UUID4 = Field(
        description="The token which you will use to get the answer to your question"
    )
    question_content: str = Field(
        min_length=5,
        description="The content of the question you asked",
    )

    @validator("token")
    def add_prefix_to_token(cls, token):
        return f"/ask/{token}"
