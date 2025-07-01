# 1. IMPORTS AND CONFIGURATION
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import allure
import pytest

from tests.conftest import load_user_data_from_csv

if TYPE_CHECKING:
    from pages.login_page import LoginPage
    from pages.product_page import ProductPage

#per il file csv

# Configure logging for this specific test module.
logging.basicConfig(level=logging.INFO)

#-----SMOKE-------
# SMOKE TESTS - FAST, FOCUSED, AND CRITICAL
# These tests verify the most basic and critical functionalities.

@pytest.mark.smoke
@allure.feature("Login errato")
@allure.story("Login con credenziali sbagliate")
@allure.severity(allure.severity_level.CRITICAL)
def test_unsuccesful_login(locked_user_credentials, base_url, login_page: "LoginPage", product_page: "ProductPage"):  #con browserInstance si intende che il browser e' gia' aperto
        username, password = locked_user_credentials
        logging.info(f"[Fixture Setup] Provo login locker con utente: {username}")
        login_page.open(base_url)
        login_page.login(username, password)
        with allure.step("Verifica: Il login è stato respinto e viene mostrato un errore"):
            # Se questa fallisce, il test si ferma qui con lo stato "Failed".
            assert not product_page.is_on_products_page(), \
                "BUG CRITICO: Il login è riuscito con credenziali errate!"
            # Questa parte viene eseguita solo se il primo assert passa, se il login fallisce (cosa che non deve accadere)
            actual_error = login_page.get_error_message()  # assegno a variabile il risultato return
            assert actual_error is not None, "Nessun messaggio di errore visualizzato dopo login fallito."


@pytest.mark.smoke
@allure.feature("Login")
@allure.story("Login con credenziali valide")
@allure.severity(allure.severity_level.CRITICAL)
def test_succesful_login(standard_user_logged_in: "ProductPage"):  #con browserInstance si intende che il browser e' gia' aperto
        product_page_instance = standard_user_logged_in #spacchetto
        assert product_page_instance.is_loaded(), "La pagina prodotti non si è caricata"




#-----END SMOKE_----


# REGRESSION TEST - COMPREHENSIVE AND DATA-DRIVEN
# This test covers multiple scenarios to prevent regressions.

@pytest.mark.regression
@allure.feature("Login")
@allure.story("Regression Test: Login Scenarios from Data Source")
@pytest.mark.parametrize(
    "username, password, expected_outcome, expected_message",
    load_user_data_from_csv()
)
def test_login_scenarios_from_file(
    login_page: "LoginPage",
    product_page: "ProductPage",
    base_url: str,
    username: str,
    password: str,
    expected_outcome: str,
    expected_message: str
):
    """Tests multiple login scenarios using an external CSV data set."""
    allure.dynamic.title(f"Login Test for user: '{username}' - Expected: {expected_outcome}")
    allure.dynamic.severity(allure.severity_level.NORMAL)

    with allure.step(f"Attempting login for user '{username}'"):
        login_page.open(base_url)
        login_page.login(username, password)

    with allure.step(f"Verifying outcome is '{expected_outcome}'"):
        if expected_outcome == "success":
            assert product_page.is_on_products_page(), \
                f"Login should have succeeded for user '{username}', but it failed."
        else:
            assert not product_page.is_on_products_page(), \
                f"Login should have failed for user '{username}', but it succeeded."

            actual_error = login_page.get_error_message()
            assert actual_error is not None, "Error message was expected but not found."
            assert expected_message in actual_error, \
                f"Incorrect error message. Expected: '{expected_message}', Got: '{actual_error}'"