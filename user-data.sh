#!/usr/bin/env bash
# the contents of this file should be put in the user data field
sudo apt-get install -y git
cd /home/ubuntu/
sudo git clone https://github.com/executivereader/mongo-startup.git
cd /home/ubuntu/mongo-startup
sudo sh startup_script.sh
