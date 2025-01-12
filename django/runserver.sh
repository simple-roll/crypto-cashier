#!/bin/bash

if [ "$DJANGO_NATIVE_SERVER" = "true" ]; then
    ./env/bin/python \
        manage.py runserver \
        0.0.0.0:$GUNICORN_PORT
else
    ./env/bin/gunicorn \
        cashier.wsgi \
        --bind 0.0.0.0:$GUNICORN_PORT 
fi
