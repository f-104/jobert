#!/usr/bin/env python
import requests
import logging
import indeed
import glassdoor

# Run scraping functions for Indeed and Glassdoor using each query in the database, then post jobs to database
def main():
    level = logging.DEBUG
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(filename='/jobert/scrape.log', level=level, format=fmt, filemode='w')
    logger = logging.getLogger(__name__)

    base_url = "http://app:8080/"
    queryResponseRaw = requests.get(base_url + "query")
    all_queries = queryResponseRaw.json()

    i = 1
    j = len(all_queries)

    for query_item in all_queries:
        logger.info(f'Scraping Indeed for query {i} of {j}...')
        jobs_list_indeed = indeed.iJobs(**query_item).get()
        logger.info(f'Scraping Glassdoor for query {i} of {j}...')
        jobs_list_glassdoor = glassdoor.gJobs(**query_item).get()
        jobs_url = base_url + "job"

        logger.info(f'Posting Indeed jobs for query {i} of {j}...')
        for i_job in jobs_list_indeed:
            send_job = requests.post(jobs_url, json=i_job)

        logger.info(f'Posting Glassdoor jobs for query {i} of {j}...')
        for g_job in jobs_list_glassdoor:
            send_job = requests.post(jobs_url, json=g_job)

        i += 1
    
    logger.info("All jobs posted for this cycle")

if __name__ == '__main__':
    main()