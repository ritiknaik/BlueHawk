#!/usr/bin/bash

center() {
  termwidth="$(tput cols)"
  padding="$(printf '%0.1s' \ {1..500})"
  printf '%*.*s %s %*.*s\n' 0 "$(((termwidth-2-${#1})/2))" "$padding" "$1" 0 "$(((termwidth-1-${#1})/2))" "$padding"
}

if [ $# -eq 0 ]
then
    echo "BlueHawk Server Started"
    echo "Press Ctrl-C to stop the BlueHawk Server"
    echo ""
    python3 http-server.py
    echo ""
    echo "Bye"
else
    if [[ $1 == "-i" ]]
    then
      center "BlueHawk 1.0"
      echo ""
      center "BlueHawk is an HTTP/1.1 compliant multithreaded server based on RFC 2616"
      echo ""
      echo "It supports Get, Head, Put, Post, Delete methods"
      echo ""
      echo "Status codes handled"
      echo ""
      echo "Successful: 200   201   204   206"
      echo ""
      echo "Redirection: 304"
      echo ""
      echo "Client Error: 400   401   403   404   405   406   412   415   416"
      echo ""
      echo "Server Error: 500   501   505"
      echo ""
      echo "File types that can be sent over the server are:"
      echo ""
      echo "txt    html   php"
      echo "pdf    csv    css" 
      echo "apng   gif    bmp" 
      echo "png    ico    jpeg" 
      echo "jpg    svg    webp"
      echo "json   js     bin"
      echo "mp3    webm   mpeg"
      echo ""
    else
      echo "To run server: bash bluehawk.sh"
      echo "For more info: bash bluehawk.sh -i"
    fi
fi