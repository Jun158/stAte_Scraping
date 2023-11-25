import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from get_chrome_driver import GetChromeDriver
from linebot import LineBotApi
from linebot.models import TextSendMessage

class AStateAccountChecker:
    def __init__(self):
        self.browser = self.driver_init()
        self.wait = WebDriverWait(self.browser, 10)
        self.CHANNEL_ACCESS_TOKEN = os.getenv('token')
        self.USER_ID = os.getenv('id')

    @staticmethod
    def driver_init():
        get_driver = GetChromeDriver()
        get_driver.install()
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        return webdriver.Chrome(options=options)

    def login(self):
        self.browser.get('https://www.astate.edu/')
        # Wait for the login button and click
        login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="resource-nav"]/div/ul/li[6]/a')))
        login_button.click()

        # Enter username and password
        username = os.getenv('aStateName')
        password = os.getenv('aStatePw')
        self.wait.until(EC.presence_of_element_located((By.ID, 'input-username'))).send_keys(username)
        self.wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
        self.browser.find_element(By.ID, 'loginForm').find_element(By.TAG_NAME, 'button').click()

    def navigate_to_transaction_report(self):
        # Navigate to the Account Transaction Report page
        transaction_report_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main-link-container"]/div[5]/div/a')))
        transaction_report_link.click()

    def specify_date(self):
        # Specify date for transaction report
        date_input = self.wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_BeginRadDateTimePicker_dateInput')))
        date_input.clear()
        date_input.send_keys('8/23/2021 12:00 AM')
        continue_button = self.browser.find_element(By.ID, 'MainContent_ContinueButton')
        continue_button.click()

    def scrape_data(self):
        # Scrape A-State flex amount and assign it as MESSAGE
        transactions = []
        # Continue scraping data...
        # You will need to adjust this method to scrape the transaction data as required.
        return transactions

    def calculate_balance(self, transactions):
        # Calculate the balance based on the transactions
        balance = sum(transactions)
        # Continue calculating balance...
        # You will need to fill this in with the logic from your original code.
        return ('BeginDate', 'TodayDate', 'SpendAmount', 'BalanceAmount', 'DeltaDays', 'Weeks', 'DaysRemaining')

    def format_message(self, begin, today, spend, balance, delta, wks, wRem):
        MESSAGE = "From: {0}\nTo: {1}\n({5} weeks, {6} days) \n\nSpend: {2}\nBalance: {3}\nPer Day: {4}day"
        return MESSAGE.format(begin, today, spend, balance, delta, wks, wRem)

    def push_to_line(self, message):
        line_bot_api = LineBotApi(self.CHANNEL_ACCESS_TOKEN)
        line_bot_api.push_message(self.USER_ID, messages=TextSendMessage(text=message))

    def run(self):
        try:
            self.login()
            self.navigate_to_transaction_report()
            self.specify_date()
            transactions = self.scrape_data()
            begin, today, spend, balance, delta, wks, wRem = self.calculate_balance(transactions)
            message = self.format_message(begin, today, spend, balance, delta, wks, wRem)
            self.push_to_line(message)
        finally:
            self.browser.quit()

if __name__ == '__main__':
    checker = AStateAccountChecker()
    checker.run()
