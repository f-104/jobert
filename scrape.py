import requests
import indeed
import glassdoor

# Run scraping functions for Indeed and Glassdoor using each query in the database, then post jobs to database
def main():
    base_url = "http://127.0.0.1:5000/"
    queryResponseRaw = requests.get(base_url + "query")
    all_queries = queryResponseRaw.json()

    i = 1
    j = len(all_queries)
    
    for query_item in all_queries:
        print(f'Scraping Indeed for query {i} of {j}...')
        jobs_list_indeed = indeed.iJobs(**query_item).get()
        print(f'Scraping Glassdoor for query {i} of {j}...')
        jobs_list_glassdoor = glassdoor.gJobs(**query_item).get()

        jobs_url = base_url + "job"

        for i_job in jobs_list_indeed:
            print(f'Posting Indeed jobs for query {i} of {j}...')
            send_job = requests.post(jobs_url, json=i_job)

        for g_job in jobs_list_glassdoor:
            print(f'Posting Glassdoor jobs for query {i} of {j}...')
            send_job = requests.post(jobs_url, json=g_job)

        i += 1
    
    print("All jobs posted for this cycle")

if __name__ == '__main__':
    main()