# 🟢 06 VPC Public/Private Subnets + IGW + 2-Tier Architecture

**Custom VPC → Public Subnet (Frontend EC2) → Private Subnet (DB EC2) → IGW → Route Table → Internet Access**

## 🎯 Architecture Diagram
Internet
↓ IGW
Custom VPC (10.0.0.0/16)
├── Public Subnet 10.0.1.0/24 (ap-south-1a)
│ └── Frontend EC2 (Public IP ✓)
└── Private Subnet 10.0.2.0/24 (ap-south-1a)
└── Database EC2 (Public IP ✗)
↓ Route Table → IGW (0.0.0.0/0)

## **📋 COMPLETE PRODUCTION STEPS **

### **Step 1: Create Custom VPC**
VPC Dashboard → Your VPCs → Create VPC:
├── Name tag: MyApp-VPC
├── IPv4 CIDR: 10.0.0.0/16
├── Tenancy: Default

**#1: MyApp-VPC created → 10.0.0.0/16 CIDR**

### **Step 2: Create Public Subnet (Frontend)**
Subnets → Create subnet:
├── VPC: MyApp-VPC
├── Subnet name: Public-Subnet-Frontend (10.0.1.0/24)
├── Availability Zone: ap-south-1a
├── IPv4 CIDR: 10.0.1.0/24 (Auto-fill)

** #2: Public-Subnet-Frontend created → 10.0.1.0/24**

### **Step 3: Create Private Subnet (Database)**
Same → Subnet name: Private-Subnet-DB (10.0.2.0/24)
├── Availability Zone: ap-south-1a
├── IPv4 CIDR: 10.0.2.0/24

** #3: Private-Subnet-DB created → 10.0.2.0/24**

### **Step 4: Create & Attach Internet Gateway**
Internet Gateways → Create internet gateway:
├── Name: MyApp-IGW

Actions → Attach to VPC → MyApp-VPC

** #4: MyApp-IGW → Status: Attached**

** #5: Public-RouteTable → 0.0.0.0/0 → igw-[ID]**

### **Step 06: Launch Frontend EC2 (Public Subnet)**
EC2 → Launch Instance:
├── Name: Frontend-Public
├── AMI: Ubuntu 24.04 LTS
├── Instance Type: t3.micro
├── Key Pair: saroj-vpc-key.pem (Download)
├── Network: Custom VPC → Public-Subnet-Frontend
├── Auto-assign Public IP: ENABLE ✓
├── Security Group: SSH (22) + HTTP (80)

** #06: Frontend-Public running → Public IP ✓ → Public-Subnet-Frontend**

### **Step 07: Launch Database EC2 (Private Subnet)**
Same settings → Name: Database-Private
├── Network: Private-Subnet-DB
├── Auto-assign Public IP: DISABLE ✗

** #07: Database-Private running → Private IP only → Private-Subnet-DB**

### **Step 08: Test Frontend Internet Access**
SSH Frontend-Public:
ssh -i saroj-vpc-key.pem ubuntu@[Public-IP]
ping -c 4 google.com
curl ifconfig.me # Shows Public IP

### **Step 9: Final Architecture Verification**
AWS Console → VPC → MyApp-VPC → Diagram view


** #15: Complete VPC → Public/Private → IGW → Route Tables**

## **📊 VPC Configuration Summary**
| Component | Name | CIDR | AZ | Route Table | Public IP | Purpose |
|-----------|------|------|----|-------------|-----------|---------|
| VPC | MyApp-VPC | 10.0.0.0/16 | - | - | - | Container |
| Public Subnet | Public-Subnet-Frontend | 10.0.1.0/24 | 1a | Public-RouteTable ✓ | ✓ | Frontend EC2 |
| Private Subnet | Private-Subnet-DB | 10.0.2.0/24 | 1a | Private-RouteTable | ✗ | Database EC2 |
| IGW | MyApp-IGW | - | - | Public-RouteTable | - | Internet |
| Frontend EC2 | Frontend-Public | 10.0.1.x | 1a | IGW Access ✓ | ✓ | Web Server |
| DB EC2 | Database-Private | 10.0.2.x | 1a | No IGW | ✗ | Database |
