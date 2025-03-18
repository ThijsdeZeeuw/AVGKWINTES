#!/bin/bash

# Check if secrets.txt exists
if [ ! -f "secrets.txt" ]; then
    echo "Error: secrets.txt not found. Please run generate_secrets.sh first."
    exit 1
fi

# Create a backup of the current .env file if it exists
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Read secrets from secrets.txt and apply them to .env
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ $key =~ ^#.*$ ]] && continue
    [[ -z $key ]] && continue
    
    # Remove any quotes from the value
    value=$(echo "$value" | tr -d '"'"'")
    
    # Update the .env file
    if grep -q "^$key=" .env; then
        # Key exists, update its value
        sed -i "s|^$key=.*|$key=$value|" .env
    else
        # Key doesn't exist, append it
        echo "$key=$value" >> .env
    fi
done < secrets.txt

echo "Secrets have been applied to .env file"
echo "A backup of the previous .env file has been created"

# Created and maintained by Z4Y 