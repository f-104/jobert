<div align="center">
  <img alt="Logo goes here" style="width: 25%; height: auto" src="logo.png">
</div>
<h1 align="center">Jobert API</h1>
<p align ="center">
  The Jobert API is a RESTful API which aims to automate mass execution of job searches.
</p>

### Table of Contents
- [Summary](#Summary)
- [Usage](#Usage)
- [Warnings](#Warnings)
- [Roadmap](#Roadmap)
- [Contributing](#Contributing)
- [License](#License)

## Summary
The Jobert API is meant to take in queries, run searches, and provide results, although it is a complete CRUD application. The end goal here is to use this API on the backend of a simplified job search website to save non-technical users massive amounts of time.

This project is loosely based on [Job Search Automation Software](https://github.com/f-104/jsas) and will be prioritized in terms of maintenance.

## Usage
First, see the `Pipfile` and ensure all dependencies are met. Also note that the appropriate Webdriver for Selenium is required. For users of Google Chrome, [Chromedriver](https://chromedriver.chromium.org/downloads) is recommended.

From the Flask-SQLAlchemy documentation, you will need to run the following commands in the root directory of the project once:

```Python
>>> from yourapplication import db
>>> db.create_all()
```

This facilitates the initial creation of the local database which will contain all queries and jobs.

Queries can be added to the database through `POST` requests. The recommended tool for interacting with this API in development is [Postman](https://www.postman.com/). See this code snippet for the proper fields to include in a given `POST` request:

```Python
@app.route('/query', methods=['POST'])
def add_query():
    term = request.json['term'] # string
    city = request.json['city'] # string
    state = request.json['state'] # two-character string
    radius = request.json['radius'] # two-character string
    ...
```

Recall that `app.py` must be running in order to send any requests.

Note that `radius` must be chosen from one of the given options among Indeed's filters. Otherwise, there is a risk of this filter not being applied and potentially of other filters not being applied as well. Query `POST`/`PUT` requests containing an invalid choice of radius are refused.

With all desired queries in the database and `app.py` running, simply run `scrape.py` and wait. This relies upon `indeed.py` and `glassdoor.py` to scrape all valid results for a given query posted to those websites in the past day. Debugging information is logged to `jobert-scrape.log`. Recommended usage is to deploy on a local device or VPS and utilize `cron` to clear the database of stale jobs and run `scrape.py` daily.

## Warnings
- Keep in mind that `debug` is set to `True` in `app.py`. This should be set to `False` in production:

    ```Python
    if __name__ == '__main__':
        app.run(debug=True)
    ```
- This version of the API usis SQLite in order to provide a ready-to-use implementation for those who wish to clone the repository and use Jobert 'as is.' A more secure alternative such as MySQL, MariaDB, or PostgreSQL is recommended for production use.

## Roadmap
- [X] Core API functionality
- [X] Give error if incorrect radius in a query
- [X] Address webscraping failure when using `headless` option for Selenium
- [X] Add support for Glassdoor
- [X] Implement logging to a file
- [X] Switch from SQLite to MySQL for production (See [Warnings](#Warnings))
- [ ] Create Dockerfile for local deployment of the API

## Contributing
Webscraping applications are fequently broken by website updates. If you are the first to notice such an event here, please feel free to address it and submit a pull request. Similarly, you are welcome to work on any [Roadmap](#Roadmap) tasks which remain incomplete.

## License
All original software is licensed under the GPL-3.0 license. You are bound to the Terms of Service of any other websites with which you may interact while using this software. [Developer](https://github.com/f-104) does not support Terms of Service violations.