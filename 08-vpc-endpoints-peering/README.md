# 🟢 08 VPC Endpoints + Cross-Region Peering (Private → Private Connect)

**Mumbai Private EC2 → EC2 Instance Connect Endpoint → Ping US Private 195.15.51.64**

## 🎯 Private-to-Private Architecture
Mumbai (ap-south-1) N.Virginia (us-east-1)
VPC01-Mumbai 172.12.0.0/16 ↔ VPC02-US 195.15.0.0/16
↓ Private Subnet ↓ Private Subnet
Instance-MumbaiPrivate Instance-USPrivate
172.12.63.169 ←→ 195.15.51.64 (PING)
↓ VPC Endpoint (ec2-instance-connect)
Connect via AWS Console Private IP ✓
↓ Peering pcx-xxx + /32 Routes

## **📋 COMPLETE PRODUCTION STEPS **

### **🌍 VPC01-Mumbai (ap-south-1)**

**Step 1: Create VPC01-Mumbai**
VPC → Create VPC:
├── Name: VPC01-Mumbai
├── CIDR: 172.12.0.0/16

**#1: VPC01-Mumbai 172.12.0.0/16**

**Step 2: Create Private Subnet Mumbai**
Subnets → Create:
├── Name: Subnet-Private-Mumbai
├── VPC: VPC01-Mumbai
├── AZ: ap-south-1a
├── CIDR: 172.12.0.0/16

** #2: Subnet-Private-Mumbai**

**Step 3: Launch Mumbai Private EC2**
EC2 → Launch:
├── Name: instanceMumbaiPrivate
├── AMI: Ubuntu 24.04 LTS
├── t3.micro
├── VPC: VPC01-Mumbai → Subnet-Private-Mumbai
├── Auto-assign Public IP: DISABLE ✗
├── SG Rules: All ICMP - IPv4 Anywhere ✓

** #3: instanceMumbaiPrivate → Private IP 172.12.63.169 ✓**

### **🇺🇸 VPC02-US (us-east-1 N. Virginia)**

**Step 4: Switch Region → Create VPC02-US**
Region: us-east-1 → VPC → Create:
├── Name: vpc02-us
├── CIDR: 195.15.0.0/16

** #4: vpc02-us 195.15.0.0/16**

**Step 5: Create Private Subnet US**
Subnets → Create:
├── Name: Subnet-Private-US
├── VPC: vpc02-us
├── AZ: us-east-1a
├── CIDR: 195.15.0.0/16

** #5: Subnet-Private-US**

**Step 6: Launch US Private EC2**
Name: instanceUSPrivate
├── VPC: vpc02-us → Subnet-Private-US
├── Auto-assign Public IP: DISABLE ✗
├── SG: All ICMP - IPv4 Anywhere

** #6: instanceUSPrivate → Private IP 195.15.51.64 ✓**

### **🔌 VPC Endpoint (Mumbai → EC2 Instance Connect)**

**Step 7: Create VPC Endpoint in Mumbai**
Mumbai → VPC → Endpoints → Create endpoint:
├── Name: endpoint-Mumbai-to-US-privately-connect
├── Service category: AWS services
├── Type: EC2 Instance Connect Endpoint
├── VPC: VPC01-Mumbai
├── Subnets: Subnet-Private-Mumbai
├── Security group: Default

** #7: EC2 Instance Connect Endpoint → Available**

**Step 8: Connect Mumbai Private via VPC Endpoint**
EC2 → instanceMumbaiPrivate → Connect → EC2 Instance Connect
├── Endpoint: endpoint-Mumbai-to-US-privately-connect
├── Username: ubuntu → Connect

** #8: AWS Console → Connected via Endpoint ✓**

### **🌉 Cross-Region VPC Peering**

**Step 9: Create Peering Connection (Mumbai → US)**
Mumbai → VPC → Peering Connections → Create:
├── VPC (Requester): VPC01-Mumbai
├── Accepter Region: us-east-1
├── VPC ID: vpc-[vpc02-us-ID]

** #9: pcx-[ID] → Pending acceptance**

**Step 10: Accept Peering (US Region)**
N.Virginia → Peering → Actions → Accept request

** #10: pcx-[ID] → Active ✓**

**Step 11: Mumbai Route Table → Add US Private IP**
Mumbai → Route Tables (VPC01-Mumbai Main) → Edit routes:
├── Destination: 195.15.51.64/32 ← US Private IP
├── Target: pcx-[Peering-ID]

** #11: Mumbai RT → 195.15.51.64/32 → pcx-[ID]**

**Step 12: US Route Table → Add Mumbai Private IP**
N.Virginia → Route Tables (vpc02-us Main) → Edit routes:
├── Destination: 172.12.63.169/32 ← Mumbai Private IP
├── Target: pcx-[Peering-ID]

** #12: US RT → 172.12.63.169/32 → pcx-[ID]**

### **🧪 Cross-Region Ping Test**

**Step 13: Test Ping from Mumbai Private → US Private**
AWS Console → EC2 Instance Connect (Endpoint) → Mumbai Private:
ping -c 10 195.15.51.64

** #13: Ping results (Success/Failure)**

## **❌ PING FAILURE - TOP 5 REASONS & FIXES**

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Route /32 vs /16** | `ping: 195.15.51.64/16` | **USE /32**: `195.15.51.64/32` ✓ |
| **SG Blocks ICMP** | Timeouts | US EC2 SG → **All ICMP IPv4 - Anywhere** ✓ |
| **No Endpoint Policy** | Connect fails | Endpoint → Policy: `ec2-instance-connect.amazonaws.com` full access |
| **Peering DNS Off** | Name resolution | Peering → **Enable DNS resolution** ✓ |
| **Subnet RT Wrong** | No route | **Main RT** associated with Private subnet ✓ |

**🚨 MY ISSUE**: `/16` instead of `/32` → **Change to 195.15.51.64/32**!

## **✅ FIXED Ping Test (Step 14)**

**Step 14: FIXED Routes + Ping Success**
Edit Mumbai RT: 195.15.51.64/32 ✓

Edit US RT: 172.12.63.169/32 ✓

EC2 Connect Endpoint → ping 195.15.51.64

** #14: `64 bytes from 195.15.51.64: icmp_seq=1` ✓**

**Step 15: Reverse Ping US → Mumbai**
N.Virginia → Session Manager/EC2 Connect → ping 172.12.63.169

** #15: US → Mumbai ping ✓**

**Step 16: VPC Endpoint Status + Traffic**
VPC → Endpoints → endpoint-Mumbai-to-US → Endpoint connections

** #16: Endpoint connections → Active**

## **📊 VPC Endpoint + Peering Summary**
| Component | Mumbai | US N.Virginia |
|-----------|--------|---------------|
| VPC | VPC01-Mumbai 172.12.0.0/16 | vpc02-us 195.15.0.0/16 |
| Subnet | Subnet-Private-Mumbai | Subnet-Private-US |
| EC2 Private IP | 172.12.63.169 | 195.15.51.64 |
| Endpoint | EC2 Instance Connect | - |
| Peering | pcx-[ID] Active | pcx-[ID] Active |
| Route | → 195.15.51.64/32 | → 172.12.63.169/32 |
| Ping | ✓ 64 bytes | ✓ 64 bytes |
