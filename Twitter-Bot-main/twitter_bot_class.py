from selenium import webdriver
from selenium import common
from selenium.webdriver.common.by import By
from selenium.webdriver.common import keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
from PIL import Image
from time import sleep

driver = webdriver.Firefox()

class Twitter_Bot:

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.bot = driver
        self.bot.maximize_window()
        self.is_logged_in = False

    #Login Function 
    def login(self):
        bot = self.bot
        bot.get('https://twitter.com/login/')
        
        email_field = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.NAME,"text")))
        email_field.clear()
        email_field.send_keys(self.email)
        email_field.send_keys(keys.Keys().ENTER)

        password_field = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.NAME, 'password')))
        password_field.clear()
        password_field.send_keys(self.password)
        password_field.send_keys(keys.Keys().ENTER)

        self.is_logged_in = True

    #Function to post tweets
    def post_tweets(self,tweetBody, image_path):
        if not self.is_logged_in:
            raise Exception("You must log in first!")

        bot = self.bot  

        WebDriverWait(driver, 60).until(EC.visibility_of_element_located(
                (By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']")
        )).click()

        sleep(2)

        WebDriverWait(driver, 60).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@role='textbox']")
        )).send_keys(tweetBody)

        sleep(2)

        WebDriverWait(driver, 60).until(EC.presence_of_element_located(
                (By.XPATH, "//input[@accept]")
        )).send_keys(image_path)

        sleep(3)

        WebDriverWait(driver, 60).until(EC.visibility_of_element_located(
            (By.XPATH, "//div[@data-testid='tweetButton']")
        )).send_keys(keys.Keys.ENTER)
