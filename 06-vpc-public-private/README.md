# 🏗️ AWS VPC — Public/Private Subnets + IGW + NAT Gateway (2-Tier Architecture)

Build a **production-grade 2-tier VPC architecture** on AWS with a public frontend subnet and a private database subnet — connected via Internet Gateway and NAT Gateway for secure, controlled internet access.

---

## 🗂️ Project Overview

This project implements a classic **2-tier application architecture** inside a custom AWS VPC. The frontend EC2 instance lives in a public subnet with direct internet access, while the database EC2 instance lives in a private subnet with outbound-only internet access via NAT Gateway — exactly how real-world production environments are structured.

---

## 🎯 Architecture

### Phase 1 — Basic VPC + IGW

```
                        Internet
                           │
                           ▼
                      MyApp-IGW
                           │
              ┌────────────┴────────────┐
              │       MyApp-VPC         │
              │      10.0.0.0/16        │
              │                         │
              │  ┌──────────────────┐   │
              │  │  Public Subnet   │   │
              │  │  10.0.1.0/24     │   │
              │  │  ap-south-1a     │   │
              │  │                  │   │
              │  │  Frontend-Public │   │
              │  │  (Public IP ✓)   │   │
              │  └──────────────────┘   │
              │                         │
              │  ┌──────────────────┐   │
              │  │  Private Subnet  │   │
              │  │  10.0.2.0/24     │   │
              │  │  ap-south-1a     │   │
              │  │                  │   │
              │  │  Database-Private│   │
              │  │  (No Public IP)  │   │
              │  └──────────────────┘   │
              └─────────────────────────┘
```

### Phase 2 — With NAT Gateway

```
                        Internet
                           │
                    ┌──────┴──────┐
                    │  MyApp-IGW  │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │       MyApp-VPC         │
              │      10.0.0.0/16        │
              │                         │
              │  ┌──────────────────┐   │
              │  │  Public Subnet   │   │
              │  │  10.0.1.0/24     │   │
              │  │                  │   │
              │  │  Frontend-Public │   │
              │  │  (Direct Internet│   │
              │  │   Access ✓)      │   │
              │  │                  │   │
              │  │  NAT-amazon-     │   │
              │  │  clone-DB        │   │
              │  └────────┬─────────┘   │
              │           │ Outbound    │
              │           │ only        │
              │  ┌────────▼─────────┐   │
              │  │  Private Subnet  │   │
              │  │  10.0.2.0/24     │   │
              │  │                  │   │
              │  │  Database-Private│   │
              │  │  ping 8.8.8.8 ✓  │   │
              │  └──────────────────┘   │
              └─────────────────────────┘
```

---

## ✅ Prerequisites

- AWS Account with VPC and EC2 access
- Region: **ap-south-1 (Mumbai)**
- Key pair downloaded locally (e.g. `saroj-vpc-key.pem`)

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — Custom VPC + Subnets + IGW

### Step 1 — Create Custom VPC

```
VPC → Your VPCs → Create VPC
├── Name:     MyApp-VPC
├── CIDR:     10.0.0.0/16
└── Tenancy:  Default
```

> ✅ MyApp-VPC created — 10.0.0.0/16

---

### Step 2 — Create Public Subnet (Frontend)

```
VPC → Subnets → Create Subnet
├── VPC:   MyApp-VPC
├── Name:  Public-Subnet-Frontend
├── AZ:    ap-south-1a
└── CIDR:  10.0.1.0/24
```

> ✅ Public-Subnet-Frontend created — 10.0.1.0/24

---

### Step 3 — Create Private Subnet (Database)

```
├── Name:  Private-Subnet-DB
├── VPC:   MyApp-VPC
├── AZ:    ap-south-1a
└── CIDR:  10.0.2.0/24
```

> ✅ Private-Subnet-DB created — 10.0.2.0/24

---

### Step 4 — Create and Attach Internet Gateway

```
VPC → Internet Gateways → Create
├── Name: MyApp-IGW
→ Actions → Attach to VPC → MyApp-VPC
```

> ✅ MyApp-IGW — Status: Attached to MyApp-VPC

---

### Step 5 — Configure Public Route Table

```
VPC → Route Tables → Select MyApp-VPC Main RT
→ Rename: Public-RouteTable
→ Edit Routes → Add Route
├── Destination: 0.0.0.0/0
└── Target:      MyApp-IGW
→ Subnet Associations → Edit
└── Public-Subnet-Frontend ✓
```

> ✅ Public-RouteTable: 0.0.0.0/0 → IGW (Full internet access)

---

### Step 6 — Launch Frontend EC2 (Public Subnet)

```
EC2 → Launch Instance
├── Name:            Frontend-Public
├── AMI:             Ubuntu 24.04 LTS
├── Instance Type:   t3.micro
├── Key Pair:        saroj-vpc-key.pem  ← Download and save locally
├── VPC:             MyApp-VPC
├── Subnet:          Public-Subnet-Frontend
├── Auto-assign IP:  ENABLE ✓
└── Security Group:
    ├── SSH  → Port 22 → 0.0.0.0/0
    └── HTTP → Port 80 → 0.0.0.0/0
```

> ✅ Frontend-Public running — Public IP assigned in Public-Subnet-Frontend

---

### Step 7 — Launch Database EC2 (Private Subnet)

```
EC2 → Launch Instance
├── Name:            Database-Private
├── AMI:             Ubuntu 24.04 LTS
├── Instance Type:   t3.micro
├── Key Pair:        saroj-vpc-key.pem
├── VPC:             MyApp-VPC
├── Subnet:          Private-Subnet-DB
├── Auto-assign IP:  DISABLE ✗  (private only)
└── Security Group:
    └── SSH → Port 22 → 0.0.0.0/0
```

> ✅ Database-Private running — Private IP only in Private-Subnet-DB

---

### Step 8 — Test Frontend Internet Access

```bash
# SSH into Frontend EC2
ssh -i saroj-vpc-key.pem ubuntu@[Frontend-Public-IP]

# Test internet connectivity
ping -c 4 google.com

# Check public IP
curl ifconfig.me
```

Expected:
```
64 bytes from google.com: icmp_seq=1 ✓
[Your Public IP shown]
```

> ✅ Frontend EC2 has full internet access via IGW

---

### Step 9 — Verify VPC Architecture

```
AWS Console → VPC → MyApp-VPC → Resource Map
```

Confirm:
```
MyApp-VPC
├── Public-Subnet-Frontend  → Public-RouteTable → IGW ✓
└── Private-Subnet-DB       → Main RT (no IGW) ✓
```

> ✅ 2-Tier VPC architecture confirmed

---

## PHASE 2 — NAT Gateway for Private Subnet Internet Access

### Step 10 — Create NAT Gateway

```
VPC → NAT Gateways → Create NAT Gateway
├── Name:       NAT-amazon-clone-DB
├── Subnet:     Public-Subnet-Frontend  ← ⚠️ Must be in PUBLIC subnet
└── Elastic IP: Allocate Elastic IP → Create
```

> ✅ NAT-amazon-clone-DB — Status: Available
> ⏱️ Wait 1–2 minutes for NAT Gateway to become available

---

### Step 11 — Create Private DB Route Table

```
VPC → Route Tables → Create Route Table
├── Name: RT-02-amazon-clone-DB
└── VPC:  MyApp-VPC
```

> ✅ RT-02-amazon-clone-DB created

---

### Step 12 — Add NAT Route to Private Route Table

```
RT-02-amazon-clone-DB → Routes → Edit Routes
→ Add Route
├── Destination: 0.0.0.0/0
└── Target:      NAT Gateway → NAT-amazon-clone-DB
→ Save
```

> ✅ RT-02: 0.0.0.0/0 → NAT-amazon-clone-DB (Outbound only)

---

### Step 13 — Associate Private Route Table with DB Subnet

```
RT-02-amazon-clone-DB → Subnet Associations → Edit
└── Private-Subnet-DB ✓ → Save
```

> ✅ Private-Subnet-DB now routes outbound traffic via NAT Gateway

---

### Step 14 — Copy SSH Key to Frontend EC2

```bash
# Run from your LOCAL terminal
scp -i saroj-vpc-key.pem saroj-vpc-key.pem \
  ubuntu@[Frontend-Public-IP]:~/.ssh/
```

Expected:
```
saroj-vpc-key.pem    100%  → transfer complete ✓
```

> ✅ SSH key copied to Frontend EC2

---

### Step 15 — SSH into Private DB + Test NAT Internet

```bash
# Step 1: SSH into Frontend EC2
ssh -i saroj-vpc-key.pem ubuntu@[Frontend-Public-IP]

# Step 2: Fix key permissions
chmod 600 ~/.ssh/saroj-vpc-key.pem

# Step 3: SSH from Frontend → Private DB
ssh -i ~/.ssh/saroj-vpc-key.pem ubuntu@10.0.2.x

# Step 4: Test outbound internet via NAT
ping -c 10 8.8.8.8
```

Expected output:

```
64 bytes from 8.8.8.8: icmp_seq=1 ttl=64 time=xx ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=64 time=xx ms

--- 8.8.8.8 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss ✓
```

> ✅ Private DB EC2 has outbound internet access via NAT — no public IP exposed!

---

## 📊 VPC Configuration Summary

| Component | Name | CIDR | AZ | Route Table | Public IP | Purpose |
|---|---|---|---|---|---|---|
| VPC | MyApp-VPC | 10.0.0.0/16 | — | — | — | Network container |
| Public Subnet | Public-Subnet-Frontend | 10.0.1.0/24 | 1a | Public-RouteTable → IGW | ✅ | Frontend EC2 |
| Private Subnet | Private-Subnet-DB | 10.0.2.0/24 | 1a | RT-02 → NAT | ❌ | Database EC2 |
| IGW | MyApp-IGW | — | — | Public-RouteTable | — | Internet access |
| NAT Gateway | NAT-amazon-clone-DB | — | 1a (Public) | — | EIP | Private outbound |
| Frontend EC2 | Frontend-Public | 10.0.1.x | 1a | IGW direct ✓ | ✅ | Web server |
| Database EC2 | Database-Private | 10.0.2.x | 1a | NAT outbound ✓ | ❌ | Database |

---

## 🔧 Troubleshooting

| Issue | Symptom | Fix |
|---|---|---|
| Frontend no internet | Ping fails | Check Public-RouteTable has 0.0.0.0/0 → IGW |
| Private DB no outbound | Ping 8.8.8.8 fails | Check RT-02 has 0.0.0.0/0 → NAT and is associated to Private-Subnet-DB |
| NAT Gateway not working | Timeout | Ensure NAT Gateway is in PUBLIC subnet with EIP allocated |
| SSH to private fails | Connection refused | SCP the key to Frontend first, then SSH hop through Frontend |
| SCP permission denied | Auth error | Run `chmod 400 saroj-vpc-key.pem` locally before SCP |

---

## 💡 Key Concepts Learned

- **Custom VPC** — Isolated network with full control over subnets, routing, and security
- **Public vs Private Subnets** — Public has IGW route; private has no direct internet route
- **Internet Gateway (IGW)** — Enables two-way internet access for public subnet resources
- **NAT Gateway** — Allows private instances to reach internet outbound without exposing them inbound
- **SSH Jump Host** — Use public EC2 as bastion to access private EC2 instances
- **Route Tables** — Control traffic flow within and outside the VPC

---

## 📁 File Structure

```
.
├── README.md
└── screenshots/
```

---

## 📌 References

- [VPC Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [Internet Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)
- [NAT Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
- [Public and Private Subnets](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Scenario2.html)
