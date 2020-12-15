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
browser = webdriver.Firefox(options = options, firefox_binary = binary)
browser.get (argv[1])
browser.fullscreen_window()

# def find_element(xpath):
#     return WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, xpath)))

def find_element(xpath):
    element = None
    while not element:
        try:
            element = browser.find_element_by_xpath(xpath)
        except NoSuchElementException:
            sleep(1)
            element = None
    return element

find_element('//form[@class="signin"]//input[@name="credentials:login"]').send_keys('vnc-om')
find_element('//input[@name="credentials:pass"]').send_keys('zsRrNDJZcrymd5IH0H9U5rGI0JIgdl6m!')
find_element('//button[@name="signin:dialog:footer:buttons:0:button"]').click()

find_element('//canvas[contains(@id,"-slide-")]')  # Just wait for it ...
print('Canvas found.')

browser.execute_script('e = document.getElementsByClassName("wb-zoom-block"); '
                     + 'if (e && e.length > 0) '
                     + '  for (var i = 0, len = e.length; i < len; i++) '
                     + '    e[i].style.display = "none"; '
                     + 'e = document.getElementsByClassName("wb-tabbar"); '
                     + 'if (e && e.length > 0) '
                     + '  e[0].style.display = "none"; '
                     + 'e = document.getElementsByClassName("menu"); '
                     + 'if (e && e.length > 0) '
                     + '  e[0].style.display = "none"; '
                     + 'e = document.getElementsByClassName("sidebar ui-resizable"); '
                     + 'if (e && e.length > 0) '
                     + '  e[0].style.display = "none"; '
                     + 'e = document.getElementById ("chatPanel"); '
                     + 'if (e) '
                     + '  e.style.display = "none"; '
                     + 'var canvases = document.getElementsByTagName ("canvas"); '
                     + 'var item; '
                     + 'for (var i = 0, len = canvases.length; i < len; i++) '
                     + '  { '
                     + '    item = canvases[i]; '
                     + '    if (item.id && item.id.indexOf ("-slide-") >= 0) '
                     + '      e = item; '
                     + '  } '
                     + 'e = e.parentElement; '
                     + 'e.style.position = "absolute"; '
                     + 'e.style.left = 0; '
                     + 'e.style.top = 0; '
                     + 'e.style.margin = "5px"; '
                     + 'e.style.border = "none"; '
                     + 'e.style.boxShadow = "none"; '
                     + 'e = e.parentElement; '
                     + 'while (e) '
                     + '  { '
                     + '    e.style.position = "inherit"; '
                     + '    e = e.parentElement; '
                     + '  } ')
