"""
Represent a list of records returned by 
the API and the metadata with it
"""
from pydantic import BaseModel, Field

class ArticlesPage(BaseModel):
    """
    Represent a list of records returned by 
    the API and the metadata with it

    Parameters
    ----------

    records: [Record]
        List of records

    resumption_token: str
        resumption token used to retrieve the next list page

    resumption_token_cursor: str
        the number of the last record element on the total
        requested

    resumption_total_size: str
        Total number of elements to retrieve in the request

    Returns
    -------
    None
    """
    records: list = Field(default=[])
    resumption_token: str = Field(default=None)
    resumption_token_cursor: str = Field(default=None)
    resumption_total_size: str = Field(default=None)
