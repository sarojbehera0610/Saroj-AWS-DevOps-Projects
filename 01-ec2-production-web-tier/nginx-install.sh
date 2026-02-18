#!/bin/bash
# Production Nginx deployment script for AWS EC2 t3.micro
sudo yum update -y
sudo amazon-linux-extras install nginx1 -y
sudo systemctl start nginx
sudo systemctl enable nginx
sudo chown -R ec2-user:ec2-user /usr/share/nginx/html/
echo "<h1>Production Nginx Live ✅</h1>" | sudo tee /usr/share/nginx/html/index.html
