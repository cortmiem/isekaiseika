#!/bin/bash

# Enter a endless loop
while true; do
  echo -ne "\033[32m~> \033[0m"
  
  # Read user input
  read url

  # Execute the `fetch.sh' script with the provided url
  ./fetch.sh "${url}"
done