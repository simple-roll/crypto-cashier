#!/bin/bash

read -p "Do you want reset db and remove all data? (y/n): " choice
if [ "$choice" != "y" ]; then
    echo "Aborted."
    exit 0
fi

rm -r postgres/data

# Remove migrations also
rm -r django/core/migrations/00*.py
rm -r django/ethereum/migrations/00*.py
