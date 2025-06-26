import logging
import allure
import pytest

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
def test_checkout_form_is_filled(checkout_step_one_page_with_item):
    checkout_page_instance = checkout_step_one_page_with_item #spacchetto ciò che ritorna dalla fixture
    checkout_page_instance.fill_checkout_form("Claudio", "Ramo", "12345")


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
    assert product_page.is_cart_empty(), "il cartello è vuoto ritornando alla home page"




