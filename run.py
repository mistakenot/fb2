from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from os import environ
import re

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

class PhotoIteratorPageObject(PageObject):
    def __init__(self, driver):
        super(driver)
        self.driver = driver
        self.links = self.driver.find_elements_by_css_selector("a.ba")

    def __iter__(self):
        if len(self.links) > 0:
            self.current_link = self.links[0]
        else:
            self.current_link = None
        return self
    
    def __next__(self):
        
        self.current_link.click()
        self._get_element_by_text("View full size").click()
        image_src = self.driver.find_element_by_name("img").get_attribute("src")
        return image_src


class FacebookPageObject(PageObject):
    
    def __init__(self, driver):
        super(driver)
        self.driver = driver

    def login(self, username, password):
        
        facebook_login_url = "https://m.facebook.com"
        self.driver.get(facebook_login_url)
        self.driver.find_element_by_id("m_login_email").send_keys(username)
        self.driver.find_element_by_css_selector("input[name=pass]").send_keys(password)
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
        links = self.driver.find_elements_by_css_selector("a.ba")

driver = webdriver.Firefox()
page = FacebookPageObject(driver)
page.login(user_name, password)
page.go_to_photos()

print("done")
# driver.get(facebook_login_url)
# assert "Python" in driver.title
# elem = driver.find_element_by_name("q")
# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
# driver.close()