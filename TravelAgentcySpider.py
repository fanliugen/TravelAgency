from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as  EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from pyquery import PyQuery as pq
import pymongo

import time
username = "18612002550"
password = "yu891201"
visit_url ="https://www.foxsaas.com/"
MAX_PAGE = 300

browser = webdriver.Chrome()
wait = WebDriverWait(browser,15)
browser.maximize_window()


def login():
    try:
        browser.get(visit_url)
        loginBtn = wait.until(EC.presence_of_element_located((By.LINK_TEXT,"登录")))
        loginBtn.click()

        usernameInput = wait.until(EC.presence_of_element_located((By.ID,"phone")))
        usernameInput.send_keys(username)

        nextBtn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT,"下一步")))
        nextBtn.click()


        time.sleep(5)

        passwordInput = wait.until(EC.presence_of_element_located((By.XPATH,'//input[@id="password"]')))
        passwordInput.send_keys(password)

        time.sleep(5)

        submit = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="formBox"]/form/div[2]/div/a')))
        submit.click()
        time.sleep(5)


        wait.until(EC.presence_of_element_located((By.LINK_TEXT,'潜在客户')))
    except ElementNotVisibleException as e:
        print('=====ElementNotVisibleException=====',e)
        login()



def index_page(page):
    try:
        if page > 1:
            input = wait.until(EC.presence_of_element_located((By.CLASS_NAME,"js-page-jump")))
            submit = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"js-page-jump-btn")))
            input.clear()
            input.send_keys(page)
            submit.click()
            time.sleep(15)
            js = 'document.getElementsByClassName("main-data")[0].scrollTop=10000'
            browser.execute_script(js)
            # wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME,"page-item page-item-active"),str(page)))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,".js-data-list .js-get-info")))
        get_Info()
    except TimeoutException as e:
        print('=====TimeOutError=====',e)
        index_page(page)
    except ElementNotInteractableException as e:
        print('=====ElementNotInteractableException=====',e)
        index_page(page)






def get_Info():
    html = browser.page_source
    doc = pq(html)
    items = doc('.js-data-list .js-get-info')
    for item in items.items():
        product = {
            'name': item.find('td:nth-child(3)').attr('title'),
            'catogory': item.find('td:nth-child(4)').attr('title'),
            'boss': item.find('td:nth-child(5)').attr('title'),
            'position': item.find('td:nth-child(6)').attr('title'),
             'phone': item.find('td:nth-child(7) .td-inner').text(),
            'email': item.find('td:nth-child(8)').attr('title'),
            'address':item.find('td:nth-child(9)').attr('title')

        }
        print(product)
        save_to_mongo(product)



MONGO_URL = 'localhost'
MONGO_DB = 'travelagency'
MONGO_COLLECTION = 'INFO'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def save_to_mongo(result):

    try:
        if db[MONGO_COLLECTION].insert(result):
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')


def main():
    condition = wait.until(EC.presence_of_element_located((By.ID,"searchvalue")))
    condition.clear()
    condition.send_keys("旅行社")
    condition.send_keys(Keys.ENTER)
    time.sleep(10)
    for i in range(40,MAX_PAGE + 1):
        index_page(i)
    browser.close()


if __name__ == '__main__':
    login()
    main()
