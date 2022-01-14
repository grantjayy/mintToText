#!/usr/bin/env bash

sudo apt update -y && sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-y
sudo chmod 666 /var/run/docker.sock

# sudo ufw allow 'OpenSSH'
# sudo ufw allow 'Nginx HTTP'
# sudo ufw enable

chmod +x ./deployment.sh