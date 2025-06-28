import logging
import allure
import pytest

from pages.checkout_page import CheckoutStepOnePage
from pages.product_page import ProductPage

logging.basicConfig(level=logging.ERROR)
import os  # per far leggere a jenkins il parametro che useremo per username


@pytest.mark.smoke
@pytest.mark.login
@allure.feature("Login")
@allure.story("Login con credenziali valide")
@allure.severity(allure.severity_level.CRITICAL)
def test_succesful_login(standard_user_logged_in, product_page):  #con browserInstance si intende che il browser e' gia' aperto
        assert product_page.is_loaded(), "La pagina prodotti non si è caricata"


@pytest.mark.smoke
@pytest.mark.products
@allure.feature("Add product to cart")
@allure.story("Aggiungiamo un prodotto al cart e verifichiamo che badge si aggiorni")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_product_to_cart_updates_badge(standard_user_logged_in, product_page):
    """Verifica che aggiungendo un prodotto, il badge del carrello si aggiorni."""
    #Arrange
    product_to_add = "Sauce Labs Bike Light"
    # ACT
    product_page.add_to_cart_by_product_name(product_to_add)
    # ASSERT
    assert product_page.get_cart_badge_count() == "1", "Il badge del carrello non è aggiornato correttamente"

@pytest.mark.smoke
@pytest.mark.products
@allure.feature("Verify product added to cart is the right one")
@allure.story("Verifichiamo prodotto aggiunto sia quello giusto")
@allure.severity(allure.severity_level.CRITICAL)
def test_cart_content_is_correct(cart_page_with_one_item):
    cart_page_instance, product_added = cart_page_with_one_item #mi spacchetto ciò che mi ritorna dalla fixture
    assert cart_page_instance.is_product_in_cart(product_added), "Prodotto non trovato"
    logging.info(
        f"Verifica: Il prodotto '{product_added}' è stato trovato correttamente nel carrello.")

@pytest.mark.smoke
@pytest.mark.checkout
@allure.feature("Checkout")
@allure.story("Checkout completo")
@allure.severity(allure.severity_level.CRITICAL)
def test_full_checkout_process(checkout_complete_page_with_order_placed: "CheckoutCompletePage"): #la parte finale è il type hint/suggerimento
    checkout_complete_page = checkout_complete_page_with_order_placed #spacchetto ciò che ritorna dalla fixture
    assert checkout_complete_page.get_confirmation_message(), "Conferma non avvenuta"
    logging.info("Verifica della pagina di conferma ordine superata con successo.")


@pytest.mark.smoke
@pytest.mark.homeReset
@allure.feature("Home Reset")
@allure.story("Post Checkout torna alla Home con cart vuoto")
@allure.severity(allure.severity_level.CRITICAL)
def test_back_home_button_reset_application(checkout_complete_page_with_order_placed: "CheckoutCompletePage"):
    checkout_complete_page = checkout_complete_page_with_order_placed #spacchetto ciò che ritorna dalla fixture
    product_page_instance = checkout_complete_page.click_back_home_button()
    #Vefico che il bottone mi porti alla pagina dei prodotti
    assert product_page_instance.is_on_products_page(), "Non siamo sulla pagina dei prodotti dopo il reset"
    #Verifico che il badge del carrello sia vuoto
    assert product_page_instance.is_cart_empty(), "Il carrello non è vuoto dopo il reset"





