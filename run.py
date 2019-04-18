from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from os import environ, path
import re
import urllib.request
import time
import datetime
import sys

print(sys.version)

user_name = environ["FACEBOOK_USERNAME"]
password = environ["FACEBOOK_PASSWORD"]

print("Logging in as {}.".format(user_name))

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
            raise NoSuchElementException("Not found: {}".format(css_selector))
    
    def _element_exists(self, css_selector):
        try:
            self.driver.find_element_by_css_selector(css_selector)
            return True
        except NoSuchElementException:
            return False

class PhotoIteratorPageObject(PageObject):
    def __init__(self, driver):
        PageObject.__init__(self, driver)
        self.driver = driver
        self.index = -1
        self.image_failed = []

    def __iter__(self):
        return self

    def _get_src(self):
        try:
            self._get_element_by_text("View full size").click()
            # Is an image
            time.sleep(0.1)
            tabs = self.driver.window_handles
            self.driver.switch_to.window(tabs[1])
            self._wait_for_element("body img")
            image_src = self.driver.find_element_by_tag_name("body img").get_attribute("src")
            self.driver.close()
            self.driver.switch_to.window(tabs[0])
            return image_src, 'jpg'
        except NoSuchElementException:
            # Might be a video
            self._get_element_of_type_with_href_matching_regex('a', 'video_redirect').click()
            time.sleep(0.1)
            tabs = self.driver.window_handles
            self.driver.switch_to.window(tabs[1])
            self._wait_for_element("body video")
            image_src = self.driver.current_url
            self.driver.close()
            self.driver.switch_to.window(tabs[0])
            return image_src, 'mp4'

    def _get_current_image(self):
        try:
            self._current_link().click()
            date_string = self.driver.find_element_by_tag_name("abbr").text
            date = self._parse_date(date_string)
            image_src, file_type = self._get_src()
            formatted_date_string = "{:%Y_%m_%d}".format(date)
            return (image_src, formatted_date_string, file_type)
        except NoSuchElementException:
            raise NoSuchElementException("Error fetching image for url: {}".format(self.driver.current_url))
        finally:
            self.driver.back()

    def next(self):
        while True:
            self.index += 1
            if self._current_link() is None:
                break
            try:
                return self._get_current_image()
            except NoSuchElementException as e:
                print("Fetching image failed.")
                print(e)
                self.image_failed.append(e)

        raise StopIteration()

    __next__ = next

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
        try:
            next_page_link = self._get_element_by_text("See more photos")
        except NoSuchElementException:
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

try:
    iterator = page.get_photo_link_iterator()
    for (link, name, filetype) in iterator:
        i = 0
        full_name = "output/{}_{:0>3}.{}".format(name, i, filetype)
        while path.exists(full_name):
            i += 1
            full_name = "output/{}_{:0>3}.{}".format(name, i, filetype)

        urllib.request.urlretrieve(link, full_name)
        count += 1
finally:
    driver.close()
    print("Downloaded {}.".format(count))

    if len(iterator.image_failed) > 0:
        print("Errors:")
        for error in iterator.image_failed:
            print(error)


print("Done.")