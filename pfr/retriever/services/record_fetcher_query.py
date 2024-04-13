
import datetime
from pydantic import BaseModel
from pydantic import Field

class RecordFetcherQuery(BaseModel):
    """Represent query parameters to Arxiv.

    Parameters
    ----------
    verb: str
        action requested on the API

    metadataPrefix: str
        format of the response data

    set: str
        subset of scientific papers to query

    from_date: date
        Retrieve records from this date.

    Returns
    -------
    None
    """

    verb: str = Field(min_length=1, max_length=32)
    metadataPrefix: str = Field(min_length=1, max_length=32)
    set: str = Field(min_length=1, max_length=32)
    from_: datetime.date = Field(alias="from")