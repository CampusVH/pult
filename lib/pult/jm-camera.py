#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from sys import argv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options  
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

options = Options()  

binary = FirefoxBinary('/usr/lib/firefox-esr/firefox-bin')
browser = webdriver.Firefox(options = options, firefox_binary = binary, service_log_path = '/dev/null')
browser.get (argv[1])
browser.fullscreen_window()

def try_click_element(xpath):
    try:
        element = browser.find_element_by_xpath(xpath)
    except NoSuchElementException:
        element = None
    if element:
        element.click()

sleep(2)
try_click_element('//button[@id="toggleFilmstripButton"]')
sleep(1)
try_click_element('//button[contains(@class,"styledFlag__DismissButton")]')
sleep(1)
try_click_element('//button[contains(@class,"styledFlagActions__StyledButton")]')
sleep(1)
try_click_element('//button[contains(@class,"styledFlag__DismissButton")]')
sleep(1)
try_click_element('//button[contains(@class,"styledFlagActions__StyledButton")]')
