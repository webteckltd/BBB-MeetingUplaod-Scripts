#!/bin/bash

# Check if we are root
uid=$(id -u)
if [ $uid -ne 0 ]
then 
    echo "Please run as root"
    exit 1
fi

# Install python and pip
apt-get install -y python3
apt-get install -y python3-pip

#install boto3 s3 python client 
pip3 install boto3

chmod 755 /usr/local/bigbluebutton/core/scripts/post_publish/*

# Create log directory
mkdir -p /var/log/bigbluebutton/s3Upload
chown bigbluebutton:bigbluebutton /var/log/bigbluebutton/s3Upload
chmod -R go+rw /var/log/bigbluebutton/s3Upload

# Copy python scripts to post_publish directory
cp src/*.py /usr/local/bigbluebutton/core/scripts/post_publish


# Copy ruby script that controlls the download process
cp src/*.rb /usr/local/bigbluebutton/core/scripts/post_publish
