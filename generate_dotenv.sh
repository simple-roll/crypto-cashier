#!/bin/bash

if ! command -v openssl >/dev/null 2>&1; then
    echo "OpenSSL util is not available. Please install"
    exit 1
fi

generate_key() {
    length=$1
    openssl rand -base64 $length | tr '+/' '-_' | tr -d '='
}

django_admin_secret_path="$(generate_key 8)/admin/"

config="# CASHIER CONFIG

# Important! Copy and store this key in a secure location.
# Losing access to this key may result in the loss of your funds.
DB_FIELD_ENCRYPTION_KEY=$(generate_key 32)=

# Payment methods available by default
ETHEREUM_NATIVE_COIN_ENABLED=true
ETHEREUM_USDT_ERC20_ENABLED=true
ETHEREUM_USDC_ERC20_ENABLED=true
TRON_NATIVE_COIN_ENABLED=true
TRON_USDT_TRC20_ENABLED=true
TRON_USDC_TRC20_ENABLED=true

# Scan sites API keys. Optional for increase API limits
ETHERSCAN_API_KEY=
TRONSCAN_API_KEY=

# Admin settings
# Use URL '127.0.0.1:8080/$django_admin_secret_path' to open django admin
DJANGO_ADMIN_SECRET_PATH=$django_admin_secret_path
DJANGO_SUPERUSER_USERNAME=admin
# This password can be set blank here after superuser created in first run
DJANGO_SUPERUSER_PASSWORD=$(generate_key 12)
# Email is not required can leave just like this
DJANGO_SUPERUSER_EMAIL=some@email.com

# Change these hosts if you are going to connect domain name to expose sevice to public
DJANGO_ALLOWED_HOSTS=127.0.0.1

# List of all timezones https://gist.github.com/mjrulesamrat/0c1f7de951d3c508fb3a20b4b0b33a98
TIME_ZONE=UTC

# Using system ports
GUNICORN_PORT=8000
NGINX_PORT=8080

# Celery beat intervals in seconds. Only 'BEAT_SYNC_CHAIN_TRANZES_INTERVAL' beat job uses scansites API, other else just use local DB requests
BEAT_SYNC_CHAIN_TRANZES_INTERVAL=60
BEAT_TRANZES_CONFIRM_CHECK_INTERVAL=30
BEAT_HANDLE_CONFIRMED_INVOICES_INTERVAL=30
BEAT_HANDLE_EXPIRED_INVOICES_INTERVAL=30

# DB settings
POSTGRES_USER=user
POSTGRES_PASSWORD=$(generate_key 16)
POSTGRES_DB=cashier
POSTGRES_HOST=postgres

# Django rest essential
DJANGO_DEBUG=false
DJANGO_NATIVE_SERVER=false
DJANGO_SECRET_KEY=$(generate_key 32)

# Tests addresses settings. This addresses should have received USDT transactions 
# Not requed if don't going to run the Django tests
ETHEREUM_TEST_ADDRESS=
TRON_TEST_ADDRESS=
"

if [ -f .env ]; then
    read -p ".env already exists. Do you want to override it? (y/N): " choice
    if [ "$choice" != "y" ]; then
        echo "Aborted."
        exit 0
    fi
fi

echo "$config" > .env
echo "New .env has been generated"

