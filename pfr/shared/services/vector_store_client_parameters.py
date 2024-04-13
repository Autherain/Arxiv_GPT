from pydantic import BaseModel
from pydantic import Field


class VectorStoreClientParameters(BaseModel):
    """
    Keep and validate the parameters for a DBConnector. A pydantic
    model is used to validate the entries on init.
    """

    host: str = Field(min_length=1, max_length=255, alias="NEO4J_HOST")
    user: str = Field(min_length=1, max_length=255, alias="NEO4J_USER")
    pwd: str = Field(min_length=1, max_length=255, alias="NEO4J_PWD")
    vector_index: str = Field(min_length=1, max_length=255, alias="NEO4J_VECTOR")
    api_key: str = Field(min_length=1, max_length=255, alias="CHAT_GPT_KEY")