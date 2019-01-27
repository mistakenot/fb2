from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import environ, path
import re
import urllib
import time
import datetime

user_name = environ["FACEBOOK_USERNAME"]
password = environ["FACEBOOK_PASSWORD"]

class PageObject:
    def __init__(self, driver):
        self.driver = driver

    def _get_element_by_text(self, text):
        xpath = "//*[contains(text(), '{}')]".format(text)
        return driver.find_element_by_xpath(xpath)

    def _get_element_by_href(self, url):
        return self.driver.find_element_by_css_selector('a[href="{}"]'.format(url))

    def _get_element_of_type_with_text_matching_regex(self, tag, regex):
        elements = self.driver.find_elements_by_tag_name(tag)
        for element in elements:
            result = re.search(regex, element.text)
            if result is not None:
                return element
        return None

    def _get_element_of_type_with_href_matching_regex(self, tag, regex):
        elements = self.driver.find_elements_by_tag_name(tag)
        for element in elements:
            href = element.get_attribute("href")
            if href is not None:
                result = re.search(regex, href)
                if result is not None:
                    return element
        return None

    def _wait_for_element(self, css_selector):
        try:
            _ = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        except:
            raise "Not found: {}".format(css_selector)

class PhotoIteratorPageObject(PageObject):
    def __init__(self, driver):
        PageObject.__init__(self, driver)
        self.driver = driver
        self.index = 0

    def __iter__(self):
        return self

    def next(self):
        if self._current_link() is None:
            raise StopIteration()

        self._current_link().click()
        date_string = self.driver.find_element_by_tag_name("abbr").text
        date = self._parse_date(date_string)
        formatted_date_string = "{:%Y_%m_%d}".format(date)
        self._get_element_by_text("View full size").click()
        time.sleep(0.1)
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[1])
        time.sleep(1)
        image_src = self.driver.find_element_by_tag_name("img").get_attribute("src")
        self.driver.close()
        self.driver.switch_to.window(tabs[0])
        self.driver.back()
        self.index += 1
        return (image_src, formatted_date_string)

    def _parse_date(self, date_string):
        for fmt in ('%d %b %Y', '%d %B %Y'):
            try:
                stripped = date_string.split(' at ')[0]
                return datetime.datetime.strptime(stripped, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def _current_link(self):
        links = self.driver.find_elements_by_css_selector("a.ba")
        if len(links) == 0:
            return None
        if self.index >= len(links) and not self._next_page():
            return None
        else:
            links = self.driver.find_elements_by_css_selector("a.ba")
        return links[self.index]

    def _next_page(self):
        next_page_link = self._get_element_by_text("See more photos")
        if next_page_link is None:
            return False
        next_page_link.click()
        self.index = 0
        return True

class FacebookPageObject(PageObject):
    
    def __init__(self, driver):
        PageObject.__init__(self, driver)
        self.driver = driver

    def login(self, username, password):
        
        facebook_login_url = "https://m.facebook.com"
        self.driver.get(facebook_login_url)
        self.driver.find_element_by_id("m_login_email").send_keys(username)
        self.driver.find_element_by_css_selector("input[name='pass']").send_keys(password)
        self.driver.find_element_by_css_selector("input[name='login']").click()
        # self.driver.find_element_by_css_selector('a[href="/login/save-device/cancel/?flow=interstitial_nux&nux_source=regular_login"]').click()
        self._get_element_by_href("/login/save-device/cancel/?flow=interstitial_nux&nux_source=regular_login").click()

    def go_to_photos(self, page=0):
        self._get_element_by_text("Profile").click()
        self._get_element_by_text("Photos").click()
        element = self._get_element_of_type_with_text_matching_regex("a", "^See*")
        element.click()
        for _ in range(0, page):
            self.driver.find_element_by_css_selector("#m_more_item a").click()

    def get_photo_link_iterator(self):
        return PhotoIteratorPageObject(self.driver)

driver = webdriver.Firefox()
page = FacebookPageObject(driver)
page.login(user_name, password)
page.go_to_photos()
count = 0

for (link, name) in page.get_photo_link_iterator():
    i = 0
    full_name = "output/{}_{}.jpg".format(name, i)
    while path.exists(full_name):
        i += 1
        full_name = "output/{}_{}.jpg".format(name, i)

    urllib.urlretrieve(link, full_name)
    print("Created {}.".format(full_name))

print("done")
# driver.get(facebook_login_url)
# assert "Python" in driver.title
# elem = driver.find_element_by_name("q")
# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
# driver.close()