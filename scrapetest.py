# from lxml import html
# import requests
# import time
# page = requests.get('https://info.binance.com/en/currencies/monero')
# tree = html.fromstring(page.content)
# time.sleep(2)
# buyers = tree.xpath('//div[@class="container"]/text()')
# print(str(buyers))
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys

# options = Options()
# options.add_argument('headless')
# options.binary_location = 'chromedriver'


# driver = webdriver.Chrome(chrome_options=options)
# driver.get("https://info.binance.com/en/currencies/monero")
# # assert "Python" in driver.title
# elem = driver.find_element(By.XPATH, '//div[@class="container"]')
# # elem.send_keys("selenium")
# # elem.send_keys(Keys.RETURN)
# # assert "Python" in driver.title
# # print(str(elem.text))
# for i in enumerate(elem):
#     print(str(i))

# driver.close()



import os  
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.binary_location = 'chromedriver'

driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), chrome_options=chrome_options)
driver.get("http://www.duo.com")

magnifying_glass = driver.find_element_by_id("js-open-icon")
if magnifying_glass.is_displayed():
    magnifying_glass.click()
else:
    menu_button = driver.find_element_by_css_selector(".menu-trigger.local")
    menu_button.click()

search_field = driver.find_element_by_id("site-search")
search_field.clear()
search_field.send_keys("Olabode")
search_field.send_keys(Keys.RETURN)
# assert "Looking Back at Android Security in 2016" in driver.page_source driver.close()