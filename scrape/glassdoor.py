from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
import os
import sys

import logging
logger = logging.getLogger(__name__)

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.add_argument("--window-size=1920,1080")
options.add_argument('headless')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--whitelisted-ips")

load_dotenv()
gdUser = os.environ.get('gdUser')
gdPass = os.environ.get('gdPass')

class gJobs:
    def __init__(self, city, id, radius, state, term):
        self.city = city
        self.id = id
        self.radius = radius
        self.state = state
        self.term = term

    def get(self):
        def checkPopup():
            try:
                closePopup = driver.find_element(By.XPATH, '//*[@id="qual_ol"]/div[1]')
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(closePopup)).click()
            except NoSuchElementException:
                pass

        driver = webdriver.Remote("http://sel:4444/wd/hub", options=options)

        try:
            driver.get("https://glassdoor.com")
            checkPopup()
        except Exception:
            logger.exception('Unable to reach Glassdoor. Either Glassdoor is down or there is no internet connection')
            sys.exit(1)

        attempts = 5
        for k in range(attempts):
            try:
                # Login to Glassdoor
                login_btn = driver.find_element(By.XPATH, '//*[@id="SiteNav"]/nav/div[2]/div/div/div/button')
                login_btn.click()
                driver.implicitly_wait(1)
                user_input = driver.find_element(By.XPATH, '//*[@id="userEmail"]')
                pass_input = driver.find_element(By.XPATH, '//*[@id="userPassword"]')
                user_input.send_keys(gdUser)
                pass_input.send_keys(gdPass)
                send_info_btn = driver.find_element(By.XPATH, '//*[@id="LoginModal"]/div/div/div[2]/div[2]/div[2]/div/div/div/div[3]/form/div[3]/div[1]/button')
                send_info_btn.click()
                checkPopup()

                # Search for current job term
                termInputArea = driver.find_element(By.XPATH, '//*[@id="sc.keyword"]')
                termInputArea.send_keys(Keys.CONTROL, "a")
                termInputArea.send_keys(self.term)
                termInputArea.send_keys(Keys.ENTER)
                checkPopup()
                jobs_link = driver.find_element(By.XPATH, '//*[@id="Discover"]/div/div/div[1]/div[1]/div[3]/a')
                jobs_link.click()
                checkPopup()

                # Search for current job location
                cityInput = self.city + ", " + self.state
                cityInputArea = driver.find_element(By.XPATH, '//*[@id="sc.location"]')
                cityInputArea.send_keys(Keys.CONTROL, "a")
                cityInputArea.send_keys(cityInput)
                cityInputArea.send_keys(Keys.ENTER)
                checkPopup()

                # Apply radius filter
                radius_dropdown = driver.find_element(By.XPATH, '//*[@id="filter_radius"]')
                radius_dropdown.click()
                radius_XPATH_base = '//*[@id="PrimaryDropdown"]/ul/li'
                radius_XPATH_full = ''

                radius_options = ['0', '5', '10', '15', '25', '50', '100']
                found = False
                for i,j in enumerate(radius_options):
                    if self.radius == j:
                        radius_to_add = str(i + 1)
                        radius_XPATH_full = f'{radius_XPATH_base}[{radius_to_add}]'
                        found = True
                        break
                if not found:
                    logger.error('Invalid radius')
                    sys.exit(1)

                radius_to_click = driver.find_element(By.XPATH, radius_XPATH_full)
                radius_to_click.click()

                # Get results from last day only
                time_dropdown = driver.find_element(By.XPATH, '//*[@id="filter_fromAge"]')
                time_dropdown.click()
                last_day = driver.find_element(By.XPATH, '//*[@id="PrimaryDropdown"]/ul/li[2]')
                last_day.click()

                # Close a popup not covered by checkPopup()
                actions = ActionChains(driver)
                actions.send_keys(Keys.ESCAPE)
                actions.perform()
            except Exception:
                l = k + 1
                if l < attempts:
                    logger.warning(f'Selenium error: failed attempt {l} of {attempts}, trying again')
                    continue
                else:
                    logger.exception('Failed to navigate website using Selenium, XPATH of one or more elements has likely changed')
                    sys.exit(1)
            break

        # Parse each page and add results to list
        glassdoor_jobs = []
        while True:
            try:
                page = driver.page_source
                page_jobs = self.__parse_index(page)
                glassdoor_jobs.extend(page_jobs)
            except Exception:
                logger.exception('Error downloading webpage')
                sys.exit(1)
            
            try:
                nextButton = driver.find_element(By.CSS_SELECTOR, 'a[data-test="pagination-next"]')
                nextButton.click()
            except Exception:
                logger.info('Reached end of results')
                driver.quit()
                return glassdoor_jobs

    def __parse_index(self, htmlcontent):
        soup = bs(htmlcontent, 'lxml')

        # Find all jobs on page
        try:
            jobs_container = soup.find(attrs={"id": "MainCol"})
        except Exception:
            logger.error("Error finding jobs_container, returning empty list")
            return []

        try:
            job_items = jobs_container.find_all(class_='react-job-listing')
        except Exception:
            logger.error("Error finding job items, returning empty list")
            return []

        # Get all job data from current page
        all_jobs = []
        for job_elem in job_items:
            title_elem_raw = job_elem.find('a', class_='jobLink job-search-key-1rd3saf eigr9kq1')
            company_elem_raw = job_elem.find('a', class_='job-search-key-l2wjgv e1n63ojh0 jobLink')
            loc_elem_raw = job_elem.find('span', class_='css-1buaf54 pr-xxsm job-search-key-iii9i8 e1rrn5ka4')
            url_elem_raw = job_elem.find('a', class_='jobLink')

            # Skip invalid jobs
            if None in (title_elem_raw, company_elem_raw, loc_elem_raw, url_elem_raw):
                logger.info('Skipped invalid job')
                continue

            # Clean data
            title_elem = title_elem_raw.text.strip()
            company_elem = company_elem_raw.text.strip()
            loc_elem = loc_elem_raw.text.strip()
            url_elem_href = url_elem_raw.get('href')
            if url_elem_href is None:
                continue
            url_elem = f'https://glassdoor.com{url_elem_href}'

            # Append job to list as dictionary
            item = {
                "title": title_elem,
                "company": company_elem,
                "location": loc_elem,
                "href": url_elem,
                "query_id": self.id
            }
            all_jobs.append(item)

        return all_jobs