from os.path import dirname, abspath, join

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.ie.webdriver import WebDriver


def chrome_driver() -> WebDriver:
    # chromedriver-win64\chromedriver.exe
    service = Service(join(dirname(dirname(abspath(__file__))) ,"chromedriver-win64\chromedriver.exe"))
    driver = webdriver.Chrome(service=service)

    return driver