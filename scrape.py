import requests
import indeed
import glassdoor

base_url = "http://127.0.0.1:5000/"

queryResponseRaw = requests.get(base_url + "query")

all_queries = queryResponseRaw.json()

test_query = all_queries[0]

jobs_list_test = glassdoor.gJobs(**test_query).get()

for job in jobs_list_test:
    print(f'Sending:\n{job}')
    full_url = base_url + "job"
    send_job = requests.post(full_url, json=job)