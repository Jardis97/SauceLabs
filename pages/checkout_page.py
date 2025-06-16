from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from selenium.webdriver.support.ui import WebDriverWait
import time


class CheckoutPage: #locator come attributi classe
    URL = "https://www.saucedemo.com/checkout-step-one.html"
    URL2= "https://www.saucedemo.com/checkout-step-two.html"
    first_name_field = (By.ID, "first-name")
    last_name_field = (By.ID, "last-name")
    postal_code_field = (By.ID, "postal-code")
    continue_button = (By.ID, "continue")
    finish_button = (By.ID, "finish")
    URL_checkout_complete = "https://www.saucedemo.com/checkout-complete.html"
    back_button = (By.ID, "back-to-products")


    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) #per non dover scrivere sempre webdriverwait e poter controllare timeout facilmente

    def open(self):
        self.driver.get(self.URL)

    def is_on_checkout_page(self):
        return self.driver.current_url == self.URL


    def compile_checkout(self, first_name, last_name, postal_code):
        try:
            self.wait.until(EC.visibility_of_element_located(self.first_name_field)).send_keys(first_name)
            self.wait.until(EC.visibility_of_element_located(self.last_name_field)).send_keys(last_name)
            self.wait.until(EC.visibility_of_element_located(self.postal_code_field)).send_keys(postal_code)
            self.wait.until(EC.element_to_be_clickable(self.continue_button)).click()
        except Exception as e:
            logging.error(f"Errore durante la compilazione del checkout: {e}")
            return False

    def is_on_checkout_step_two(self):
        return self.driver.current_url == self.URL2

    def finish_checkout(self):
        try:
            self.wait.until(EC.element_to_be_clickable(self.finish_button)).click()
            print("Finalizzazione checkout completata con successo.")
        except TimeoutException:
            logging.error("Il pulsante di completamento non è cliccabile entro il timeout.")
            return False

    def is_checkout_complete(self):
        return self.driver.current_url == self.URL_checkout_complete


    def back_toProducts(self):
        try:
            self.wait.until(EC.element_to_be_clickable(self.back_button)).click()
            print("Ritorno alla pagina prodotti.")
        except TimeoutException:
            logging.error("Il pulsante di ritorno non è cliccabile entro il timeout.")
            return False





