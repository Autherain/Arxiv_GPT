"""
Repository used to query the database
against the params collection.

The params collection keep dynamic configuration
elements of the application.
"""

from pydantic import ValidationError
from shared.models.output_redis_api_ask_question import OutputRedisApiAskQuestion
from shared.models.get_ask_input import GetAskInput
from shared.models.redis_popped_api_ask_question import RedisPoppedApiAskQuestion

import logging
import json
import datetime

from redis import Redis
from redis import RedisError


class ParamsRepository:
    """
    Repository used to query the database
    against the params collection.

    The params collection keep dynamic configuration
    elements of the application.

    Parameters
    ------
    db: Database
        The Mongo database in wich the record collection
        is kept.

    Attributes
    ------
    _logger: Logger
        The repository logger

    _collection: Collection
        The database collection where the documents are
        kept.
    """

    def __init__(self, db: Redis) -> None:
        self._logger = logging.getLogger(__name__)

        if not isinstance(db, Redis):
            self._logger.error(
                "The Redis connector given to the repository is not of "
                "the right type : %s",
                type(db),
                exc_info=True,
            )
            raise RuntimeError("Redis Bad Type")
        self.db = db

    def update_api_retrieve_time(self, param: datetime.datetime) -> None:
        """
        Update the last time data was retrieved from the API.

        Parameters
        ------
        param: datetime.datetime

        Return
        ------
        None

        Raises
        ------
        TypeError
            - If the given parameter is not of the right type

        PyMongoError
            - If the writing procedure on the database went wrong


        """
        if not isinstance(param, datetime.datetime):
            self._logger.error(
                "The parameter given for update of api retrieval is not "
                "of the right type : %s",
                type(param),
                exc_info=True,
            )
            raise TypeError("Parameter Bad Type")

        try:
            self.db.set("param_retrieval_time", param.isoformat())
        except RedisError as e:
            self._logger.error(
                "Failed to update api retrieval time document : %s.", e, exc_info=True
            )
            raise RuntimeError("Fail Update Api Retrieval Time") from e

    def get_api_retrieve_time(self):
        """
        Get the last time data was retrieved from the API.

        Parameters
        ------
        None

        Return
        ------
        datetime | None

        Raises
        ------
        PyMongoError
            - If the read procedure on the database went wrong

        KeyError
            - If the document retrieved from the database lack the
            'retrieval_time' key.
        """

        try:
            result = self.db.get("param_retrieval_time")
        except RedisError as e:
            self._logger.error(
                "Failed to get api retrieval time document : %s.", e, exc_info=True
            )
            raise RuntimeError("Fail Get Api Retrieval Time") from e

        try:
            if result is not None:
                result = datetime.datetime.fromisoformat(result)
        except KeyError as e:
            self._logger.error(
                "The api retrieval time document lack the 'retrieval_time' " "key. ",
                exc_info=True,
            )
            raise RuntimeError("Wrong Api Retrieval Time Document") from e

        return result

    def set_key_value_api_ask_question(
        self, output_redis_api_ask_question: OutputRedisApiAskQuestion
    ) -> None:
        """
        Set a key-value pair in Redis for the API endpoint post /ask/.

        Parameters
        ----------
        output_redis_api_ask_question : OutputRedisApiAsk
            An instance of OutputRedisApiAsk class containing.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the parameter provided is not an instance of OutputRedisApiAsk.
        RuntimeError
            If there is a failure in setting the key-value pair in Redis.

        Notes
        -----
        This method sets the key-value pair in Redis using the token from the
        OutputRedisApiAsk instance
        as the key and the JSON representation of the model data as the value.
        It handles potential errors
        such as invalid parameter type or Redis operation failure,
        logging relevant information for debugging.
        """
        if not isinstance(output_redis_api_ask_question, OutputRedisApiAskQuestion):
            self._logger.error(
                "The parameter given for set of api retrieval is not "
                "of the right type : %s",
                type(output_redis_api_ask_question),
                exc_info=True,
            )
            raise TypeError("Parameter Bad Type")

        try:
            self.db.set(
                output_redis_api_ask_question.token,
                output_redis_api_ask_question.model_dump_json(),
            )
        except RedisError as e:
            self._logger.error(
                "Failed to set in redis the key '%s' with value '%s': %s.",
                output_redis_api_ask_question.token,
                output_redis_api_ask_question.model_dump_json(),
                e,
                exc_info=True,
            )
            raise RuntimeError(
                "Failed to set key value into redis for the endpoint /ask/"
            ) from e

    def get_key_value_api_ask_question(
        self,
        get_ask_input: GetAskInput,
    ) -> OutputRedisApiAskQuestion:
        """
        Get the value associated with a key. It is used in endpoints get /ask/<token>.

        Parameters
        ----------
        get_ask_input: GetAskInput
            An instance of GetAskInput containing the token.

        Returns
        -------
        output_redis_api_ask_question
            The value associated with the provided token.

        Raises
        ------
        TypeError
            If the parameter provided is not an instance of GetAskInput.
        RuntimeError
            If there is a failure in retrieving the value from Redis.

        """

        if not isinstance(get_ask_input, GetAskInput):
            self._logger.error(
                "The parameter given for get of api retrieval is not "
                "of the right type: %s",
                type(get_ask_input),
                exc_info=True,
            )
            raise TypeError("Parameter Bad Type")
        try:
            result = self.db.get(get_ask_input.token)
            if result is None:
                self._logger.error(
                    "No value found in Redis for the key '%s'.",
                    get_ask_input.token,
                )
                raise RuntimeError("No value found in Redis for the given key")
        except RedisError as e:
            self._logger.error(
                "Failed to retrieve from Redis "
                "the value associated with the key '%s': %s.",
                get_ask_input.token,
                e,
                exc_info=True,
            )
            raise RuntimeError(
                "Failed to get value from Redis for the endpoint get_key_value_api_ask_question"
            ) from e

        try:
            data = json.loads(result)
        except json.JSONDecodeError as e:
            self._logger.error(
                "Failed to decode the JSON %s coming from Redis: %s",
                result,
                e,
                exc_info=True,
            )
            raise RuntimeError("Failed to transform the JSON coming from REDIS") from e

        try:
            output_redis_api_ask_question = OutputRedisApiAskQuestion(**data)
        except ValidationError as e:
            self._logger.critical(
                exc_info=True,
                msg=f"Faulty parameter into the OutputRedisApiAskQuestion: {e}.",
            )
            raise RuntimeError("Bad Config Parameter") from e

        return output_redis_api_ask_question

    def set_key_value_error_qa_question(
        self, output_redis_error_qa_question: RedisPoppedApiAskQuestion
    ) -> None:
        """ """
        if not isinstance(output_redis_error_qa_question, RedisPoppedApiAskQuestion):
            self._logger.error(
                "The parameter given for set of api retrieval is not "
                "of the right type : %s",
                type(output_redis_error_qa_question),
                exc_info=True,
            )
            raise TypeError("Parameter Bad Type")

        try:
            self.db.set(
                output_redis_error_qa_question.token,
                json.dumps(
                    {
                        "token": output_redis_error_qa_question.token,
                        "state": "ERROR",
                        "question_content": output_redis_error_qa_question.question_content,
                    }
                ),
            )
        except RedisError as e:
            self._logger.error(
                "Failed to set in redis the key '%s' with value '%s': %s.",
                output_redis_error_qa_question.token,
                output_redis_error_qa_question.model_dump_json(),
                e,
                exc_info=True,
            )
            raise RuntimeError(
                "Failed to set key value error of the qa process into redis"
            ) from e
