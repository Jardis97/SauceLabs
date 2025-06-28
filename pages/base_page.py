import logging

from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """
    Classe base per tutte le Page Objects.
    Contiene la logica comune e l'inizializzazione del driver e del WebDriverWait.
    """
    def __init__(self, driver):
        """
        Il costruttore inizializza il driver e il WebDriverWait.
        Questo verrà ereditato da tutte le altre pagine.
        """
        self.driver = driver
        # Inizializzi WebDriverWait una sola volta qui!
        self.wait = WebDriverWait(driver, 10)
        self.log = logging

    # metodi comuni per evitar duplicazioni
    def _find_element(self, locator):
        """Trova un elemento attendendo che sia presente."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def _find(self, locator: tuple, timeout: int = None):
        """
        Trova un elemento, usando un timeout personalizzato se fornito.
        Se non fornito, usa il wait di default della classe.
        """
        # Se non passo un timeout, usa quello di default (10s)
        wait_instance = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            return wait_instance.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            # Rilancia l'eccezione per essere gestita dal chiamante
            raise


    def _get_current_url(self):
        """Restituisce l'URL corrente del browser."""
        return self.driver.current_url

    def _fill(self, locator: tuple, text: str) -> None:
        """
        Trova un elemento, lo pulisce e inserisce il testo.
        """
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            element.clear()
            element.send_keys(text)
        except TimeoutException:
            self.log.error(f"Timeout: l'elemento {locator} non è visibile per essere compilato.")
            # Rilancia l'eccezione per far fallire il test.
            raise

    def _click(self, locator: tuple) -> None:
        """
        Trova un elemento in modo robusto e ci clicca sopra.
        """
        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        except TimeoutException:
            self.log.error(f"Timeout: l'elemento {locator} non è cliccabile.")
            # Rilancia l'eccezione per far fallire il test.
            raise


    def _is_visible(self, locator: tuple, timeout: int = 5) -> bool:
        """
               Verifica se un elemento è visibile entro un timeout, restituendo True/False.
               Questo è un metodo di VERIFICA, quindi non solleva eccezioni ma risponde a una domanda.
               """
        try:
            # Usiamo un wait specifico per questa verifica per permettere timeout personalizzati
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            self.log.info(f"Elemento {locator} non è diventato visibile entro {timeout} secondi.")
            return False

    def _get_text(self, locator: tuple) -> str:
        try:
            # Usa SEMPRE self.wait, che ha il timeout fisso.
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return element.text
        except TimeoutException:
            self.log.info(f"Timeout: Elemento {locator} non visibile per recuperare il testo.")
            return None