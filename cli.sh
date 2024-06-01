#!/bin/bash

# Enter a endless loop
while true; do
  echo -ne "\033[32m~> \033[0m"
  
  read url

  if [[ $url == *"utaten"* ]]; then
    ./fetch.sh "${url}"
  elif [[ $url == *"jpmarumaru"* ]]; then
    ./fetch2.sh "${url}"
  fi
done