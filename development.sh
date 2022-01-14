#!/usr/bin/env bash

docker build -t flask:latest . && docker run -p 9000:8080 flask:latest