#!/bin/bash

openssl req -new -newkey rsa:2048 -nodes -out ca.csr -keyout ca.key -subj "/C=US/ST=CA/L=Redwood City/O=Mac Experts LLC" && openssl x509 -trustout -signkey ca.key -days 365 -req -in ca.csr -out ca.pem

echo Enter the IP/hostname of your MacShell server:

read server

echo Enter listening port for your MacShell server:

read port

python3 generator.py -s $server -p $port

docker build -t macshell-docker .

docker volume create macshell

sudo docker run --rm -p 443:443 -v macshell:/mshell -ti macshell-docker
