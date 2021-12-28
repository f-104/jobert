<div align="center">
  <img alt="Logo goes here" style="width: 25%; height: auto" src="logo.png">
</div>
<h1 align="center">Jobert API</h1>
<p align ="center">
  The Jobert API is a RESTful API created to automate mass execution of job searches.
</p>
<div align="center">
  <a href="LICENSE"><img alt="License badge" src="https://img.shields.io/github/license/f-104/jobert-api?color=blue"></a>
  <a href="https://github.com/f-104/jobert-api/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/f-104/jobert-api?color=blue"></a>
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/f-104/jobert-api?color=blue">
  <a href="https://github.com/f-104/jobert-api/releases"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/f-104/jobert-api?color=blue&include_prereleases"></a>
  <img alt="Python Version" src="https://img.shields.io/badge/python-3.9%2B-blue">
</div>

### Table of Contents
- [Summary](#Summary)
- [Usage](#Usage)
- [Contributing](#Contributing)
- [License](#License)

## Summary
The Jobert API is meant to take in queries, automate job searches, and regularly provide results, although it is a complete CRUD application for both queries and jobs independent of each other. The end goal is to use this API on the backend of a simplified job search website to save non-technical users massive amounts of time. In its current iteration, Jobert is intended for use in a home server or VPS environment.

This project is loosely based on [Job Search Automation Software](https://github.com/f-104/jsas) and takes priority regarding development.

## Usage
The preferred method of running the Jobert API is to use Docker. Instructions for standalone use are provided below as well. In any case, the first step is to download the most recent release and create the file `.env` in the `scrape` folder:

```python
# scrape/.env
# Glassdoor Credentials go here
gdUser = "Paste Glassdoor email here"
gdPass = "Paste Glassdoor password here"
```

### Docker (Preferred)
By default, Jobert will scrape Indeed and Glassdoor for new jobs based on all stored queries at 12:00 UTC every day. If a different schedule is desired, please modify the CronJob in `docker/scrape/Dockerfile`, line 14, as necessary.

From `docker-compose.yml`, ports 3307, 4444, and 8080 are required. Ensuring that Docker is installed and these ports are free, run these commands to pull the necessary images:

```
docker-compose pull sel
docker-compose pull mysql
```

At this point, you can use docker-compose to start Jobert:

```
docker-compose up
```

The Jobert API is now running.

### Standalone

First, with Python installed, run `pip install -r requirements.txt` to install necessary Python modules. Also note that the appropriate Webdriver for Selenium is required. For users of Google Chrome, [Chromedriver](https://chromedriver.chromium.org/downloads) is recommended.

As Jobert is designed for use with docker-compose, some lines will need to be modified in order for it to function on its own:

| File                    | Line  | Modification                                |
|-------------------------|-------|---------------------------------------------|
| `app/app.py`            | `7`   | Change database URI                         |
| `scrape/scrape.py`      | `11`  | Change directory in `filename`              |
| `scrape/scrape.py`      | `14`  | Change base_url to `http://localhost:8080/` |
| `scrape/indeed.py`      | `42`  | Change webdriver type, remove URL argument  |
| `scrape/glassdoor.py`   | `49`  | Change webdriver type, remove URL argument  |

For the database URI in `app.py`, you will need to ensure a SQL RDBMS is already installed and configured on the host system. Such configuration is beyond the scope of these instructions.

Regarding modifications to `indeed.py` and `glassdoor.py`, here is an example for Chrome users:

```Python
driver = webdriver.Chrome(options=options)
```

Now with configuration out of the way, run `app/prep.py` once. This file can then be discarded.

The Jobert API is now installed on the host system. Scraping may be automated, or the user may run `scrape/scrape.py` when required. `app/app.py` must be running at all times in order to maintain functionality.

---

Queries can be added to the database through `POST` requests to `/query`. Provided here is an example of an acceptable `POST` request:

```json
{
    "term": "Software Engineer",
    "city": "New York",
    "state": "NY",
    "radius": "25"
}
```

Of particular note are restrictions on the value of `radius`:

```Python
# Parameters allowed by radius filter on Indeed, Glassdoor
radius_options = ['0', '5', '10', '15', '25', '50', '100']
```

Query `POST`/`PUT` requests containing an invalid choice of radius are refused.

Debugging information is logged to `scrape.log`. In the Docker implementation, this file is located at `/jobert/scrape.log` within the `scrape` container.

Job results can be gotten through `GET` requests to `/job`. Note that each job has a `query_id` linking it to a query, so requests can filter by query.

It is recommended in most cases that older jobs be periodically removed from the `job` table within the database. If such functionality is desired, the simplest way to accomplish this would be to utilize the [MySQL Event Scheduler](https://dev.mysql.com/doc/refman/5.7/en/event-scheduler.html) within the MySQL Docker container.

## Contributing
Webscraping applications are fequently broken by website updates. If you are the first to notice such an event here, please feel free to open an issue or to address it and submit a pull request.

## License
All original software is licensed under the GPL-3.0 license. You are bound to the Terms of Service of any other websites with which you may interact while using this software. [Developer](https://github.com/f-104) does not support Terms of Service violations.