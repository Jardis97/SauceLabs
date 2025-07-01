
# 1. FORWARD REFERENCES E TYPE_CHECKING
from __future__ import annotations

import csv
import logging
import os  # libreria per leggere variabili d'ambiente, per Jenkins
from typing import Generator
from typing import TYPE_CHECKING
from typing import Tuple  # lo uso per gli hint

import allure
import pytest
from dotenv import load_dotenv  # aggiungo per far leggere i dati dal file .env
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
# chrome driver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

# 2
#    blocco visibile solo agli analizzatori di tipo (PyCharm, MyPy)
#    e previene qualsiasi errore di importazione circolare a runtime.
if TYPE_CHECKING:
    from pages.cart_page import CartPage
    from pages.checkout_page import (
        CheckoutCompletePage,
        CheckoutStepOnePage,
        CheckoutStepTwoPage,
    )
    from pages.login_page import LoginPage
    from pages.product_page import ProductPage



#non usare perché troppo lunga oi dipendenze
@pytest.fixture  #per non dover ricreare manualmente l'istanza dentro il test "product_page = ProductPage(browserInstance)"
def product_page(browserInstance) -> "ProductPage":
    from pages.product_page import ProductPage
    return ProductPage(browserInstance)

@pytest.fixture
def login_page(browserInstance) -> "LoginPage":
    from pages.login_page import LoginPage
    return LoginPage(browserInstance)

@pytest.fixture
def cart_page(browserInstance) -> "CartPage":
    from pages.cart_page import CartPage
    return CartPage(browserInstance)


#Def per fare screenshot in qualsiasi test
def allure_screenshot(driver, name):
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG
    )
#fine screenshoot

#Hook per fare screenshot allure ad ogni fallimento del test
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook di Pytest che viene eseguito dopo ogni fase di un test (setup, call, teardown).
    Viene usato per catturare lo screenshot in caso di fallimento.
    """
    # Esegui tutti gli altri hook per ottenere un oggetto "report"
    outcome = yield
    report = outcome.get_result()

    # Ci interessa solo il fallimento nella fase di "call" (l'esecuzione del test vero e proprio)
    if report.when == "call" and report.failed:
        logging.error(f"Test fallito: {item.name}. Catturo lo screenshot.")

        # Cerca la fixture 'browserInstance' tra quelle usate dal test fallito.
        # Questo è il modo "magico" per accedere a una fixture dall'interno di un hook.
        if "browserInstance" in item.fixturenames:
            driver = item.funcargs["browserInstance"]

            # Allega lo screenshot al report di Allure
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"screenshot_failure_{item.name}",
                attachment_type=allure.attachment_type.PNG,
            )

            # Allega il sorgente della pagina (HTML)
            allure.attach(
                driver.page_source,
                name=f"pagesource_failure_{item.name}",
                attachment_type=allure.attachment_type.HTML,
            )

# Per risolvere problema, devi dire a `pytest` di accettare l'opzione `--browser_name` come argomento tramite l'uso di una funzione chiamata `pytest_addoption`.
def pytest_addoption(parser):
    # Aggiungiamo l'opzione per scegliere l'ambiente
    parser.addoption(
        "--env", action="store", default="sit", help="Ambiente da testare (es: sit, uat)"
    )
    # per lanciare docker in remote
    parser.addoption("--browser", action="store", default="chrome", help="Browser: chrome, firefox, o remote per docker/selenium grid")
    parser.addoption(
        "--resolution",
        action="store",
        default="1280,800",
        help="dimensione finestra browser (es: 1280,800 o 375,812)"
    )
#pytest tests/ --browser_name=firefox/edge ecc

    parser.addoption(
        "--all-usernames", action="store_true", default=False, help="Esegui test con tutti gli username"
    )

#------------FIXTURE PER CARICARE L'AMBIENTE (autouse=True la esegue automaticamente)
@pytest.fixture(scope="session", autouse=True)
def load_env(request):
    """
    Carica le variabili d'ambiente dal file .env corretto prima dell'inizio dei test.
    """
    env = request.config.getoption("--env")
    env_file = os.path.join(os.path.dirname(__file__), '..', f'.env.{env}') # Cerca il file nella root del progetto
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file, override=True)
        logging.info(f"Caricato file di configurazione per l'ambiente: {env_file}")
    else:
        pytest.fail(f"File di configurazione '{env_file}' non trovato. Assicurati che esista.")


# 3. CREA FIXTURE PER FORNIRE I DATI AI TEST
#    Queste fixture leggono i valori caricati e li passano ai test.
#    Questo disaccoppia i test dalla conoscenza di 'os.environ'.

@pytest.fixture(scope="session")
def base_url() -> str:
    """Restituisce l'URL base per l'ambiente selezionato."""
    url = os.environ.get("BASE_URL")
    if not url:
        pytest.fail("La variabile BASE_URL non è definita nel file .env")
    return url

@pytest.fixture(scope="session")
def standard_user_credentials() -> Tuple[str, str]:
    """Restituisce le credenziali (username, password) per l'utente standard."""
    username = os.environ.get("STANDARD_USER_USERNAME")
    password = os.environ.get("STANDARD_USER_PASSWORD")
    if not username or not password:
        pytest.fail("Le credenziali per l'utente standard non sono definite nel file .env")
    return username, password

@pytest.fixture(scope="session")
def locked_user_credentials() -> Tuple[str, str]:
    """Restituisce le credenziali (username, password) per l'utente standard."""
    username = os.environ.get("LOCKED_USER_USERNAME")
    password = os.environ.get("LOCKED_USER_PASSWORD")
    if not username or not password:
        pytest.fail("Le credenziali per l'utente LOCKED non sono definite nel file .env")
    return username, password

#-----FINE fitxute per caricare variabili da file .env



#FIXTURE PER caricare multipli dati da un file .csv
def load_user_data_from_csv():
    """Legge i dati degli utenti dal file CSV e li restituisce come lista di tuple.
    Ignora le righe vuote e giestisce le righe con numero errato di colonne"""

    user_data = []
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_users.csv')

    with open(csv_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Leggi l'intestazione
        expected_columns = len(header)

        for i, row in enumerate(reader, start=2):  # start=2 per contare la riga header
            # 1. Ignora le righe completamente vuote
            if not row:
                continue

            # 2. Controlla che il numero di colonne sia corretto
            if len(row) != expected_columns:
                print(
                    f"\nATTENZIONE: La riga {i} nel file CSV ha {len(row)} colonne, "
                    f"ma ne erano attese {expected_columns}. La riga verrà saltata."
                    f"\nDati della riga: {row}"
                )
                continue

            user_data.append(tuple(row))

    return user_data

@pytest.fixture(scope="function") #scope="function" si distrugge ad ogni test, module/session no
def browserInstance(request: pytest.FixtureRequest) -> Generator[WebDriver, None, None]: #restituisce yield, generator indica quello
    """
    Crea, configura e distrugge l'istanza del browser per ogni test.
    Supporta tre modalità:
    1. remote: Si connette a un Selenium Grid (in Docker).
    2. cloud (Sauce Labs): Si connette a Sauce Labs se rileva un'esecuzione parallela.
    3. local: Esegue Chrome o Firefox sulla macchina locale.
    """
    # Usa la nuova opzione unificata
    browser_name = request.config.getoption("--browser")
    resolution = os.environ.get("RESOLUTION") or request.config.getoption("resolution")
    width, height = map(int, resolution.split(","))

    # Controlla se siamo in un'esecuzione parallela su Sauce Labs
    is_sauce_run = (
        "PYTEST_XDIST_WORKER" in os.environ
        and os.environ.get("SAUCE_USERNAME")
        and os.environ.get("SAUCE_ACCESS_KEY")
    )

    driver: WebDriver #webdriver per docker/seleniumgrid, sauce labs o locale

    if browser_name == "remote":
        # --- 1. ESECUZIONE REMOTA (DOCKER) ---
        logging.info("Modalità remota: connessione a Selenium Grid (Docker)...")
        # 'chrome' è il nome del servizio nel file docker-compose.yml
        # Docker lo risolverà con l'IP corretto del container.
        selenium_hub_url = "http://chrome:4444/wd/hub"
        options = ChromeOptions() # Per ora supportiamo solo Chrome in remote
        driver = webdriver.Remote(command_executor=selenium_hub_url, options=options)

    elif is_sauce_run:
        # --- 2. ESECUZIONE SU CLOUD (SAUCE LABS) ---
        logging.info(f"Modalità cloud: connessione a Sauce Labs con {browser_name}...")
        sauce_url = (
            f"https://{os.environ['SAUCE_USERNAME']}:{os.environ['SAUCE_ACCESS_KEY']}"
            "@ondemand.eu-central-1.saucelabs.com:443/wd/hub"
        )
        if browser_name == "chrome":
            options = ChromeOptions()
        elif browser_name == "firefox":
            options = FirefoxOptions()
        else:
            raise ValueError(f"Browser non supportato su Sauce Labs: {browser_name}")

        options.platform_name = "Windows 10"
        options.browser_version = "latest"
        sauce_options = {'name': request.node.name}
        options.set_capability('sauce:options', sauce_options)
        driver = webdriver.Remote(command_executor=sauce_url, options=options)

    else:
        # --- 3. ESECUZIONE LOCALE ---
        logging.info(f"Modalità locale: avvio di {browser_name}...")
        if browser_name == "chrome":
            options = ChromeOptions()
            options.add_argument("--incognito")
            options.add_argument("--disable-notifications")
            # Non è necessario specificare il 'service'. Selenium Manager lo gestisce.
            driver = webdriver.Chrome(options=options)
        elif browser_name == "firefox":
            options = FirefoxOptions()
            options.add_argument("-private")
            driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Browser non supportato localmente: {browser_name}")

    driver.set_window_size(width, height)
    yield driver  # Il test viene eseguito qui

    # Teardown: viene eseguito dopo che il test è terminato
    driver.quit()


#---------- FIXTURE DI STATO -------------------

@pytest.fixture(scope="function")
def standard_user_logged_in(login_page, product_page, base_url, standard_user_credentials):
    """
    Fixture di base che esegue il login SOLO con l'utente standard.
    NON è parametrizzata e può essere usata in qualsiasi test
    che ha bisogno di un utente loggato come pre-requisito.
    """
    username, password = standard_user_credentials
    logging.info(f"[Fixture Setup] Eseguo login standard con utente: {username}")
    login_page.open(base_url)
    login_page.login(username, password)
    # Auto-verifica: la fixture controlla di aver fatto bene il suo lavoro
    assert product_page.is_on_products_page(), "Setup del login standard fallito."
    logging.info("[Fixture Setup] Login standard riuscito. Pronto per il test.")
    yield product_page #restituisco pagina con product page
    # --- TEARDOWN (eseguito dopo il test) ---
    logging.info(f"[Fixture Teardown] Test che usava standard_user_logged_in per l'utente '{username}' completato.")



#Fixture per partire da stato in cui utente ha aggiunto 1 prodotto al carrello
@pytest.fixture(scope="function")
def products_page_with_item_in_cart(standard_user_logged_in: "ProductPage"):
   # 'product_page' è la richiesta alla fixture "fabbrica".
    # 'product_page_instance' è la variabile che usiamo per agire.
    product_page_instance = standard_user_logged_in
    # Aggiungiamo prodotto al carrello
    product_added = "Sauce Labs Bike Light"
    product_page_instance.add_to_cart_by_product_name(product_added)
    logging.info(f"[Fixture Setup] Aggiunto '{product_added}' al carrello.")
    assert product_page_instance.get_cart_badge_count() == "1", "Setup fallito: il prodotto non è nel carrello"
    yield (product_page_instance, product_added) #passa pagina e nome prodotto al test/fixture successiva
    # Teardown (eseguito dopo il test)
    logging.info("[Fixture Teardown] Test che usava 'cart_with_one_item' completato.")

#Utente naviga al carrello dalla pagina prodotto
@pytest.fixture(scope="function")
def cart_page_with_one_item(products_page_with_item_in_cart) -> Tuple["CartPage", str]: #hint perchè restituisce CartPage e stringa/prod added
    # ricevo pacchetto da yield della fixture e lo spacchetto in due variabili
    product_page_instance, product_added = products_page_with_item_in_cart
    # Navighiamo al carrello
    cart_page_instance = product_page_instance.click_cart_button() #mi salvo la pagina così poi la restituisco alle prossime fixture che la richiedono; #click_cart_button restituisce cart_page in product_page per com'è dichiarato
    logging.info("[Fixture Setup] Navigato alla pagina del carrello.")
    assert cart_page_instance.is_on_cart_page(), f"Setup fallito: non siamo sulla pagina carrello"
    assert cart_page_instance.is_product_in_cart(product_added), f"Setup fallito: prodotto non è nel carrello"
    yield (cart_page_instance, product_added) #passa risultato al test/fixture successiva - importante ordine sia giusto
    # Teardown (eseguito dopo il test)
    logging.info("[Fixture Teardown] Test che usava 'cart_with_one_item' completato.")

@pytest.fixture(scope="function")
def checkout_step_one_page_with_item(cart_page_with_one_item) -> "CheckoutStepOnePage": #-> è una hint/suggerimento per l'IDE per dirgli cosa restituirà la fixture
    cart_page_instance, _ = cart_page_with_one_item #con _ mi scarto il product added
    checkout_page_instance = cart_page_instance.click_checkout_button()
    assert checkout_page_instance.is_on_checkout_page(), \
        "Setup della fixture fallito: non siamo sulla pagina di checkout (Step 1)."
    logging.info("[Fixture Setup] Verifica riuscita. Pronto per il test.")
    yield checkout_page_instance
    # 6. Teardown
    logging.info("[Fixture Teardown] Test sul form di checkout completato.")

@pytest.fixture(scope="function")
def checkout_step_two_page_with_summary(checkout_step_one_page_with_item: CheckoutStepOnePage) -> "CheckoutStepTwoPage":
    checkout_page_instance = checkout_step_one_page_with_item  # spacchetto ciò che ritorna dalla fixture
    checkout_page_instance.fill_checkout_form("Claudio", "Ramo", "12345")
    checkout_step_two_page = checkout_page_instance.click_continue_button()  # assegno il return ad una nuova variabile per controllare le sue funzioni
    assert checkout_step_two_page.is_on_checkout_step_two(), "Setup fixture fallito: non siamo su pagina riepilogo"
    logging.info("[Fixture Setup], Verifica riuscita, siamo sulla pagina riepologo")
    yield checkout_step_two_page
    #Teardown
    logging.info("[Fixture Teardown] Test sul form di checkout step 2 completato.")


@pytest.fixture(scope="function")
def checkout_complete_page_with_order_placed(checkout_step_two_page_with_summary: CheckoutStepTwoPage) -> "CheckoutCompletePage":
    checkout_step_two_page_instance = checkout_step_two_page_with_summary #spacchetto
    checkout_complete_page = checkout_step_two_page_instance.click_finish_button()
    assert checkout_complete_page.is_checkout_complete(), "Setup fixture fallito: non siamo su pagina conferma ordine"
    logging.info("[Fixture Setup], Verifica riuscita, siamo sulla pagina del checkout con summary")
    yield checkout_complete_page
    #Teardown
    logging.info("[Fixture Teardown] Test sul form di checkout con summary completato.")

