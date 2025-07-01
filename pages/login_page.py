import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class LoginPage(BasePage): #locator come attributi classe perché non cambiano
    #URL = "https://www.saucedemo.com/" --> ora è nel file .env
    username_field = (By.ID, "user-name")
    password_field = (By.ID, "password")
    login_button = (By.ID, "login-button")
    _error_message_locator = (By.CSS_SELECTOR, 'h3[data-test="error"]')

    def __init__(self, driver):
        # 3. Chiama il costruttore della classe genitore (BasePage)
        # Questo inizializza self.driver e self.wait automaticamente!
        super().__init__(driver)


    def open(self, base_url: str):
        self.driver.get(f"{base_url}")
        return self


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

    def get_error_message(self) -> str:
        """
        Cerca il messaggio di errore e ne restituisce il testo.
        Restituisce None se l'elemento non viene trovato entro il timeout,
        evitando di far crashare il test.
        """
        try:
            # Attende che l'elemento sia visibile e ne restituisce il testo
            error_element = self.wait.until(EC.visibility_of_element_located(self._error_message_locator))
            return error_element.text
        except TimeoutException:
            # Se l'elemento non appare, logga un avviso e restituisce None.
            # Questo permette al test di gestire il caso in cui l'errore non appare.
            logging.warning("Elemento del messaggio di errore non trovato sulla pagina.")
            return None