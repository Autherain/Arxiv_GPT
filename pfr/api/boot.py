import sys

# APP CONFIGURATION & LOGGER
# ----------------------
try:
    from shared.services.get_config import get_config

    config = get_config("api")
except RuntimeError as e:
    print("Failed to initialize application configuration :" f" {e}. Exiting...")
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
# ----------------------
try:
    from shared.services.get_redis_client import get_redis_client

    db_client = get_redis_client(config)
except RuntimeError:
    logger.critical(exc_info=True, msg="Failed to initialize db client. Exiting...")
    sys.exit(1)

# Repository initialisation
# ----------------------
try:
    from shared.repositories.params_repository import ParamsRepository

    params_repository = ParamsRepository(db_client)
except RuntimeError:
    logger.critical(
        exc_info=True, msg="Failed to initialize params repositories. Exiting..."
    )
    sys.exit(1)

try:
    from shared.repositories.update_queues import UpdateQueues

    update_article_queue = UpdateQueues(db_client)
except RuntimeError:
    logger.critical(
        exc_info=True, msg="Failed to initialize update articles queue. Exiting..."
    )
    sys.exit(1)

# FastAPI intialization
# ----------------------

try:
    from api.main import app

except RuntimeError:
    logger.critical(exc_info=True, msg="Failed to load the API code. Exiting...")
    sys.exit(1)
