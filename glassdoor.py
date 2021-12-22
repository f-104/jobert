from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
import os
import sys

from helpers import HttpHelpers

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
#options.add_argument("--window-size=1920,1080")
#options.add_argument('headless')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--disable-extensions")

load_dotenv()
gdUser = os.environ.get('gdUser')
gdPass = os.environ.get('gdPass')

class gJobs:
    def __init__(self, city, entryLevel, id, radius, state, term):
        self.helpers = HttpHelpers()
        self.city = city
        self.entryLevel = entryLevel
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
        
        def checkOtherPopup():
            try:
                closePopup = driver.find_element(By.XPATH, '//*[@id="JAModal"]/div/div[2]/span')
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(closePopup)).click()
            except NoSuchElementException:
                pass

        driver = webdriver.Chrome(options=options)
        driver.get("https://glassdoor.com")
        checkPopup()

        # Login to Glassdoor
        login_btn = driver.find_element(By.XPATH, '//*[@id="SiteNav"]/nav/div[2]/div/div/div/button')
        login_btn.click()
        driver.implicitly_wait(1)
        user_input = driver.find_element(By.XPATH, '//*[@id="userEmail"]')
        pass_input = driver.find_element(By.XPATH, '//*[@id="userPassword"]')
        #user_input.click()
        user_input.send_keys(gdUser)
        #user_input.send_keys(Keys.ESCAPE)
        #pass_input.click()
        pass_input.send_keys(gdPass)
        send_info_btn = driver.find_element(By.XPATH, '//*[@id="LoginModal"]/div/div/div[2]/div[2]/div[2]/div/div/div/div[3]/form/div[3]/div[1]/button')
        send_info_btn.click()
        checkPopup()

        # Search for current job term
        termInputArea = driver.find_element(By.XPATH, '//*[@id="sc.keyword"]')
        #termInputArea.click()
        termInputArea.send_keys(Keys.CONTROL, "a")
        termInputArea.send_keys(Keys.DELETE)
        termInputArea.send_keys(self.term)
        termInputArea.send_keys(Keys.ENTER)
        checkPopup()
        jobs_link = driver.find_element(By.XPATH, '//*[@id="Discover"]/div/div/div[1]/div[1]/div[3]/a')
        jobs_link.click()
        checkPopup()

        # Search for current job location
        cityInput = self.city + ", " + self.state
        cityInputArea = driver.find_element(By.XPATH, '//*[@id="sc.location"]')
        #cityInputArea.click()
        cityInputArea.send_keys(Keys.CONTROL, "a")
        cityInputArea.send_keys(Keys.DELETE)
        cityInputArea.send_keys(cityInput)
        cityInputArea.send_keys(Keys.ENTER)
        # still need to check glassdoor webpage for invalid city error
        checkPopup()

        # Apply radius filter
        radius_dropdown = driver.find_element(By.XPATH, '//*[@id="filter_radius"]')
        radius_dropdown.click()
        radius_XPATH_base = '//*[@id="PrimaryDropdown"]/ul/li'
        radius_XPATH_full = ''

        radius_options = ['0', '5,', '10', '15', '25', '50', '100']
        found = False
        for i in range(len(radius_options)):
            if self.radius == radius_options[i]:
                radius_to_add = str(i + 1)
                radius_XPATH_full = f'{radius_XPATH_base}[{radius_to_add}]'
                found = True
                break
        if not found:
            sys.exit('Error: invalid radius')

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

        # entryLevel filter not applicable on Glassdoor

        # Parse each page and add results to list
        glassdoor_jobs = []
        while True:
            page = driver.page_source
            if page is None:
                sys.exit('Error downloading webpage')
            
            page_jobs = self.__parse_index(page)
            glassdoor_jobs.extend(page_jobs)

            try:
                nextButton = driver.find_element(By.CSS_SELECTOR, 'a[data-test="pagination-next"]')
                nextButton.click()
            except:
                driver.quit()
                return glassdoor_jobs

    def __parse_index(self, htmlcontent):
        soup = bs(htmlcontent, 'lxml')

        # Find all jobs on page
        jobs_container = soup.find(attrs={"id": "MainCol"})
        if jobs_container is None:
            print("Error finding jobs_container\nReturning empty list")
            return []

        job_items = jobs_container.find_all(class_='react-job-listing')
        if job_items is None:
            print("Error finding job items\nReturning empty list")
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