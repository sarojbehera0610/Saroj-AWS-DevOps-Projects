# 🟢 10 VPC Best Practices + ALB → Private Web Servers (Multi-AZ HA)

**2 Public Subnets + 2 Private Subnets + NAT + ALB(SG-ALB) → Private Web Servers(SG-Web)**

## 🎯 Secure Multi-AZ Architecture
Internet
↓ ALB (Public Subnets 1a+1b, SG-ALB:80)
↓ HTTP:80 (SG-Web allowed)
2x Web Servers (Private Subnets 1a+1b, SG-Web)
↓ NAT Gateway (Outbound only)
↓ Main RT (0.0.0.0/0 → IGW) + Sub-RT (0.0.0.0/0 → NAT)

## **📋 COMPLETE PRODUCTION STEPS **

### **🌐 VPC + Multi-AZ Subnets**

**Step 1: Create VPC Best Practices**
VPC → Create VPC:
├── Name: VPC-Best-Practices
├── CIDR: 10.0.0.0/16

** #1: VPC-Best-Practices 10.0.0.0/16**

**Step 2: Public Subnet 1a**
Subnets → Create:
├── Name: PublicSubnetBestPractices1a
├── AZ: ap-south-1a
├── CIDR: 10.0.0.0/18

** #2: PublicSubnet1a 10.0.0.0/18**

**Step 3: Public Subnet 1b**
Name: PublicSubnetBestPractices1b
├── AZ: ap-south-1b
├── CIDR: 10.0.64.0/18

** #3: PublicSubnet1b 10.0.64.0/18**

**Step 4: Private Subnet 1a**
Name: PrivateSubnetBestPractices1a
├── AZ: ap-south-1a
├── CIDR: 10.0.128.0/18

** #4: PrivateSubnet1a 10.0.128.0/18**

**Step 5: Private Subnet 1b**
Name: PrivateSubnetBestPractices1b
├── AZ: ap-south-1b
├── CIDR: 10.0.192.0/18

** #5: PrivateSubnet1b 10.0.192.0/18**

### **🚪 Internet Gateway + NAT Gateway**

**Step 6: Create & Attach IGW**
IGW → Create → Name: IGW-Best-Practices → Attach VPC-Best-Practices

** #6: IGW-Best-Practices attached**

**Step 7: Main RT → IGW Route**
Route Tables → Main RT → Edit routes:
├── 0.0.0.0/0 → IGW-Best-Practices
├── Rename: Main-RT-Public

** #7: Main RT → 0.0.0.0/0 → igw-[ID]**

**Step 8: Create NAT Gateway**
NAT Gateways → Create:
├── Name: NAT-Best-Practices
├── VPC: VPC-Best-Practices
├── Subnet: PublicSubnetBestPractices1a

** #8: NAT-Best-Practices Available**

**Step 9: Create Sub-RT-NAT + NAT Route**
Route Tables → Create → Name: Sub-RT-NAT → VPC-Best-Practices
Edit routes → 0.0.0.0/0 → NAT-Best-Practices

** #9: Sub-RT-NAT → 0.0.0.0/0 → nat-[ID]**

**Step 10: Sub-RT-NAT → Private Subnets**
Sub-RT-NAT → Edit subnet associations:
├── PrivateSubnetBestPractices1a ✓
├── PrivateSubnetBestPractices1b ✓

** #10: Sub-RT-NAT → 2 Private subnets**

### **🔒 Security Groups (ALB → Web Servers)**

**Step 11: SG-ALB (Public Facing)**
Security Groups → Create:
├── Name: SG-ALB
├── Inbound: HTTP:80 | 0.0.0.0/0

**#11: SG-ALB → HTTP:80 Anywhere**

**Step 12: SG-Web-Server-Private**
Name: SG-Web-Server-Private
├── Inbound: HTTP:80 | Source: SG-ALB (Security Group)

** #12: SG-Web → HTTP:80 | sg-[ALB-ID] ✓**

### **🖥️ Private Web Servers (Multi-AZ)**

**Step 13: Launch WebServer1 (Private 1a)**
EC2 → Launch:
├── Name: WebServer1
├── Ubuntu 24.04 LTS | t3.micro
├── VPC: VPC-Best-Practices → PrivateSubnetBestPractices1a
├── Auto-assign Public IP: DISABLE ✗
├── Security group: SG-Web-Server-Private

** #13: WebServer1 launching**

**Step 14: WebServer1 User Data**
User data:

bash
#!/bin/bash
apt update && apt install nginx -y
echo "<h1>ALB Web Server 1 - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx

** #14: WebServer1 user data**

**Step 15: Launch WebServer2 (Private 1b)**
Name: WebServer2
├── PrivateSubnetBestPractices1b (1b)
├── Same SG + User data: "ALB Web Server 2 - $(hostname)"

** #15: WebServer2 → Private IP 10.0.192.x**

### **⚖️ ALB + Target Group**

**Step 16: Create Target Group TG-Web**
Target Groups → Create:
├── Name: TG-Web
├── Target type: Instances | HTTP:80
├── VPC: VPC-Best-Practices
├── Health check: /

** #16: TG-Web created**

**Step 17: Register Web Servers**
TG-Web → Targets → Register:
├── WebServer1:80 ✓
├── WebServer2:80 ✓


** #17: 2 Web targets → Healthy ✓**

**Step 18: Create ALB**
Load Balancers → ALB:
├── Name: ALB-Best-Practices
├── Internet-facing | Default VPC → NO → VPC-Best-Practices
├── Mappings:
│ ├── AZ 1a → PublicSubnetBestPractices1a ✓
│ └── AZ 1b → PublicSubnetBestPractices1b ✓
├── Security group: SG-ALB
├── Listener: HTTP:80 → Forward to TG-Web

** #18: ALB-Best-Practices creating**

**Step 19: ALB Active + DNS**
Load Balancers → ALB-Best-Practices → DNS name

** #19: ALB Active → DNS: alb-best-[random].elb.ap-south-1.amazonaws.com**

### **🧪 High Availability Testing**

**Step 20: ALB → WebServer1/2 Load Balancing**
Browser → http://ALB-DNS/
Expected: "ALB Web Server 1 - ip-10-0-128-xx"
Refresh → "ALB Web Server 2 - ip-10-0-192-xx"


** #20: ALB DNS → WebServer1 ✓**

**Step 21: Target Health + ALB Monitoring**
TG-Web → Targets → Healthy ✓
ALB → Monitoring → Healthy host count: 2/2


** #21: 2/2 Healthy targets**

**Step 22: Security Verification**
Direct Private IP access → FAIL (No Public IP/SG blocks)
ALB → SUCCESS ✓


** #22: ALB works, direct private IP timeout**

## **📊 VPC Best Practices Summary**
| Component | AZ 1a | AZ 1b | Security | Route Table |
|-----------|-------|-------|----------|-------------|
| **Public Subnet** | 10.0.0.0/18 | 10.0.64.0/18 | SG-ALB:80 | Main-RT (IGW) |
| **Private Subnet** | 10.0.128.0/18 | 10.0.192.0/18 | SG-Web:80←ALB | Sub-RT-NAT |
| **Web Servers** | WebServer1 | WebServer2 | Private only | NAT outbound |
| **ALB** | PublicSubnet1a | PublicSubnet1b | HTTP:80 public | TG-Web 2/2 ✓ |
