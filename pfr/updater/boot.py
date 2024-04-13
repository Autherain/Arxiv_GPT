import sys

# APP CONFIGURATION & LOGGER
#----------------------
try:
    from shared.services.get_config import get_config
    config = get_config("updater")
except RuntimeError as e:
    print("Failed to initialize application configuration :"
          f" {e}. Exiting...")
    sys.exit(1)

try:
    import logging
    from shared.services.app_logger import AppLogger
    AppLogger(config)
    logger = logging.getLogger(__name__)
except RuntimeError:
    print("Failed to initialize logger. Exiting...")
    sys.exit(1)

# INIT Database connection
#----------------------
try:
    from shared.services.get_redis_client import get_redis_client
    db_client = get_redis_client(config)
except RuntimeError:
    logger.critical(
        exc_info=True,
        msg="Failed to initialize db client. Exiting..."
    )
    sys.exit(1)

try:
    from shared.services.graphdb_client import GraphDBClient
    graphdb_client = GraphDBClient(config)
except RuntimeError:
    logger.critical(
        exc_info=True,
        msg="Failed to initialize graphdb client. Exiting..."
    )
    sys.exit(1)

try:
    from shared.services.vector_store_client import get_vector_store_client
    vector_store = get_vector_store_client(config)
except RuntimeError:
    logger.critical(
        exc_info=True,
        msg="Failed to initialize vector store client. Exiting..."
    )
    sys.exit(1)

# Repository initialisation
#----------------------
try:
    from shared.repositories.params_repository import ParamsRepository
    params_repository = ParamsRepository(db_client)
except RuntimeError:
    logger.critical(
        exc_info=True,
        msg="Failed to initialize params repositories. Exiting..."
    )
    sys.exit(1)

try:
    from shared.repositories.update_queues import UpdateQueues
    update_article_queue = UpdateQueues(db_client)
except RuntimeError:
    logger.critical(
        exc_info=True,
        msg="Failed to initialize update articles queue. Exiting..."
    )
    sys.exit(1)

try:
    from updater.repositories.articles_repository import ArticleRepository
    article_repository = ArticleRepository(graphdb_client)
except RuntimeError:
    logger.critical(
        exc_info=True,
        msg="Failed to initialize article repository. Exiting..."
    )
    sys.exit(1)
