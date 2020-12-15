#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from sys import argv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from selenium.common.exceptions import NoSuchElementException

def find_element(xpath):
    element = None
    while not element:
        try:
            element = browser.find_element_by_xpath(xpath)
        except NoSuchElementException:
            sleep(1)
            element = None
    return element

def click_element(xpath):
    element = find_element(xpath)
    success = False
    while not success:
        try:
            element.click()
            success = True
        except:
            sleep(1)

options = Options()  
options.add_argument('--disable-infobars') 
options.add_argument('--no-sandbox') 
options.add_argument('--kiosk') 
options.add_argument('--window-size=1920,1080')
options.add_argument('--window-position=0,0')
options.add_experimental_option("excludeSwitches", ['enable-automation']);   
options.add_argument('--shm-size=1gb') 
options.add_argument('--disable-dev-shm-usage') 
options.add_argument('--start-fullscreen') 

browser = webdriver.Chrome(executable_path='chromedriver', options=options)
browser.get (argv[1])

find_element('//input[contains(@id,"_join_name")]').send_keys('VNC')
find_element('//button[@id="room-join"]').click()
browser.find_element_by_id('yes').click()
click_element('//button[@aria-label="Close Join audio modal"]')
click_element('//div[@id="container"]//div[contains(@class,"videoContainer--")]//button')
