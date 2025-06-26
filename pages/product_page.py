from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import \
    element_to_be_clickable
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from pages.cart_page import CartPage


class ProductPage(BasePage): #locator come attributi classe
    URL = "https://www.saucedemo.com/inventory.html"
    login_button = (By.ID, "login-button")
    error_message = (By.CSS_SELECTOR, 'h3[data-test="error"]')
    INVENTORY_CONTAINER = (By.CLASS_NAME, "inventory_container")
    add_to_cart = (By.ID, "add-to-cart-sauce-labs-backpack")
    cart_button = (By.ID, "shopping_cart_container")
    cart_count = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]') #piu' robusto di class_name

    def __init__(self, driver):
        super().__init__(driver)

    def open(self):
        self.driver.get(self.URL)

    #per verificare che utente sia sulla pagina dei prodotti
    #La logica di attesa è incapsulata nel metodo helper "_is_visible_" della BasePage.
    def is_loaded(self):
         return self._is_visible(self.INVENTORY_CONTAINER)

    def is_on_products_page(self):
        return self.driver.current_url == self.URL

    def get_add_to_cart_locator(self, product_name): #costruisco dinamicamente il locator, sauce labs usa lo stesso pattern per i vari id dei prodotti
        product_slug = product_name.lower().replace(" ", "-")
        return (By.ID, f"add-to-cart-{product_slug}")

    def add_to_cart_by_product_name(self, product_name): #uso locator creato prima per cliccare prodotto
        locator = self.get_add_to_cart_locator(product_name)
        self._click(locator)  #usiamo metodo _click definito in BasePage

    def get_cart_badge_count(self):
        return self._get_text(self.cart_count)

    def click_cart_button(self) -> CartPage:
        self._click(self.cart_button)
        return CartPage(self.driver)

    def is_cart_empty(self):
        #riutilizzo get_cart_badge_count
        return self.get_cart_badge_count() is None
            # try:
            #     badge = self.wait.until(*self.cart_count)
            #     return badge.text == "" or badge.text == "0"
            # except NoSuchElementException:
            #     return True  # Il badge non è presente


