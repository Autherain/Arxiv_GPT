"""
This function is used to return the db_engine. If the engine
is not created, the engine is initialized with the parameters.
If the engine is not initialized and no parameters are given,
an error is raised.
"""
import logging
from redis import Redis
from redis import RedisError
from pydantic import ValidationError

from shared.services.redis_client_parameters import RedisClientParameters

def get_redis_client(app_config: dict = None) -> Redis:
    """
    This function is used to return the db_engine. If the engine
    is not created, the engine is initialized with the parameters.
    If the engine is not initialized and no parameters are given,
    an error is raised.

    It ensure the presence and coherence of configuration
    parameters needed by the service.

    Parameters
    ----------
    app_config
        The configuration dictionary of the application.

    Returns
    -------
    MongoClient

    Exceptions
    -------
    RuntimeError
        Something went wrong during setup process.

    """
    logger = logging.getLogger(__name__)

    if not isinstance(app_config, dict):
        logger.critical(
            exc_info=True,
            msg="The configuration given to the db client is not of dict type "
            "and the engine isn't initialized."
        )
        raise RuntimeError("Bad Config Type")

    try:
        parameters = RedisClientParameters(**app_config)
    except ValidationError as e:
        logger.critical(
            exc_info=True,
            msg=f"Faulty parameter into the db client's configuration : {e}."
        )
        raise RuntimeError("Bad Config Parameter") from e

    try:
        return Redis(
            host=parameters.host,
            port=parameters.port,
            username=parameters.user,
            password=parameters.pwd,
            ssl=False,
            decode_responses=True
        )
    except RedisError as e:
        logger.critical(
            exc_info=True,
            msg=f"Could not initialize DB client : {e}."
        )
        raise RuntimeError("DB Client Init Error") from e
