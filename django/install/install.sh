#!/bin/bash

# Create and switch environmen
PYTHON_ENV_PATH=/home/user/django/env
if [ -z "$(ls -A $PYTHON_ENV_PATH)" ]; then
    echo "Make python env"
    python -m venv $PYTHON_ENV_PATH
fi
echo "Activate python env"
source $PYTHON_ENV_PATH/bin/activate
pip install  -r requirements.txt \
  --default-timeout=10000  # For slow connections

# Run the Django makemigrations command with --check
output=$(python manage.py makemigrations --check 2>&1)

# Check if the output contains "No changes detected"
if [[ $output == *"No changes detected"* ]]; then
    echo "No migrations needed."
else
    echo "Migrations are needed."
    python manage.py makemigrations
    echo "$output"
fi

# Check for unapplied migrations
unapplied_migrations=$(python manage.py showmigrations --plan | grep "\[ \]")

if [ -n "$unapplied_migrations" ]; then
    echo "There are unapplied migrations:"
    echo "$unapplied_migrations"
    echo "Let's apply them"
    python manage.py migrate
else
    echo "All migrations are applied."
fi

echo "Create django superuser"
output=$( { python manage.py createsuperuser --no-input; } 2>&1 ) || true
if echo "$output" | grep -q "That username is already taken"; then
    echo "Django superuser already exists"
elif echo "$output" | grep -q "Superuser created successfully"; then
    echo "Superuser created"
else
    echo "$output"
    exit 1
fi

# Update payment methods 
./manage.py shell < ./install/update_payment_methods.py 

# Staticfiles
./manage.py collectstatic --no-input

# Bulma Framework
BULMA_JS_URL=https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css
BULMA_JS_PATH=./staticfiles/bulma.min.css
if [ ! -f $BULMA_JS_PATH ]; then
  echo "Download Bulma Framework"
  wget -O $BULMA_JS_PATH $BULMA_JS_URL
fi

echo "Django ready to use"
