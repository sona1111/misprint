#!/usr/bin/env bash

sudo supervisorctl stop misprint-gunicorn
sudo supervisorctl stop misprint-queue
sudo supervisorctl stop misprint-beat

sudo mv /var/www/misprint/config.py /tmp/config.py
sudo rm /var/www/misprint/* -R
sudo cp /home/ubuntu/workspace/misprint_app/* /var/www/misprint -R
sudo mv /tmp/config.py /var/www/misprint/config.py
sudo chmod 777 /var/www/misprint -R

sudo supervisorctl start misprint-gunicorn
sudo supervisorctl start misprint-queue
sudo supervisorctl start misprint-beat

echo "Deploy Complete"