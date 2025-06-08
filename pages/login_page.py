from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    URL = "https://www.saucedemo.com/"
    username_field = (By.ID, "user-name")
    password_field = (By.ID, "password")
    login_button = (By.ID, "login-button")
    error_message = (By.CSS_SELECTOR, 'h3[data-test="error"]')

    def __init__(self, driver): #locator come attributi classe
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) #per non dover scrivere sempre webdriverwait e poter controllare timeout facilmente

    def open(self):
        self.driver.get(self.URL)


    def is_username_field_present(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.username_field)).is_displayed()
            print("Campo username visibile")
        except TimeoutException:
            logging.error("Il campo username non è visibile entro il timeout.") #logging per fare report nei log segnalando errore
            return False
        except NoSuchElementException:
            logging.error("Il campo username non è stato trovato.")
            return False

    def enter_username(self, username):
        self.wait.until(EC.visibility_of_element_located(self.username_field)).send_keys(username)

    def enter_password(self, password):
        self.wait.until(EC.visibility_of_element_located(self.password_field)).send_keys(password)

    def click_login(self):
        self.wait.until(EC.element_to_be_clickable(self.login_button)).click()

    def get_error_message(self):
        return self.wait.until(EC.visibility_of_element_located(self.error_message)).text