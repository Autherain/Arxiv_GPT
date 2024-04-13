"""
This function is used to return the db_engine. If the engine
is not created, the engine is initialized with the parameters.
If the engine is not initialized and no parameters are given,
an error is raised.
"""
import logging
from pydantic import ValidationError

from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings

from shared.services.vector_store_client_parameters import VectorStoreClientParameters

def get_vector_store_client(app_config: dict = None) -> Neo4jVector:
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
    Neo4jVector

    Exceptions
    -------
    RuntimeError
        Something went wrong during setup process.

    """
    logger = logging.getLogger(__name__)

    if not isinstance(app_config, dict):
        logger.critical(
            exc_info=True,
            msg="The configuration given to the neo4j client is not of dict type "
            "and the engine isn't initialized."
        )
        raise RuntimeError("Bad Config Type")

    try:
        parameters = VectorStoreClientParameters(**app_config)
    except ValidationError as e:
        logger.critical(
            exc_info=True,
            msg=f"Faulty parameter into the neo4j client's configuration : {e}."
        )
        raise RuntimeError("Bad Config Parameter") from e

    try:
        return Neo4jVector.from_existing_index(
                OpenAIEmbeddings(api_key=parameters.api_key),
                url=parameters.host,
                username=parameters.user,
                password=parameters.pwd,
                index_name=parameters.vector_index,
            )
    except Exception as e:
        logger.critical(
            exc_info=True,
            msg=f"Could not initialize Neo4J client : {e}."
        )
        raise RuntimeError("Neo4J Client Init Error") from e
