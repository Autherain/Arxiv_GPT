from pydantic import BaseModel
from pydantic import Field


class RedisClientParameters(BaseModel):
    """
    Keep and validate the parameters for a DBConnector. A pydantic
    model is used to validate the entries on init.
    """

    host: str = Field(min_length=1, max_length=255, alias="REDIS_HOST")
    port: int = Field(gt=0, alias="REDIS_PORT")
    time_out_ms: int = Field(gt=0, alias="REDIS_TIME_OUT_MS")
    user: str = Field(min_length=1, max_length=255, alias="REDIS_USER")
    pwd: str = Field(min_length=1, max_length=255, alias="REDIS_PWD")