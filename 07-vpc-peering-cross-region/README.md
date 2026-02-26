# 🟢 07 VPC Peering Cross-Region (Mumbai ↔ N. Virginia)

**VPC-A (Mumbai) Public/Private → Peering → VPC-B (N.Virginia) Private → Ping 175.12.246.82 ✓**

## 🎯 Cross-Region Architecture
Local → SCP → VPC-A Mumbai (ap-south-1)
├── Public EC2 (172.15.0.x) → NGINX ✓
└── Private EC2 (172.15.156.82)
↓ VPC Peering (pcx-xxx)
VPC-B N.Virginia (us-east-1)
└── Private EC2 (175.12.246.82) ← PING ✓

## **📋 COMPLETE PRODUCTION STEPS **

### **🌍 VPC-A Mumbai Region (ap-south-1)**

**Step 1: Create VPC-A**
VPC → Create VPC:
├── Name: VPC-A
├── IPv4 CIDR: 172.15.0.0/16

** #1: VPC-A 172.15.0.0/16 created**

**Step 2: Create VPC-A Public Subnet**
Subnets → Create:
├── Name: Subnet-01-VPC-A-Public
├── VPC: VPC-A
├── AZ: ap-south-1a
├── CIDR: 172.15.0.0/17

** #2: Subnet-01-VPC-A-Public 172.15.0.0/17**

**Step 3: Create VPC-A Private Subnet**
Create subnet:
├── Name: Subnet-02-VPC-A-Private
├── AZ: ap-south-1a
├── CIDR: 172.15.128.0/17

** #3: Subnet-02-VPC-A-Private 172.15.128.0/17**

**Step 4: Create & Attach IGW to VPC-A**
IGW → Create → Name: IGW-VPC-A → Attach VPC-A

** #4: IGW-VPC-A attached**

**Step 5: Edit VPC-A Route Table → Add IGW**
Route Tables → Main RT → Edit routes:
├── 0.0.0.0/0 → IGW-VPC-A

** #5: VPC-A RT → 0.0.0.0/0 → igw-[ID]**

**Step 6: Launch VPC-A Public EC2 (Instance01-Public-VPC-Mumbai)**
EC2 → Launch:
├── Name: Instance01-Public-VPC-Mumbai
├── AMI: Ubuntu 24.04 LTS
├── t3.micro
├── Key: saroj-peering-key.pem (Download)
├── VPC: VPC-A → Subnet-01-VPC-A-Public
├── Auto-assign Public IP: ENABLE ✓

** #6: Public EC2 running → Public IP ✓**

**Step 7: Add User Data (NGINX) + Security Group**
Advanced → User data:

#!/bin/bash
apt update && apt install nginx -y
echo "<h1>Welcome VPC-A</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx

Security Group → Add rules:
├── SSH (22) | 0.0.0.0/0
├── HTTP (80) | 0.0.0.0/0
├── ICMP IPv4 | 0.0.0.0/0

** #7: User data + SG rules**

**Step 8: Launch VPC-A Private EC2 (Instance02-Private-VPC-Mumbai)**
Name: Instance02-Private-VPC-Mumbai
├── VPC: VPC-A → Subnet-02-VPC-A-Private
├── Auto-assign Public IP: DISABLE ✗
├── Same SG (SSH/ICMP)

** #8: Private EC2 → Private IP 172.15.156.82 ✓**

### **🇺🇸 VPC-B N. Virginia Region (us-east-1)**

**Step 9: Switch Region → Create VPC-B**
Region: US East (N. Virginia) us-east-1
VPC → Create:
├── Name: VPC-B
├── CIDR: 175.12.0.0/16

** #9: VPC-B 175.12.0.0/16 (us-east-1)**

**Step 10: Create VPC-B Private Subnet**
Subnets → Create:
├── Name: Subnet-01-VPC-B-Private
├── VPC: VPC-B
├── AZ: us-east-1a
├── CIDR: 175.12.0.0/16

**#10: Subnet-01-VPC-B-Private**

**Step 11: Associate VPC-B Main RT with Private Subnet**
Route Tables → Main RT → Edit subnet associations:
├── Subnet-01-VPC-B-Private

** #11: VPC-B RT → Private subnet associated**

**Step 12: Launch VPC-B Private EC2**
Name: Instance01-Private-VPC-B
├── AMI: Ubuntu 24.04 LTS
├── VPC: VPC-B → Subnet-01-VPC-B-Private
├── Auto-assign Public IP: DISABLE ✗
├── SG: SSH(22)/ICMP IPv4 All Traffic

** #12: VPC-B Private EC2 → Private IP 175.12.246.82 ✓**

### **🌉 VPC Peering Connection**

**Step 13: Create Peering Connection (Mumbai VPC-A → N.Virginia VPC-B)**
Mumbai Region → VPC → Peering Connections → Create:
├── VPC ID (Requester): vpc-[VPC-A-ID]
├── Region: us-east-1
├── VPC ID (Accepter): vpc-[VPC-B-ID]

** #13: pcx-[ID] → Pending Acceptance**

**Step 14: Accept Peering Request (N.Virginia)**
N.Virginia → Peering Connections → Actions → Accept Request

** #14: pcx-[ID] → Active ✓**

### **🛤️ Route Tables + Specific Routes**

**Step 15: VPC-A Route Table → Add VPC-B Private IP Route**
Mumbai → Route Tables (Main) → Edit routes:
├── Destination: 175.12.246.82/32
├── Target: pcx-[Peering-ID]

** #15: VPC-A RT → 175.12.246.82/32 → pcx-[ID]**

**Step 16: VPC-B Route Table → Add VPC-A Private IP Route**
N.Virginia → Route Tables (Main) → Edit routes:
├── Destination: 172.15.156.82/32
├── Target: pcx-[Peering-ID]

** #16: VPC-B RT → 172.15.156.82/32 → pcx-[ID]**

### **🔑 SSH Access Chain + Cross-VPC Ping**

**Step 17: SCP Key Local → VPC-A Public EC2**
Local Terminal:
scp -i saroj-peering-key.pem saroj-peering-key.pem ubuntu@[VPC-A-Public-IP]:~/.ssh/

** #17: SCP 100% success**

**Step 18: SSH VPC-A Public → Copy Key to VPC-A Private**
ssh -i saroj-peering-key.pem ubuntu@[VPC-A-Public-IP]

** #18: Key copied to VPC-A Private**

**Step 19: SSH VPC-A Public → SSH VPC-A Private**
ssh -i ~/.ssh/saroj-peering-key.pem ubuntu@172.15.156.82
chmod 600 ~/.ssh/saroj-peering-key.pem

** #19: VPC-A Private access ✓**

**Step 20: VPC-A Private → Ping VPC-B Private (175.12.246.82)**
ping -c 10 175.12.246.82

64 bytes from 175.12.246.82 ✓

** #20: 64 bytes... 0% packet loss → CROSS-REGION PING ✓**

## **📊 VPC Peering Summary**
| VPC | Region | CIDR | Public EC2 | Private EC2 | Peering Route |
|-----|--------|------|------------|-------------|---------------|
| VPC-A | Mumbai ap-south-1 | 172.15.0.0/16 | 172.15.0.x ✓ | 172.15.156.82 | → 175.12.246.82/32 |
| VPC-B | N.Virginia us-east-1 | 175.12.0.0/16 | - | 175.12.246.82 | → 172.15.156.82/32 |
