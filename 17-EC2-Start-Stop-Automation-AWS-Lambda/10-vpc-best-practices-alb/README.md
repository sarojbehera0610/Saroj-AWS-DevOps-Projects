# 🔒 AWS VPC Best Practices — ALB + Private Web Servers (Multi-AZ HA)

Build a **production-grade secure VPC architecture** on AWS with public/private subnets, NAT Gateway, and an Application Load Balancer routing traffic to private web servers across multiple Availability Zones.

---

## 🗂️ Project Overview

This project implements AWS VPC best practices by placing web servers in **private subnets** — completely inaccessible from the internet directly — and exposing them only through an **Application Load Balancer** in public subnets. This is the standard secure architecture used in real-world production environments.

---

## 🎯 Secure Multi-AZ Architecture

```
                        Internet
                           │
                           ▼
              ┌─────────────────────────┐
              │     ALB-Best-Practices  │
              │   (Internet-facing)     │
              │  SG-ALB: HTTP:80 open   │
              └─────────────────────────┘
                    │              │
                    ▼              ▼
           PublicSubnet1a   PublicSubnet1b
           (10.0.0.0/18)   (10.0.64.0/18)
           ap-south-1a      ap-south-1b
                    │              │
             HTTP:80 (SG-Web allows only SG-ALB)
                    │              │
                    ▼              ▼
          PrivateSubnet1a   PrivateSubnet1b
          (10.0.128.0/18)  (10.0.192.0/18)
          ┌─────────────┐  ┌─────────────┐
          │  WebServer1 │  │  WebServer2 │
          │  No Public  │  │  No Public  │
          │     IP      │  │     IP      │
          └─────────────┘  └─────────────┘
                    │
                    ▼
             NAT Gateway
          (Outbound only)
                    │
                    ▼
           Internet Gateway
```

---

## 🌐 CIDR Block Design

| Subnet | AZ | CIDR | Type |
|---|---|---|---|
| PublicSubnetBestPractices1a | ap-south-1a | 10.0.0.0/18 | Public |
| PublicSubnetBestPractices1b | ap-south-1b | 10.0.64.0/18 | Public |
| PrivateSubnetBestPractices1a | ap-south-1a | 10.0.128.0/18 | Private |
| PrivateSubnetBestPractices1b | ap-south-1b | 10.0.192.0/18 | Private |

---

## ✅ Prerequisites

- AWS Account with VPC, EC2, and ALB access
- Region: **ap-south-1 (Mumbai)**

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — VPC + Multi-AZ Subnets

### Step 1 — Create VPC

```
VPC → Create VPC
├── Name: VPC-Best-Practices
└── CIDR: 10.0.0.0/16
```

> ✅ VPC-Best-Practices created with 10.0.0.0/16

---

### Step 2 — Create Public Subnet 1a

```
VPC → Subnets → Create Subnet
├── Name: PublicSubnetBestPractices1a
├── VPC:  VPC-Best-Practices
├── AZ:   ap-south-1a
└── CIDR: 10.0.0.0/18
```

> ✅ PublicSubnet1a created — 10.0.0.0/18

---

### Step 3 — Create Public Subnet 1b

```
├── Name: PublicSubnetBestPractices1b
├── AZ:   ap-south-1b
└── CIDR: 10.0.64.0/18
```

> ✅ PublicSubnet1b created — 10.0.64.0/18

---

### Step 4 — Create Private Subnet 1a

```
├── Name: PrivateSubnetBestPractices1a
├── AZ:   ap-south-1a
└── CIDR: 10.0.128.0/18
```

> ✅ PrivateSubnet1a created — 10.0.128.0/18

---

### Step 5 — Create Private Subnet 1b

```
├── Name: PrivateSubnetBestPractices1b
├── AZ:   ap-south-1b
└── CIDR: 10.0.192.0/18
```

> ✅ PrivateSubnet1b created — 10.0.192.0/18

---

## PHASE 2 — Internet Gateway + NAT Gateway

### Step 6 — Create and Attach Internet Gateway

```
VPC → Internet Gateways → Create
├── Name: IGW-Best-Practices
└── Action → Attach to VPC → VPC-Best-Practices
```

> ✅ IGW-Best-Practices attached to VPC

---

### Step 7 — Configure Main Route Table for Public Subnets

```
VPC → Route Tables → Select Main RT → Edit Routes
├── Destination: 0.0.0.0/0
├── Target:      IGW-Best-Practices
└── Rename RT:   Main-RT-Public
```

> ✅ Main-RT-Public: 0.0.0.0/0 → IGW (Public internet access)

---

### Step 8 — Create NAT Gateway

```
VPC → NAT Gateways → Create
├── Name:   NAT-Best-Practices
├── Subnet: PublicSubnetBestPractices1a  ← Must be in PUBLIC subnet
└── Elastic IP: Allocate new EIP
```

> ✅ NAT-Best-Practices → Status: Available
> ⏱️ Wait 1–2 minutes for NAT Gateway to become available

---

### Step 9 — Create Private Route Table with NAT Route

```
VPC → Route Tables → Create
├── Name: Sub-RT-NAT
├── VPC:  VPC-Best-Practices
→ Edit Routes → Add Route:
├── Destination: 0.0.0.0/0
└── Target:      NAT-Best-Practices
```

> ✅ Sub-RT-NAT: 0.0.0.0/0 → NAT (Outbound only for private subnets)

---

### Step 10 — Associate Private Subnets to Sub-RT-NAT

```
Sub-RT-NAT → Subnet Associations → Edit
├── PrivateSubnetBestPractices1a ✓
└── PrivateSubnetBestPractices1b ✓
```

> ✅ Both private subnets now route outbound traffic through NAT Gateway

---

## PHASE 3 — Security Groups (ALB → Web Servers)

### Step 11 — Create SG-ALB (Public Facing)

```
EC2 → Security Groups → Create
├── Name:        SG-ALB
├── VPC:         VPC-Best-Practices
└── Inbound Rules:
    └── HTTP → Port 80 → 0.0.0.0/0 (open to internet)
```

> ✅ SG-ALB: HTTP:80 open to anywhere

---

### Step 12 — Create SG-Web-Server-Private

```
Name: SG-Web-Server-Private
├── VPC: VPC-Best-Practices
└── Inbound Rules:
    └── HTTP → Port 80 → Source: SG-ALB (Security Group ID)
```

> ✅ SG-Web: HTTP:80 allowed ONLY from ALB — not from internet directly

---

## PHASE 4 — Launch Private Web Servers

### Step 13 & 14 — Launch WebServer1 (Private Subnet 1a)

```
EC2 → Launch Instance
├── Name:              WebServer1
├── AMI:               Ubuntu 24.04 LTS
├── Instance Type:     t3.micro
├── VPC:               VPC-Best-Practices
├── Subnet:            PrivateSubnetBestPractices1a
├── Auto-assign IP:    DISABLE ✗  (private server — no public IP)
└── Security Group:    SG-Web-Server-Private
```

**User Data:**

```bash
#!/bin/bash
apt update && apt install nginx -y
echo "<h1>ALB Web Server 1 - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx
```

> ✅ WebServer1 launched in private subnet — Private IP: 10.0.128.x

---

### Step 15 — Launch WebServer2 (Private Subnet 1b)

```
├── Name:    WebServer2
├── Subnet:  PrivateSubnetBestPractices1b
└── Same Security Group + User Data (change to "ALB Web Server 2")
```

**User Data:**

```bash
#!/bin/bash
apt update && apt install nginx -y
echo "<h1>ALB Web Server 2 - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx
```

> ✅ WebServer2 launched in private subnet — Private IP: 10.0.192.x

---

## PHASE 5 — ALB + Target Group

### Step 16 — Create Target Group TG-Web

```
EC2 → Target Groups → Create
├── Name:         TG-Web
├── Target Type:  Instances
├── Protocol:     HTTP
├── Port:         80
├── VPC:          VPC-Best-Practices
└── Health Check: /  (HTTP 200-299)
```

> ✅ TG-Web created

---

### Step 17 — Register Web Servers as Targets

```
TG-Web → Targets → Register Targets
├── WebServer1 → Port 80 ✓
└── WebServer2 → Port 80 ✓
→ Include as pending → Register
```

> ✅ 2 targets registered — wait for health checks to pass (Healthy)

---

### Step 18 — Create ALB

```
EC2 → Load Balancers → Create → Application Load Balancer
├── Name:     ALB-Best-Practices
├── Scheme:   Internet-facing
├── VPC:      VPC-Best-Practices
├── Mappings:
│   ├── ap-south-1a → PublicSubnetBestPractices1a ✓
│   └── ap-south-1b → PublicSubnetBestPractices1b ✓
├── Security Group: SG-ALB
└── Listener: HTTP:80 → Forward to TG-Web
```

> ✅ ALB-Best-Practices created — State: Provisioning

---

### Step 19 — Copy ALB DNS Name

```
Load Balancers → ALB-Best-Practices → Description Tab
→ DNS Name: alb-best-[random].elb.ap-south-1.amazonaws.com
```

> ✅ ALB Active — DNS name ready for testing

---

## PHASE 6 — High Availability Testing

### Step 20 — Test ALB Load Balancing

Open browser and hit the ALB DNS:

```
http://alb-best-[random].elb.ap-south-1.amazonaws.com/
```

Expected on first load:
```
ALB Web Server 1 - ip-10-0-128-xx
```

Refresh the page:
```
ALB Web Server 2 - ip-10-0-192-xx
```

> ✅ ALB is load balancing between both private web servers across AZs

---

### Step 21 — Verify Target Health

```
EC2 → Target Groups → TG-Web → Targets
├── WebServer1 → Healthy ✓
└── WebServer2 → Healthy ✓
```

```
ALB → Monitoring → Healthy Host Count: 2/2 ✓
```

> ✅ Both targets healthy across 2 Availability Zones

---

### Step 22 — Security Verification

```
# Try accessing WebServer1 directly via private IP → FAILS ✓
http://10.0.128.x   → Timeout (No public IP, SG blocks direct access)

# Access via ALB DNS → WORKS ✓
http://ALB-DNS/     → "ALB Web Server 1 - ip-10-0-128-xx"
```

> ✅ Security confirmed — web servers are completely private and only reachable through ALB

---

## 📊 VPC Best Practices Summary

| Component | AZ 1a | AZ 1b | Security | Route Table |
|---|---|---|---|---|
| **Public Subnet** | 10.0.0.0/18 | 10.0.64.0/18 | SG-ALB: HTTP:80 | Main-RT → IGW |
| **Private Subnet** | 10.0.128.0/18 | 10.0.192.0/18 | SG-Web: HTTP:80 ← ALB only | Sub-RT-NAT → NAT |
| **Web Servers** | WebServer1 | WebServer2 | No Public IP | NAT outbound only |
| **ALB** | PublicSubnet1a | PublicSubnet1b | HTTP:80 public | TG-Web 2/2 ✓ |

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| ALB health checks failing | Ensure SG-Web allows HTTP:80 from SG-ALB (not 0.0.0.0/0) |
| Web servers not reachable via ALB | Verify ALB is in public subnets, web servers in private subnets |
| NAT Gateway not working | Confirm NAT Gateway is in a PUBLIC subnet with EIP attached |
| Private subnet has no internet | Check Sub-RT-NAT has 0.0.0.0/0 → NAT and is associated to private subnets |
| Direct private IP access works | Check SG-Web inbound source is set to SG-ALB, not 0.0.0.0/0 |

---

## 💡 Key Concepts Learned

- **Public vs Private Subnets** — Public subnets have IGW route; private subnets use NAT
- **NAT Gateway** — Allows private instances outbound internet access without exposing them
- **Security Group Chaining** — SG-Web only allows traffic from SG-ALB, not the open internet
- **Multi-AZ High Availability** — Resources spread across 1a and 1b for fault tolerance
- **ALB as Single Entry Point** — All traffic enters through ALB; web servers stay completely private

---

## 📁 File Structure

```
.
├── README.md
└── screenshots/
```

---

## 📌 References

- [VPC Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html)
- [NAT Gateway Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
- [ALB Documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Security Group Chaining](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
