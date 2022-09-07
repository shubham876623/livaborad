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
from google.cloud import  bigquery
import os
from dateutil import parser
import schedule

def job():


    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ="ventura-cluster.json"
    client = bigquery.Client()
    table_id="ventura-cluster.PTF_competitors.galapagos_islands"
    client.delete_table(table_id, not_found_ok=True)
    schema = [
            bigquery.SchemaField("BotName", "STRING"),
            bigquery.SchemaField("StartDate", "DATETIME"),
            bigquery.SchemaField("EndDate", "DATETIME"),
            bigquery.SchemaField("Price", "FLOAT"),
            bigquery.SchemaField("Availability", "INTEGER"),
        ]
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)
    data_list=[]

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver=webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)
   # driver = webdriver.Chrome(executable_path=r"E:\Banno\chromedriver_win32 (2)\chromedriver.exe",chrome_options=chrome_options)

    driver.get('https://www.galapagosislands.com/ecommerce/search')
    time.sleep(3)
    soup=BeautifulSoup(driver.page_source,'html.parser')
    yesrs=soup.find('select',{'class':'select-without-rows ng-untouched ng-pristine ng-valid'}).find_all('option')
    # print(months)
    for y in yesrs :
        url1="https://www.galapagosislands.com/ecommerce/search/1/0/1/{}/0/0/0/0/0/0".format(y.text.strip())
        driver.get(url1)
        driver.maximize_window()
        time.sleep(3)
        soup1=BeautifulSoup(driver.page_source,'html.parser')
        
        # print(y,"ccccccccccccccccccccccccc")
        months=soup1.find_all('input',{'class':'month ng-untouched ng-pristine ng-valid ng-star-inserted'})
        for m in months:
            url="https://www.galapagosislands.com/ecommerce/search/1/0/{}/{}/0/0/0/0/0/0".format(int(m.get('id'))+1,y.text.strip())
            driver.get(url)
            
            time.sleep(5)
            print(url)
            actions = ActionChains(driver)
            for _ in range(4):
                actions.send_keys(Keys.SPACE).perform()  # moving slider
                time.sleep(2)
            for _ in range(4):
                actions.send_keys(Keys.ARROW_UP).perform()  # moving slider
                time.sleep(2)    
            time.sleep(30) 
            all_container_soup=BeautifulSoup(driver.page_source,'html.parser')
            all_containers=all_container_soup.find_all('div',{'class':'promo-container tableautomticheigh ng-star-inserted'})
            # print(len(all_containers),"lllllllllllll")
            for single_container in all_containers:
                botname=single_container.find('h4')
                all_departure_details_rows=single_container.find('tbody').find_all('tr')
                for single_row in all_departure_details_rows:
                    startDate=single_row.find_all('td')[0].text.strip().split('-')[0]+" "+y.text.strip()
                    end_date=single_row.find_all('td')[0].text.strip().split('-')[1]
                    if len(end_date)<3:
                        end_date=startDate.split(' ')[0]+" "+end_date+" "+y.text.strip()
                    else:
                        end_date=end_date+" "+y.text.strip()
                        
                    Price=single_row.find_all('td')[3]
                    Availbilty=single_row.find_all('td')[1]
                    if "left"  in Availbilty.text :
                        for digit in Availbilty.text :
                            if digit.isdigit() :
                                fiter_availblity=digit
                            elif "FULL"  in Availbilty.text :
                                
                                fiter_availblity="0"  
                            elif "available"  in Availbilty.text :
                                
                                fiter_availblity="999"  
                    
                    rows_to_insert = [
                                        {u'BotName':botname.text.strip(), u'StartDate':str(parser.parse(startDate)),u'EndDate':str(parser.parse(end_date)), u'Price':float(Price.text.strip().replace('US$','').replace(',','')), u'Availability':int(float(fiter_availblity.strip()))},
                                    ]

                    errors = client.insert_rows_json(table_id, rows_to_insert)
                    if errors == []:
                        print('New rows have been added.')
                    else:
                        print(f'Encountered errors while inserting rows: {errors}')
                    # print(single_row)
                    # print(startDate)
                    data_list.append(botname.text.strip()) 
                    data_list.append(startDate)
                    data_list.append(end_date) 
                    data_list.append(Price.text.strip().replace('US$','')) 
                    data_list.append(fiter_availblity.strip())
                    df=pd.DataFrame([data_list])
                    # df.to_csv("galapagosisoutput.csv",index=False,header=False , mode="a")
                    data_list.clear()
schedule.every(43200).seconds.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)                  
        # time.sleep(10)
            
        # print(url)
