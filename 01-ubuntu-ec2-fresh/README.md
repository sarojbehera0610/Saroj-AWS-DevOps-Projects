# 🟢 01 Production Ubuntu EC2 Deployment

**Ubuntu Server 24.04 LTS → t3.micro → LIVE 13.235.245.235**

## Live Infrastructure
🌐 Public IP: 13.235.245.235 ← SSH + Web access
🔒 Private IP: 172.31.47.200 ← VPC internal
💾 Storage: 20GB gp3 EBS
🔑 Key: saroj-ubuntu-prod-2026.pem
🛡️ Security Group: SSH(22)+HTTP(80) → Anywhere


## Production Access
bash

# SSH Connection (Ubuntu = ubuntu user)
ssh -i "saroj-ubuntu-prod-2026.pem" ubuntu@13.235.245.235

# Verify instance metadata  
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4
# 13.235.245.235
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/local-ipv4
# 172.31.47.200

Day-1 Production Setup  

# Ubuntu production hardening + Nginx
sudo apt update && sudo apt upgrade -y
sudo apt install nginx ufw -y
sudo ufw allow 'Nginx Full' && sudo ufw --force enable
sudo systemctl enable --now nginx
sudo cat index.nginx-debian.html
echo "<h1>Ubuntu Production Live ✅ 13.235.245.235</h1>" | sudo tee /var/www/html/index.nginx-debian.html

Architecture Diagram

Internet → SG(Anywhere 22/80) → Ubuntu 24.04 → Nginx → 20GB EBS

Status: 🟢 3/3 checks passed | 20GB production storage

Live Verification
✅ SSH: ubuntu@ip-172-31-47-200:~$

✅ Nginx: http://13.235.245.235

✅ index.nginx-debian.html customized

