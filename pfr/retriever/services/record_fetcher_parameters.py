
import datetime
from pydantic import BaseModel
from pydantic import Field

class RecordFetcherParameters(BaseModel):
    """
    Keep and validate the parameters for a RecordFetcher. A pydantic
    model is used to validate the entries on init.

    Parameters
    ----------
    set: str
        A subset of arxiv dataset to fetch

    host
       Arxiv endpoint

    check_time
        Time between to checks
    """

    host: str = Field(min_length=1, max_length=65, alias="ARX_HOST")
    set: str = Field(min_length=1, max_length=65, alias="ARX_SET")
    check_time: int = Field(gt=0, alias="ARX_CHECK_TIME_S")
    time_out: int = Field(gt=0, alias="ARX_TIMEOUT")
    format: str = Field(min_length=1, max_length=65, alias="ARX_FORMAT")
    start_date: datetime.date = Field(alias="ARX_START_DATE")
    limit: int = Field(alias="ARX_LIMIT", gt=-1)