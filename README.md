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

As of now, any desired queries must manually be added to the database using `POST` requests. The recommended tool for interacting with this API in development is [Postman](https://www.postman.com/). See this code snippet for the proper fields to include in a gived `POST` request:

```Python
@app.route('/query', methods=['POST'])
def add_query():
    term = request.json['term'] # string
    city = request.json['city'] # string
    state = request.json['state'] # two-character string
    radius = request.json['radius'] # two-character string
    entryLevel = request.json['entryLevel'] # boolean
    ...
```

Recall that `app.py` must be running in order to send any requests.

Note that `radius` must be chosen from one of the given options among Indeed's filters. Otherwise, there is a risk of this filter not being applied and potentially of other filters not being applied as well. In the production website, all radius options will be given in a dropdown list to prevent this issue.

By default, `indeed.py` searches for results from the past day. If a different range is desired, please modify the `fromage` variable from line 63 in accordance with the options provided by Indeed:

```Python
...
new_url = current_url + "&radius=" + self.radius + "&fromage=1"
...
```

With all desired queries in the database and `app.py` running, simply run `scrape.py` and wait. A browser window will appear where the searches can be visible, however this will be removed in a future update. Note that the provided implementation of `scrape.py` exists purely for development purposes. Without modification, this file will address only the first query in the database and print all results to the console before submitting `POST` requests for each job. Jobs will then be accessible from `db.sqlite`.

## Warnings
- Keep in mind that `debug` is set to `true` in `app.py` during development:

    ```Python
    if __name__ == '__main__':
        app.run(debug=True)
    ```
- It is recommended that the `job` table be emptied at the end of every `fromage` cycle (1 day by default). On the production server, such behavior will be automated.
- Be mindful of any issues which may be encountered when altering `radius` and `fromage`, as mentioned in [Usage](#Usage).

## Roadmap
- [X] Core API functionality
- [ ] Give error if incorrect radius in a query
- [ ] Switch from Flask-SQLAlchemy to Flask and SQLAlchemy
- [ ] Switch from SQLite to MySQL/MariaDB for production
- [ ] Address webscraping failure when using `headless` option for Selenium
- [ ] Add support for other job listing websites
    - [ ] Glassdoor
    - [ ] Monster
    - [ ] ...
- [ ] Create Dockerfile for local deployment of the API
- [ ] Create job listing aggregation website using the API with user authentication and saved queries per user

## Contributing
Webscraping applications are fequently broken by website updates. If you are the first to notice such an event here, please feel free to address it and submit a pull request. Similarly, you are welcome to work on any [Roadmap](#Roadmap) tasks which remain incomplete.

## License
All original software is licensed under the GPL-3.0 license. You are bound to the Terms of Service of any other websites with which you may interact while using this software. [Developer](https://github.com/f-104) does not support Terms of Service violations.