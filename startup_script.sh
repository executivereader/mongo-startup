#!/usr/bin/env bash
sudo apt-get update
sudo mkfs -t ext4 /dev/xvdb
sudo mkdir /data
sudo mkdir /data/disk1
sudo mount /dev/xvdb /data/disk1
sudo mkdir /data/disk1/server
sudo chmod 777 /data/disk1/server
sudo mkdir /data/disk1/log
sudo touch /data/disk1/log/mongo.txt
sudo chmod 666 /data/disk1/log/mongo.txt
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
sudo echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
sudo apt-get update
sudo apt-get install mongodb-10gen
sudo service mongodb stop
sudo rm /etc/mongodb.conf
sudo cp mongodb.conf /etc/mongodb.conf
sudo service mongodb start
python update_replica_set.py
