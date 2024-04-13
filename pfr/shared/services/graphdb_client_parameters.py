from pydantic import BaseModel
from pydantic import Field


class GraphDBClientParameters(BaseModel):
    """
    Keep and validate the parameters for a DBConnector. A pydantic
    model is used to validate the entries on init.
    """

    host: str = Field(min_length=1, max_length=255, alias="GRAPHDB_HOST")
    port: int = Field(gt=0, alias="GRAPHDB_PORT")
    time_out_ms: int = Field(gt=0, alias="GRAPHDB_TIME_OUT_MS")
    user: str = Field(min_length=1, max_length=255, alias="GRAPHDB_USER")
    pwd: str = Field(min_length=1, max_length=255, alias="GRAPHDB_PWD")