# C:/Users/user/Downloads/Corso Automation/PythonProject/SauceLabs/pages/checkout_page.py

# 1. Import di Terze Parti (solo quelli necessari!)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC # <-- L'import che mancava!

# 2. Import Locali
from pages.base_page import BasePage

# --- Pagina 1: Il Form di Checkout ---

class CheckoutStepOnePage(BasePage):
    """Rappresenta la pagina di checkout 'Step One', dove l'utente inserisce i dati."""
    _URL = "https://www.saucedemo.com/checkout-step-one.html"
    _FIRST_NAME_FIELD = (By.ID, "first-name")
    _LAST_NAME_FIELD = (By.ID, "last-name")
    _POSTAL_CODE_FIELD = (By.ID, "postal-code")
    _CONTINUE_BUTTON = (By.ID, "continue")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def is_on_checkout_page(self) -> bool:
        """Verifica se il browser si trova sulla pagina di checkout (Step 1)."""
        return self.driver.current_url == self._URL

    def fill_checkout_form(self, first_name: str, last_name: str, postal_code: str):
        """Compila i campi del form di checkout usando i metodi robusti di BasePage."""
        self._fill(self._FIRST_NAME_FIELD, first_name)
        self._fill(self._LAST_NAME_FIELD, last_name)
        self._fill(self._POSTAL_CODE_FIELD, postal_code)

    def click_continue_button(self) -> 'CheckoutStepTwoPage':
        """Clicca sul pulsante 'Continue' e naviga alla pagina successiva."""
        self._click(self._CONTINUE_BUTTON)
        return CheckoutStepTwoPage(self.driver)


# --- Pagina 2 (Overview): Il Riepilogo Ordine ---

class CheckoutStepTwoPage(BasePage):
    """Rappresenta la pagina di checkout 'Step Two', con il riepilogo dell'ordine."""
    _URL = "https://www.saucedemo.com/checkout-step-two.html"
    _FINISH_BUTTON = (By.ID, "finish")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def is_on_checkout_step_two(self) -> bool:
        """Verifica se il browser si trova sulla pagina di riepilogo (Step 2)."""
        return self.driver.current_url == self._URL

    def click_finish_button(self) -> 'CheckoutCompletePage':
        """Clicca sul pulsante 'Finish' per completare l'ordine."""
        self._click(self._FINISH_BUTTON)
        return CheckoutCompletePage(self.driver)


# --- Pagina 3  (Complete): Ordine Completato ---

class CheckoutCompletePage(BasePage):
    """Rappresenta la pagina finale 'Checkout Complete'."""
    _URL = "https://www.saucedemo.com/checkout-complete.html"
    _BACK_HOME_BUTTON = (By.ID, "back-to-products")
    _CONFIRMATION_HEADER = (By.CLASS_NAME, "complete-header")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def is_checkout_complete(self) -> bool:
        """Verifica se il browser si trova sulla pagina di conferma ordine."""
        return self.driver.current_url == self._URL

    def get_confirmation_message(self) -> str:
        """Restituisce il messaggio di conferma dell'ordine."""
        return self._get_text(self._CONFIRMATION_HEADER) # Usa il metodo di BasePage

    def click_back_home_button(self):
        """Clicca sul pulsante per tornare alla pagina dei prodotti."""
        self._click(self._BACK_HOME_BUTTON)
        # Se necessario, potresti restituire un'istanza di ProductPage
        # from pages.product_page import ProductPage
        # return ProductPage(self.driver)