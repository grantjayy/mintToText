#!/usr/bin/env bash

git pull ___
docker build -t flask:latest . && docker run -p 80:8080 flask:latest