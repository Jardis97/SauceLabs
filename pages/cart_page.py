from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from selenium.webdriver.support.ui import WebDriverWait


class CartPage:
    URL = "https://www.saucedemo.com/cart.html"
    product_in_cart_name = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    checkout_button = (By.ID, "checkout")


    def __init__(self, driver): #locator come attributi classe
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) #per non dover scrivere sempre webdriverwait e poter controllare timeout facilmente

    def open(self):
        self.driver.get(self.URL)

    def is_on_cart_page(self):
        return self.driver.current_url == self.URL

    def is_product_in_cart(self, product_name):
        try:
            self.wait.until(EC.presence_of_element_located(self.product_in_cart_name)) #wait che almeno un elemento sia presente
            products = self.driver.find_elements(*self.product_in_cart_name)
            product_names = [p.text for p in products] #creo lista di nomi dei prodotti nel carrello
            return product_name in product_names #verifico che il nome del prodotto sia presente nella lista
        except Exception as e:
            logging.error(f"Errore durante la verifica del prodotto nel carrello: {e}")
            return False


    def click_checkout_button(self):
        try:
            self.wait.until(EC.element_to_be_clickable(self.checkout_button)).click()  # Attende che il pulsante di checkout sia cliccabile
        except Exception as e:
            logging.error(f"Errore durante il click sul pulsante di checkout: {e}")
            return False






