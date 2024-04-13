"""
Represent en entry recorded in arxiv.
Generaly used to validate incoming data to ensure
types and rules.
"""
import datetime
from pydantic import BaseModel, Field


class Article(BaseModel):
    """
    Represent en entry recorded in arxiv.
    Generaly used to validate incoming data to ensure
    types and rules.

    Parameters
    ----------
    id: str
        Unique identifier of the record

    dates: [date]
        Dates of the record into Arxix

    modified_at: date
        Last date of modification of the record

    title: str
        Title of the scientific paper in the record

    creators: [str]
        List of the creators of the paper

    subjects: [str]
        Scientif subjects of the paper

    description: str
        Summary of the paper

    Returns
    -------
    None
    """
    id: str = Field(min_length=1, max_length=32, alias="id")
    dates: list = Field(default=[])
    modified_at: datetime.datetime
    title: str = Field(min_length=1)
    creators: list = Field(default=[])
    subjects: list = Field(default=[])
    description: str = Field(min_length=1)
