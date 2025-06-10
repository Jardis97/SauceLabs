import time
from pages.login_page import LoginPage
from appium.webdriver import webdriver
import pytest
import allure
#chrome driver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
import os #libreria per leggere variabili d'ambiente, per Jenkins

@pytest.fixture
def product_page(browserInstance):
    return ProductPage(browserInstance)

@pytest.fixture
def cart_page(browserInstance):
    return CartPage(browserInstance)

@pytest.fixture
def checkout_page(browserInstance):
    return CheckoutPage(browserInstance)

#Def per fare screenshot in qualsiasi test
def allure_screenshot(driver, name):
    allure.attach(
        driver.get_screenshot_as_png(),
        name=name,
        attachment_type=allure.attachment_type.PNG
    )
#fine screenshoot


# Per risolvere questo problema, devi dire a `pytest` di accettare l'opzione `--browser_name` come argomento tramite l'uso di una funzione chiamata `pytest_addoption`.
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

@pytest.fixture(scope="module") #scope="function" si distrugge ad ogni test, module/session no
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
            driver.implicitly_wait(1)
        elif browser_name == "firefox":
            driver = webdriver.Firefox(service=service_obj)
            driver.set_window_size(width, height)
            driver.implicitly_wait(4)
        else:
            raise ValueError(f"Browser non supportato: {browser_name}")

    yield driver #qui finisce il setup iniziato in riga 19 con pytest.fixture
    driver.quit() #teardown


#Per richiamarmi il login corretto
@pytest.fixture
def logged_in_browser(browserInstance):
    login_page = LoginPage(browserInstance)
    login_page.open()
    login_page.enter_username("standard_user")
    login_page.enter_password("secret_sauce")
    login_page.click_login()
    return browserInstance


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