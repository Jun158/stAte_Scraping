import os
from get_chrome_driver import GetChromeDriver
from selenium import webdriver
from time import sleep
from linebot import LineBotApi 
from linebot.models import TextSendMessage


# Visit the A-State website 
get_driver = GetChromeDriver()
get_driver.install()

def driver_init():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    return webdriver.Chrome(options=options)

browser = driver_init()
browser.get('https://www.astate.edu/')
browser.find_element('xpath','//*[@id="resource-nav"]/div/ul/li[6]/a').click()


# Enter username and pw
username = os.environ['aStateName']
pw = os.environ['aStatePw']
browser.find_element("xpath", '//*[@id="input-username"]').send_keys(username)
browser.find_element("xpath", '//*[@id="password"]').send_keys(pw)
browser.find_element("xpath", '//*[@id="loginForm"]/button').click()


# Visit Account Transaction Report page
browser.implicitly_wait(20)                                                        
browser.find_element("xpath", '//*[@id="main-link-container"]/div[5]/div/a').click()


# Specify date      
browser.implicitly_wait(20)
browser.find_element("id", 'ctl00_MainContent_BeginRadDateTimePicker_dateInput').clear()
browser.find_element("id", 'ctl00_MainContent_BeginRadDateTimePicker_dateInput').send_keys('8/23/2021 12:00 AM')
browser.find_element("xpath", '//*[@id="MainContent_ContinueButton"]').click()

browser.implicitly_wait(5)


# Scrape A-State flex amount and assign it as MESSAGE
Date = []
Loc = []
Type = []
Amo = []

date_format = "%m/%d/%Y"

jude = True
s = 1 #page number
while jude == True:
    if s <= 11:
        browser.find_element("xpath", f'//*[@id="ctl00_MainContent_ResultRadGrid_ctl00"]/tfoot/tr/td/table/tbody/tr/td/div[1]/a[{s}]').click()
        #print('fdsa')
    else:
        s = 10
        browser.find_element("xpath", f'//*[@id="ctl00_MainContent_ResultRadGrid_ctl00"]/tfoot/tr/td/table/tbody/tr/td/div[1]/a[{s}]').click()
    sleep(5)

    x = 0 #Number of element/page (Max: 14)
    while x <= 14:
        date = browser.find_element("xpath", f'//*[@id="ctl00_MainContent_ResultRadGrid_ctl00__{x}"]/td[1]').text
        loca = browser.find_element("xpath", f'//*[@id="ctl00_MainContent_ResultRadGrid_ctl00__{x}"]/td[4]').text
        ttype = browser.find_element("xpath", f'//*[@id="ctl00_MainContent_ResultRadGrid_ctl00__{x}"]/td[5]').text #credit or debit
        amnt = browser.find_element("xpath", f'//*[@id="ctl00_MainContent_ResultRadGrid_ctl00__{x}"]/td[6]').text

        #print(amnt)

        Date.append(date)
        Loc.append(loca)
        Type.append(ttype)

        if ttype == 'Credit':
            New_amnt = float(amnt.replace(' USD', '',).replace(',', ''))
            x = 14
            jude = False
        else:
            New_amnt = float(amnt.replace('(', '').replace(') USD', ''))

        Amo.append(New_amnt)

        x += 1 #Number of element/page (Max: 14)

    s += 1

#Output field
balance = sum(Amo)
spend = round(balance-900-1.06,2)
balance = 900-spend

from datetime import date
#begin date
begin = Date[-1][:-8]
#today's date
today = date.today()
today = datetime.strptime(str(today), "%Y-%m-%d").strftime("%m/%d/%Y")

#Convert Begin
DTbegin = begin
if DTbegin[5] == '/':
    date = DTbegin[0:10]
elif DTbegin[4] == '/':
    date = DTbegin[0:9]
elif DTbegin[3] == '/':
    date = DTbegin[0:8]
DTbegin = datetime.strptime(date, date_format)

#Convert Today
DTtoday = today
if DTtoday[5] == '/':
    date = DTtoday[0:10]
elif DTtoday[4] == '/':
    date = DTtoday[0:9]
elif DTtoday[3] == '/':
    date = DTtoday[0:8]
DTtoday = datetime.strptime(date, date_format)

#delta date
delta = (DTtoday-DTbegin)
delta = str(delta).replace(" days, 0:00:00","")

wks = int(delta)//7
wRem = int(delta)-wks*7

MESSAGE = "From: {0}\nTo: {1}\n({5} weeks, {6} days) \n\nSpend: {2}\nBalance: {3}\nPer Day: {4}day"
out_put = MESSAGE.format(begin,today,spend,balance,delta,wks,wRem)
    
    
browser.quit() 


# push to LINE
CHANNEL_ACCESS_TOKEN = os.environ['token']
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

USER_ID = os.environ['id']
message = TextSendMessage(out_put)
line_bot_api.push_message(USER_ID, messages=message)
