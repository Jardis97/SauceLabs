
# 1. FORWARD REFERENCES E TYPE_CHECKING
from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import os  # libreria per leggere variabili d'ambiente, per Jenkins
import time
from typing import Tuple  # lo uso per gli hint

import allure
import pytest
from appium.webdriver import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
#chrome driver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from pages.base_page import BasePage


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


# Per risolvere problema, devi dire a `pytest` di accettare l'opzione `--browser_name` come argomento tramite l'uso di una funzione chiamata `pytest_addoption`.
def pytest_addoption(parser):
    parser.addoption(
        "--browser_name",
        action="store",
        default="chrome",
        help="browser selection"
    )
    parser.addoption(
        "--window_size",
        action="store",
        default="1280,800",
        help="dimensione finestra browser (es: 1280,800 o 375,812)"
    )
#pytest tests/ --browser_name=firefox/edge ecc

    parser.addoption(
        "--all-usernames", action="store_true", default=False, help="Esegui test con tutti gli username"
    )

@pytest.fixture(scope="function") #scope="function" si distrugge ad ogni test, module/session no
def browserInstance(request): #request prende ciò che gli metto nella linea di comando (es. firefox o chrome) per capire quale browser avviare
    browser_name = request.config.getoption("browser_name", default="chrome") #quando nel terminale gli metto la linea di comando "pytest test_nomefile.py --browser_name firefox, lui si prende il nome di quest'ultima per capire quale browser usare
    window_size = os.environ.get("RESOLUTION") or request.config.getoption("window_size") #jenkins opzione 1, riga di comando opzione 2 - se non specifico prende default ciò che c'è in adoption
    width, height = map(int, window_size.replace("x", ",").split(",")) #trasforma stringa in res
    service_obj = Service() #crea oggetto per il servizio del browser, chromedriver, geckodriver, ecc.

    # Se in parallelo, usa Sauce Labs
    if (
        os.environ.get("PYTEST_XDIST_WORKER")
        and os.environ.get("SAUCE_USERNAME")
        and os.environ.get("SAUCE_ACCESS_KEY")
    ):
        sauce_url = (
            f"https://{os.environ['SAUCE_USERNAME']}:{os.environ['SAUCE_ACCESS_KEY']}"
            "@ondemand.eu-central-1.saucelabs.com:443/wd/hub"
        )
        if browser_name == "chrome":
            options = ChromeOptions()
            options.add_argument("--incognito") #incognito anche su saucelabs
        elif browser_name == "firefox":
            options = FirefoxOptions()
        else:
            raise ValueError(f"Browser non supportato: {browser_name}")

        options.set_capability("browserName", browser_name)
        options.set_capability("platformName", "Windows 10")
        options.set_capability("sauce:options", {})
        driver = webdriver.Remote(command_executor=sauce_url, options=options)
        driver.set_window_size(width, height)
    else:
        if browser_name == "chrome":
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--incognito")
            # chrome_options.add_argument("--headless=new")
            driver = webdriver.Chrome(service=service_obj, options=chrome_options)
            driver.set_window_size(width, height)
            #driver.implicitly_wait(1)
        elif browser_name == "firefox":
            driver = webdriver.Firefox(service=service_obj)
            driver.set_window_size(width, height)
            #driver.implicitly_wait(4)
        else:
            raise ValueError(f"Browser non supportato: {browser_name}")

    yield driver #qui finisce il setup iniziato in riga 19 con pytest.fixture
    driver.quit() #teardown


#---------- FIXTURE DI STATO -------------------

@pytest.fixture(scope="function")
def standard_user_logged_in(browserInstance, login_page, product_page):
    """
    Fixture di base che esegue il login SOLO con l'utente standard.
    NON è parametrizzata e può essere usata in qualsiasi test
    che ha bisogno di un utente loggato come pre-requisito.
    """
    # Per ora, l'utente è "hardcoded". In futuro lo sarà da un file .env
    username = "standard_user"
    password = "secret_sauce"
    logging.info(f"[Fixture Setup] Eseguo login standard con utente: {username}")
    login_page.open()
    login_page.login(username, password)
    # Auto-verifica: la fixture controlla di aver fatto bene il suo lavoro
    assert product_page.is_on_products_page(), "Setup del login standard fallito."
    logging.info("[Fixture Setup] Login standard riuscito. Pronto per il test.")
    yield browserInstance

#Per richiamarmi il login corretto
#Fixture per partire da stato in cui utente ha fatto login
@pytest.fixture(scope="function")
def logged_in_browser(browserInstance, login_page, product_page, username):
    # --- SETUP ---
    logging.info(f"[Fixture Setup] Inizio preparazione per 'logged_in_browser' con utente: {username}")
    login_page.open()
    logging.info(f"[Fixture Setup] Eseguo il login per l'utente: {username}")
    login_page.login(username, "secret_sauce")
    # ASSERT
    assert product_page.is_on_products_page(), "Setup della fixture 'logged_in_browser' fallito: il login non è riuscito."
    logging.info(f"[Fixture Setup] Login per '{username}' riuscito. Pronto per il test.")
    # --- YIELD: Passa il controllo al test ---
    yield browserInstance
    # --- TEARDOWN (eseguito dopo il test) ---
    logging.info(f"[Fixture Teardown] Test che usava 'logged_in_browser' per l'utente '{username}' completato.")

#Fixture per partire da stato in cui utente ha aggiunto 1 prodotto al carrello
@pytest.fixture(scope="function")
def products_page_with_item_in_cart(standard_user_logged_in, product_page):
   # 'product_page' è la richiesta alla fixture "fabbrica".
    # 'product_page_instance' è la variabile che usiamo per agire.
    product_page_instance = product_page
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





#parametrizzo test login per username, genera test separati
def pytest_generate_tests(metafunc):
    if "username" in metafunc.fixturenames:
        if metafunc.config.getoption("--all-usernames"):
            usernames = [
                "standard_user",
                "performance_glitch_user",
                "locked_out_user"
            ]
        else:
            usernames = [os.environ.get("UTENTE", "standard_user")]
        print("Usernames parametrizzati:", usernames)
        metafunc.parametrize("username", usernames)

# Per leggere username da un file CSV, decommenta le seguenti righe
# import csv
    # if metafunc.config.getoption("--all-usernames"):
    #     with open("usernames.csv", newline="") as csvfile:
    #         reader = csv.DictReader(csvfile)
    #         usernames = [row["username"] for row in reader]