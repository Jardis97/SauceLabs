import time
from pages.login_page import LoginPage
from appium.webdriver import webdriver
import pytest
import allure
#chrome driver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

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

@pytest.fixture(scope="module") #scope="function" si distrugge ad ogni test, module/session no
def browserInstance(request): #request prende ciò che gli metto nella linea di comando (es. firefox o chrome) per capire quale browser avviare
    browser_name = request.config.getoption("browser_name", default="chrome") #quando nel terminale gli metto la linea di comando "pytest test_nomefile.py --browser_name firefox, lui si prende il nome di quest'ultima per capire quale browser usare
    window_size = request.config.getoption("window_size") #imposta risoluzione default quando non metti comando
    width, height = map(int, window_size.split(","))
    service_obj = Service()

    if browser_name == "chrome":
        chrome_options = Options()
        #tolgo pop up password ecc
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--incognito")
        driver = webdriver.Chrome(service=service_obj, options=chrome_options)
        driver.set_window_size(width, height)
        driver.implicitly_wait(1)
    elif browser_name == "firefox":
        driver = webdriver.Firefox(service=service_obj)
        driver.set_window_size(width, height)
        driver.implicitly_wait(4)
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