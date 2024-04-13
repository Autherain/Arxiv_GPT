from pydantic import BaseModel
from pydantic import Field


class ChatgptVectorGraphdbQaParameters(BaseModel):
    openai_api_key: str = Field(
        min_length=1,
        max_length=255,
        alias="CHATPGPT_VECTOR_GRAPHDB_OPENAI_API_KEY",
    )

    openai_model: str = Field(
        min_length=1,
        max_length=255,
        alias="CHATPGPT_VECTOR_GRAPHDB_OPENAI_MODEL",
    )

    human_prompt: str = Field(
        min_length=1,
        alias="CHATPGPT_VECTOR_GRAPHDB_HUMAN_PROMPT",
    )

    system_prompt: str = Field(
        min_length=1,
        alias="CHATPGPT_VECTOR_GRAPHDB_SYSTEM_PROMPT",
    )
