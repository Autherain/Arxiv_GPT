from pydantic import BaseModel
from pydantic import Field


class OntologyGraphdbQaParameters(BaseModel):
    """
    Keep and validate the parameters for langchain ontology_qa. A pydantic
    model is used to validate the entries on init.
    """

    graphdb_host: str = Field(
        min_length=1,
        max_length=255,
        alias="GRAPHDB_HOST",
    )
    graphdb_user: str = Field(
        min_length=1,
        max_length=255,
        alias="GRAPHDB_USER",
    )
    graphdb_pwd: str = Field(
        min_length=1,
        max_length=255,
        alias="GRAPHDB_PWD",
    )
    graphdb_port: int = Field(
        gt=0,
        alias="GRAPHDB_PORT",
    )
    graphdb_url_end: str = Field(
        min_length=1,
        max_length=255,
        alias="GRAPHDB_URL_END",
    )

    openai_api_key: str = Field(
        min_length=1,
        max_length=255,
        alias="LANGCHAIN_OPENAI_API_KEY",
    )

    openai_model: str = Field(
        min_length=1,
        max_length=255,
        alias="LANGCHAIN_OPENAI_MODEL",
    )

    langchain_graphdb_qa_prompt: str = Field(
        min_length=5, alias="LANGCHAIN_GRAPHDB_QA_PROMPT"
    )

    graphdb_query_ontology: str = Field(
        min_length=5, alias="LANGCHAIN_GRAPHDB_QUERY_ONTOLOGY"
    )
