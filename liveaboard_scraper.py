from os import close
from selenium import webdriver
from selenium.webdriver.chrome.options import  Options
from random import seed
from random import random
from time import process_time, sleep, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from datetime import timedelta
import urllib.request
from datetime import datetime


data_list=[]

# chrome_options = webdriver.ChromeOptions()
# prefs = {"profile.default_content_setting_values.notifications" : 2}
# chrome_options.add_experimental_option("prefs",prefs)
chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument('start-maximized')
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver=webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)
url_list=["https://www.liveaboard.com/search/galapagos","https://www.liveaboard.com/search/arctic","https://www.liveaboard.com/search/antarctica"]
for url in url_list:
    driver.get(url)
    time.sleep(4)
    driver.find_element_by_xpath("//button[@id='btn-header-currency-change']").click()
    driver.find_element_by_xpath("/html/body/div[1]/div[4]/div[4]/div[2]/ul/li[30]/a").click()
    time.sleep(3)
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/main/article/div/aside/div[1]/div/button[2]').click()
    time.sleep(1)
    soup1=BeautifulSoup(driver.page_source , "html.parser")
    try :
        pangination=soup1.find('div',{'class':'pagination'}).find('em').text.replace('Page ',' ').split('/')
    except:
        pangination=['0','0']
    all_moths_year=soup1.find_all('button',{'data-field':'#display-departure'})
    for one_month in all_moths_year :
        disabled_button=one_month.get('disabled')
        if disabled_button is None :
            # print(one_month.get('data-desc'))
            if one_month.get('data-desc') is not None:
                main_url="{}/".format(url)+one_month.get('data-desc')
                # driver.get("{}/".format(url)+one_month.get('data-desc'))
            # print(pangination)
                driver.get(main_url)
                for i in range(int(pangination[0]),int(pangination[1])+1):
                    time.sleep(7)
                    soup=BeautifulSoup(driver.page_source , "html.parser")
                    all_section=soup.find('div',{'id':'divresults'}).find_all('section')
                    # print(len(all_section), "aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                    # time.sleep(100)
                    for one_section in all_section:
                        try:
                            
                            Bot_name=one_section.find('h3',{'class':'card-title'})
                            
                            all_departure=one_section.find('div',{'class':'card-departures'}).find_all('li')
                            if all_departure is not None:
                                for single_departure in all_departure:
                                    Departure_Date=single_departure.find('span',{'class':'display-date'})
                                    Day_nights=single_departure.find('span',{'class':'display-nights'})
                                    day=Day_nights.text.split('/')[1].replace('N','')
                                    # print(day)
                                    # print(type(day))
                                    enddate= datetime.strptime(Departure_Date.text, '%d %b %Y')+timedelta(days=int(day.strip()))
                                    Price=single_departure.find('span',{'class':'display-price'}).find('strong')
                                    Availbilty=single_departure.find('span',{'class':'display-status'})
                                    if "left"  in Availbilty.text :
                                        for digit in Availbilty.text :
                                            if digit.isdigit() :
                                                fiter_availblity=digit
                                    elif "FULL"  in Availbilty.text :
                                        
                                        fiter_availblity="0"  
                                    elif "available"  in Availbilty.text :
                                        
                                        fiter_availblity="999"            
                                                
                                                
                                                
                                    # if Departure_Date is not None:
                                    data_list.append(Bot_name.text) 
                                    data_list.append(Departure_Date.text)
                                    data_list.append(enddate.strftime("%d %B %Y")) 
                                    data_list.append(Price.text) 
                                    data_list.append(fiter_availblity)
                                    df=pd.DataFrame([data_list])
                                    df.to_csv("test.csv",index=False,header=False , mode="a")
                                    data_list.clear()
                        except:
                            pass
                try:
                    next_page_button_element=driver.find_element_by_xpath('//*[@id="divresults"]/div[3]/a')
                    if  "Next"  in next_page_button_element.text:
                        next_page_button_element.click()
                except:
                    pass
        
time.sleep(100)