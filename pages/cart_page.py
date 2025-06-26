from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from pages.checkout_page import CheckoutStepOnePage


class CartPage(BasePage): #locator come attributi classe
    URL = "https://www.saucedemo.com/cart.html"
    product_in_cart_name = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    checkout_button = (By.ID, "checkout")


    def __init__(self, driver):
        # 3. Chiama il costruttore della classe genitore (BasePage)
        # Questo inizializza self.driver e self.wait automaticamente!
        super().__init__(driver)

    def open(self):
        self.driver.get(self.URL)

    def is_on_cart_page(self):
        # uso metodi classe BasePage
        return self._get_current_url() == self.URL
        #return self.driver.current_url == self.URL

    def is_product_in_cart(self, product_name):
        try:
            self.wait.until(EC.presence_of_element_located(self.product_in_cart_name)) #wait che almeno un elemento sia presente
            products = self.driver.find_elements(*self.product_in_cart_name)
            product_names = [p.text for p in products] #creo lista di nomi dei prodotti nel carrello
            return product_name in product_names #verifico che il nome del prodotto sia presente nella lista
        except Exception as e:
            self.log.info(f"Errore durante la verifica del prodotto nel carrello: {e}")
            return False


    def click_checkout_button(self) -> CheckoutStepOnePage: #uso hint per dirgli cosa restituisce
        self._click(self.checkout_button)
        return CheckoutStepOnePage(self.driver)





