#!/bin/bash

read -p "Do you want remove all redis data? (y/n): " choice
if [ "$choice" != "y" ]; then
    echo "Aborted."
    exit 0
fi

rm -r redis/data
