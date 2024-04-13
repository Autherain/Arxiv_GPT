from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime

from shared.models.post_output_api_ask_question import PostOutputApiAskQuestion
from shared.models.output_redis_api_ask_question import OutputRedisApiAskQuestion
from shared.models.get_ask_input import GetAskInput

from api.boot import update_article_queue
from api.boot import params_repository

router = APIRouter(
    prefix="/ask",
    tags=["ask"],
)


class PostAskInput(BaseModel):
    """
    Schema for the input data required for posting a question.

    Attributes
    ----------
    content : str
        The content of the question.
    """

    content: str = Field(min_length=5, description="The question you want to ask")


@router.post("/")
async def post_question(input_data: PostAskInput) -> PostOutputApiAskQuestion:
    """
    Endpoint to post a question.

    Parameters
    ----------
    input_data : PostAskInput
        The input data containing the content of the question.

    Returns
    -------
    OutputApiAskQuestion
        The response containing the token, state, and question content.
    """

    # Will check weither what the user sent conform
    question_content = PostOutputApiAskQuestion(
        token=uuid4(),
        question_content=input_data.content,
    )
    update_article_queue.api_lpush_question(question_content)

    # Will send a key value to redis to be later changed
    # by the code when an answer will be found
    key_value_ask_question_redis = OutputRedisApiAskQuestion(
        token=question_content.token,
        question_content=input_data.content,
        start_date=datetime.now(),
    )

    params_repository.set_key_value_api_ask_question(key_value_ask_question_redis)

    return question_content


@router.get("/<token>")
async def get_response(token: GetAskInput = Depends()) -> OutputRedisApiAskQuestion:
    """
    Endpoint to get a response to a question.

    Parameters
    ----------
    input_data : GetAskInput
        The input data containing the token associated with the question.

    Returns
    -------
    OutputApiAskQuestion : OutputRedisApiAskQuestion
        The state of your question
    """
    value_of_token = params_repository.get_key_value_api_ask_question(token)

    return value_of_token
