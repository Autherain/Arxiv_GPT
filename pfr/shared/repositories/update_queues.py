"""
Repository used to query the database against the params collection.
The params collection keeps dynamic configuration elements of the application.
"""

import logging
import datetime
import json
from typing import Union

from redis import Redis
from redis import RedisError

from pydantic import ValidationError

from shared.models.article import Article
from shared.models.redis_popped_api_ask_question import RedisPoppedApiAskQuestion
from shared.models.post_output_api_ask_question import PostOutputApiAskQuestion


class UpdateQueues:
    """Class for updating queues in the database."""

    def __init__(self, db: Redis) -> None:
        """
        Initializes the UpdateQueues instance with a Redis database connection.

        Parameters:
        - db (Redis): The Redis database connection.
        """
        self._logger = logging.getLogger(__name__)

        # Check if db parameter is of type Redis
        if not isinstance(db, Redis):
            self._logger.error(
                "The Redis connector given to the repository is not of the right type: %s",
                type(db),
                exc_info=True,
            )
            raise RuntimeError("Redis Bad Type")
        self.db = db

    def push_task_update_article(self, article: Article) -> None:
        """
        Pushes an article update task to the database queue.

        Parameters:
        - article (Article): The article to be updated.
        """
        if not isinstance(article, Article):
            self._logger.error(
                "The parameter given for update of api retrieval is not of the right type: %s",
                type(article),
                exc_info=True,
            )
            raise RuntimeError("Parameter Bad Type")

        try:
            # Push the article update task to the database queue
            self.db.lpush("task_update_article", article.model_dump_json())
        except RedisError as e:
            self._logger.error(
                "Failed to push an update article task: %s.", e, exc_info=True
            )
            raise RuntimeError("Fail Update Api Retrieval Time") from e

    def api_lpush_question(
        self, output_api_ask_question: PostOutputApiAskQuestion
    ) -> None:
        """
        Pushes a question received from the API to the Redis queue by the api post /ask/ question.

        Parameters:
        - output_api_ask_question (PostOutputApiAskQuestion): The question received from the API.
        """
        if not isinstance(output_api_ask_question, PostOutputApiAskQuestion):
            self._logger.error(
                "The parameter given for update of api retrieval is not of the right type: %s",
                type(PostOutputApiAskQuestion),
                exc_info=True,
            )
            raise TypeError("Parameter Bad Type")

        try:
            # Push the question to the Redis queue named api_ask_question
            self.db.lpush("api_ask_question", output_api_ask_question.model_dump_json())
        except RedisError as e:
            self._logger.error(
                "Failed to push an update article task: %s.", e, exc_info=True
            )
            raise RuntimeError("Fail Push Update Task") from e

    def api_pop_question(self) -> Union[RedisPoppedApiAskQuestion, None]:
        """
        Pops a question from the Redis queue used by the api post /ask/ question.

        Returns:
        - Union[RedisPoppedApiAskQuestion, None]: The popped question or None if the queue is empty.
        """
        try:
            # Pop a question from the Redis queue named api_ask_question
            result = self.db.rpop("api_ask_question")
            if result is not None:
                result = RedisPoppedApiAskQuestion(**json.loads(result))
            return result
        except RedisError as e:
            self._logger.error(
                "Failed to pop an API ask question task: %s.", e, exc_info=True
            )
            raise RuntimeError("Fail Pop API Ask Question Task") from e
        except ValidationError as e:
            self._logger.error(
                "Failed to convert a popped API ask question task: %s.", e
            )
            return None

    def pop_task_update_article(self) -> Article:
        """
        Pops an article update task from the Redis queue.

        Returns:
        - Article: The popped article update task or None if the queue is empty.
        """
        try:
            # Pop an article update task from the Redis queue named task_update_article
            result = self.db.rpop("task_update_article")
            if result is not None:
                result = Article(**json.loads(result))
            return result
        except RedisError as e:
            self._logger.error(
                "Failed to pop an update article task: %s.", e, exc_info=True
            )
            raise RuntimeError("Fail Pop Update Task") from e
        except ValidationError as e:
            self._logger.error("Failed to convert a popped update article task: %s.", e)
            return None
