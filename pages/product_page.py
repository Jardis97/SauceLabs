from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from selenium.webdriver.support.ui import WebDriverWait


class ProductPage:
    URL = "https://www.saucedemo.com/inventory.html"
    login_button = (By.ID, "login-button")
    error_message = (By.CSS_SELECTOR, 'h3[data-test="error"]')
    add_to_cart = (By.ID, "add-to-cart-sauce-labs-backpack")
    cart_button = (By.ID, "shopping_cart_container")
    cart_count = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]') #piu' robusto di class_name

    def __init__(self, driver): #locator come attributi classe
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) #per non dover scrivere sempre webdriverwait e poter controllare timeout facilmente

    def open(self):
        self.driver.get(self.URL)

    def is_on_products_page(self):
        return self.driver.current_url == self.URL

    def get_add_to_cart_locator(self, product_name): #costruisco dinamicamente il locator
        product_slug = product_name.lower().replace(" ", "-")
        return (By.ID, f"add-to-cart-{product_slug}")

    def add_to_cart_by_product_name(self, product_name): #uso locator creato prima per cliccare prodotto
        locator = self.get_add_to_cart_locator(product_name)
        self.driver.find_element(*locator).click()

    def get_cart_badge_count(self):
        try:
            badge = self.wait.until(
                EC.visibility_of_element_located(self.cart_count)
            )
            self.cart_badge_value = badge.text #salva numero che comprare sul cartello
            #return badge.text
        except TimeoutException:
            return None

    def click_cart_button(self):
            try:
                self.wait.until(EC.element_to_be_clickable(self.cart_button)).click()
            except TimeoutException:
                logging.error("Il pulsante del carrello non è cliccabile entro il timeout.")
                return False
            return True


    def is_cart_empty(self):
        try:
            badge = self.driver.find_element(*self.cart_count)
            return badge.text == "" or badge.text == "0"
        except NoSuchElementException:
            return True  # Il badge non è presente


