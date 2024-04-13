""" 
Retriever entry point

Begin by query the DB to know the last time the API was requested.
If no data is present in the DB, then the date in the app configuration
will be used.

After, the app requests the API a determined number of times, required to get 
all the missings or updated records. To do that, we iterate over the 
get_records() method of the RecordFecther until we got everything. We wait a
sepcific duration between each requests to avoid the API rejection.

Each batch of records returned by the API is written in the DB before the next
request.

If everything goes as expected, we write in the DB the current time as the last
time the API was requested.
"""

import time
import datetime
import sys

# App services & repositories
from retriever.boot import logger
from retriever.boot import record_fetcher
from retriever.boot import params_repository
from retriever.boot import update_article_queue

#----------------------
# LAUNCH APP
#----------------------

if __name__ == "__main__":
    
    logger.info("=== Begin ARXIV articles retrieval ===")
    last_retrieval_time :datetime.datetime = \
        params_repository.get_api_retrieve_time()

    if last_retrieval_time is not None:
        logger.info(
            "- Last retrieval time : %s."
            % last_retrieval_time.isoformat()
        )
        last_retrieval_time = last_retrieval_time.date()
    else :
        logger.info("- Last retrieval time : Not found.")

    if record_fetcher._parameters.limit > 0:
        logger.info(
            "- Limit number of articles : %s articles."
            % record_fetcher._parameters.limit
        )
    else:
        logger.info("- Limit number of articles : No limit.")

    logger.info("- Begin articles fetching.")
    try:
        documents_retrieved = 0

        for records_response in record_fetcher.get_records(last_retrieval_time):
            documents_retrieved += len(records_response.records)

            logger.info("---> %s / %s articles (Limit: %s) | Arxiv response time : %s s | Parse time : %s s" 
                % (documents_retrieved,
                   records_response.resumption_total_size if records_response.resumption_total_size is not None else documents_retrieved,
                   record_fetcher._parameters.limit if record_fetcher._parameters.limit > 0 else "No limit",
                   record_fetcher.metrics_fetch_time,
                   record_fetcher.metrics_convert_time)
            )
            
            for article in records_response.records:
                update_article_queue.push_task_update_article(article)
                
            # Wait few second to avoid rejection from the API
            time.sleep(record_fetcher._parameters.check_time)

    except Exception as e:
        logger.error(
            f"An error occured during records retrieval : {e}",
            exc_info=True)

    params_repository.update_api_retrieve_time(datetime.datetime.now())
    logger.info("- Fetch Done.")
    logger.info("=== End of ARXIV articles retrieval ===")