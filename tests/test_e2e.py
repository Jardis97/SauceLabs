import pytest
import allure
import logging
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
logging.basicConfig(level=logging.ERROR)
import os #per far leggere a jenkins il parametro che useremo per username
from tests.conftest import allure_screenshot


@pytest.mark.smoke
@pytest.mark.login
@allure.feature("Login")
@allure.story("Login con credenziali valide")
@allure.severity(allure.severity_level.CRITICAL)
def test_CorrectUser(browserInstance, product_page, username):  #con browserInstance si intende che il browser e' gia' aperto
        login_page = LoginPage(browserInstance)
        login_page.open()
        assert login_page.is_username_field_present()
        print(f"Username usato: {username}")
        login_page.enter_username(username)
        login_page.enter_password("secret_sauce")
        login_page.click_login()
        assert product_page.wait_for_products_page_loaded(), "La pagina prodotti non si è caricata"
        allure_screenshot(browserInstance, "Pagina Prodotti post login")
        assert product_page.is_on_products_page()

@pytest.mark.smoke
@pytest.mark.products
@allure.feature("Add product to cart")
@allure.story("Aggiungiamo un prodotto al cart")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_product_to_cart(browserInstance, product_page):  #con logged_in_browser si intende che il browser e' gia' loggato con utenza corretta
    product_page.open()
    #assert product_page.is_on_products_page()
    product_page.add_to_cart_by_product_name("Sauce Labs Bike Light") #scelgo qui quale proddtto aggiungere
    allure_screenshot(browserInstance, "prodotto aggiunto al carrello")
    product_page.get_cart_badge_count()
    if product_page.cart_badge_value == "1":
        print("OK: numero nel cartello coincide")
        assert True
    else:
        logging.error("ERRORE: numero nel cartello NON coincide")
        assert False

    product_page.click_cart_button()
    cart_page = CartPage(browserInstance)
    allure_screenshot(browserInstance, "Pagina del carrello raggiunta")
    assert cart_page.is_on_cart_page()
    print("Pagina del carrello raggiunta")
    cart_page.is_product_in_cart("Sauce Labs Bike Light")
    assert True
    print("OK: il prodotto e' presente anche nel carrello")

    cart_page.click_checkout_button()

@pytest.mark.smoke
@pytest.mark.checkout
@allure.feature("Checkout")
@allure.story("Checkout completo")
@allure.severity(allure.severity_level.CRITICAL)
def test_checkout(browserInstance, product_page, cart_page, checkout_page):
    allure.attach(browserInstance.get_screenshot_as_png(), name="Pagina checkout iniziale 1",
                  attachment_type=allure.attachment_type.PNG)
    assert checkout_page.is_on_checkout_page()
    print("Pagina del checkout raggiunta")
#Ora metto info corrette per fare ordine
    checkout_page.compile_checkout("Generali", "Assicurazioni", "12345")
    assert checkout_page.is_on_checkout_step_two()
    print("Pagina del checkout raggiunta")
    allure_screenshot(browserInstance, "Form compilato checkot")
    checkout_page.finish_checkout()

    assert checkout_page.is_checkout_complete()

@pytest.mark.smoke
@pytest.mark.homeReset
@allure.feature("Home Reset")
@allure.story("Post Checkout torna alla Home con cart vuoto")
@allure.severity(allure.severity_level.CRITICAL)
def test_homeReset(browserInstance, product_page, cart_page, checkout_page):
    # Ora torno pagina prodotto e verifico che carrello sia vuoto
    checkout_page.back_toProducts()
    allure_screenshot(browserInstance, "RItorno pagina prodotti")
    assert product_page.is_on_products_page()
    print("Ritorno alla pagina dei prodotti effettuato con successo")
    #verifico che il badge del carrello sia vuoto
    assert product_page.is_cart_empty()




