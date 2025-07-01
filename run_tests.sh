#!/bin/sh
# run_tests.sh

# 1. Pulisci sempre i risultati precedenti
echo "Cleaning up old Allure results..."
rm -rf /app/allure-results/*

# 2. Esegui pytest con tutti gli argomenti passati a questo script
echo "Running pytest with arguments: $@"
pytest --browser=remote --env=sit --resolution=1920,1080 --alluredir=/app/allure-results "$@"
