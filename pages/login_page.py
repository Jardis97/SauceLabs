import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class LoginPage(BasePage): #locator come attributi classe perché non cambiano
    URL = "https://www.saucedemo.com/"
    username_field = (By.ID, "user-name")
    password_field = (By.ID, "password")
    login_button = (By.ID, "login-button")
    error_message = (By.CSS_SELECTOR, 'h3[data-test="error"]')

    def __init__(self, driver):
        # 3. Chiama il costruttore della classe genitore (BasePage)
        # Questo inizializza self.driver e self.wait automaticamente!
        super().__init__(driver)


    def open(self):
        self.driver.get(self.URL)


    def is_username_field_present(self):
        try:
            self.wait.until(EC.visibility_of_element_located(self.username_field)).is_displayed()
            return True
        except TimeoutException:
            logging.error("Il campo username non è visibile entro il timeout.") #logging per fare report nei log segnalando errore
            return False

#Per inserire i dati del login
    def login(self, username: str, password: str):
        self._fill(self.username_field, username)
        self._fill(self.password_field, password)
        self._click(self.login_button)


    def click_login(self):
        self.wait.until(EC.element_to_be_clickable(self.login_button)).click()

    def get_error_message(self):
        return self.wait.until(EC.visibility_of_element_located(self.error_message)).text