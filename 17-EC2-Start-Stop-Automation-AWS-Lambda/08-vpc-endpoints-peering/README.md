# 🌐 AWS VPC Endpoints + Cross-Region VPC Peering (Private → Private Connect)

Connect two **completely private EC2 instances** across different AWS regions — Mumbai and N.Virginia — without any public IPs, using **VPC Endpoints** and **Cross-Region VPC Peering**.

---

## 🗂️ Project Overview

This project demonstrates advanced AWS networking by establishing a **private-to-private connection** between two EC2 instances in different regions. No public IPs are used at any point. Access to the Mumbai instance is achieved via an **EC2 Instance Connect Endpoint**, and cross-region communication is established via **VPC Peering** with precise `/32` route entries.

---

## 🎯 Private-to-Private Architecture

```
      Mumbai (ap-south-1)                N.Virginia (us-east-1)
  ┌──────────────────────────┐       ┌──────────────────────────┐
  │      VPC01-Mumbai        │       │        vpc02-us           │
  │      172.12.0.0/16       │       │       195.15.0.0/16       │
  │                          │       │                          │
  │  ┌────────────────────┐  │       │  ┌────────────────────┐  │
  │  │  Subnet-Private-   │  │       │  │  Subnet-Private-   │  │
  │  │     Mumbai         │  │       │  │       US           │  │
  │  │                    │  │       │  │                    │  │
  │  │ instanceMumbai     │  │       │  │ instanceUSPrivate  │  │
  │  │ Private            │◄─┼───────┼─►│ 195.15.51.64      │  │
  │  │ 172.12.63.169      │  │       │  │ (No Public IP)    │  │
  │  │ (No Public IP)     │  │       │  └────────────────────┘  │
  │  └────────────────────┘  │       └──────────────────────────┘
  │           │              │                    ▲
  │           ▼              │                    │
  │  EC2 Instance Connect    │    VPC Peering (pcx-xxx)
  │     Endpoint             │    Cross-Region Active ✓
  │  (AWS Console Access)    │
  └──────────────────────────┘

  PING: 172.12.63.169 ←──────────────────────► 195.15.51.64
        64 bytes ✓                               64 bytes ✓
```

---

## ✅ Prerequisites

- AWS Account with access to **ap-south-1 (Mumbai)** and **us-east-1 (N.Virginia)**
- Permissions for VPC, EC2, VPC Endpoints, and VPC Peering

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — VPC01-Mumbai Setup (ap-south-1)

### Step 1 — Create VPC01-Mumbai

```
Region: ap-south-1 (Mumbai)
VPC → Create VPC
├── Name: VPC01-Mumbai
└── CIDR: 172.12.0.0/16
```

> ✅ VPC01-Mumbai created — 172.12.0.0/16

---

### Step 2 — Create Private Subnet Mumbai

```
VPC → Subnets → Create Subnet
├── Name: Subnet-Private-Mumbai
├── VPC:  VPC01-Mumbai
├── AZ:   ap-south-1a
└── CIDR: 172.12.0.0/16
```

> ✅ Subnet-Private-Mumbai created — no internet gateway route

---

### Step 3 — Launch Mumbai Private EC2

```
EC2 → Launch Instance
├── Name:            instanceMumbaiPrivate
├── AMI:             Ubuntu 24.04 LTS
├── Instance Type:   t3.micro
├── VPC:             VPC01-Mumbai
├── Subnet:          Subnet-Private-Mumbai
├── Auto-assign IP:  DISABLE ✗  (fully private)
└── Security Group:
    └── Inbound: All ICMP - IPv4 → 0.0.0.0/0
```

> ✅ instanceMumbaiPrivate launched — Private IP: `172.12.63.169`

---

## PHASE 2 — VPC02-US Setup (us-east-1)

### Step 4 — Switch Region → Create VPC02-US

```
⚠️ Switch AWS Console Region to: us-east-1 (N.Virginia)

VPC → Create VPC
├── Name: vpc02-us
└── CIDR: 195.15.0.0/16
```

> ✅ vpc02-us created — 195.15.0.0/16

---

### Step 5 — Create Private Subnet US

```
VPC → Subnets → Create Subnet
├── Name: Subnet-Private-US
├── VPC:  vpc02-us
├── AZ:   us-east-1a
└── CIDR: 195.15.0.0/16
```

> ✅ Subnet-Private-US created

---

### Step 6 — Launch US Private EC2

```
EC2 → Launch Instance
├── Name:            instanceUSPrivate
├── AMI:             Ubuntu 24.04 LTS
├── Instance Type:   t3.micro
├── VPC:             vpc02-us
├── Subnet:          Subnet-Private-US
├── Auto-assign IP:  DISABLE ✗  (fully private)
└── Security Group:
    └── Inbound: All ICMP - IPv4 → 0.0.0.0/0
```

> ✅ instanceUSPrivate launched — Private IP: `195.15.51.64`

---

## PHASE 3 — VPC Endpoint (Mumbai Private Access)

### Step 7 — Create EC2 Instance Connect Endpoint

```
⚠️ Switch back to: ap-south-1 (Mumbai)

VPC → Endpoints → Create Endpoint
├── Name:             endpoint-Mumbai-to-US-privately-connect
├── Service Category: AWS Services
├── Service Type:     EC2 Instance Connect Endpoint
├── VPC:              VPC01-Mumbai
├── Subnet:           Subnet-Private-Mumbai
└── Security Group:   Default
```

> ✅ Endpoint created — Status: Available
> ⏱️ Wait 2–3 minutes for endpoint to become available

---

### Step 8 — Connect to Mumbai Private Instance via Endpoint

```
EC2 → Instances → instanceMumbaiPrivate → Connect
→ EC2 Instance Connect Tab
├── Connection Type: Connect using EC2 Instance Connect Endpoint
├── Endpoint:        endpoint-Mumbai-to-US-privately-connect
├── Username:        ubuntu
→ Connect
```

> ✅ Connected to private instance via AWS Console — no public IP needed!

---

## PHASE 4 — Cross-Region VPC Peering

### Step 9 — Create Peering Connection (Mumbai → US)

```
ap-south-1 → VPC → Peering Connections → Create
├── Name:             Mumbai-to-US-Peering
├── VPC (Requester):  VPC01-Mumbai
├── Account:          My Account
├── Region:           us-east-1 (N.Virginia)
└── VPC ID (Accepter): vpc-[vpc02-us-ID]
→ Create Peering Connection
```

> ✅ Peering Connection created — Status: Pending Acceptance

---

### Step 10 — Accept Peering Request (US Region)

```
⚠️ Switch to: us-east-1 (N.Virginia)

VPC → Peering Connections
→ Select pcx-[ID] → Actions → Accept Request
→ Confirm Accept
```

> ✅ Peering Connection — Status: Active ✓

---

### Step 11 — Add Route in Mumbai → US Private IP

```
⚠️ Switch back to: ap-south-1 (Mumbai)

VPC → Route Tables → VPC01-Mumbai Main RT → Edit Routes
→ Add Route
├── Destination: 195.15.51.64/32   ← ⚠️ /32 NOT /16
└── Target:      pcx-[Peering-ID]
→ Save
```

> ✅ Mumbai RT: 195.15.51.64/32 → pcx-[ID]

---

### Step 12 — Add Route in US → Mumbai Private IP

```
⚠️ Switch to: us-east-1 (N.Virginia)

VPC → Route Tables → vpc02-us Main RT → Edit Routes
→ Add Route
├── Destination: 172.12.63.169/32   ← ⚠️ /32 NOT /16
└── Target:      pcx-[Peering-ID]
→ Save
```

> ✅ US RT: 172.12.63.169/32 → pcx-[ID]

---

## PHASE 5 — Cross-Region Ping Testing

### Step 13 — Test Ping Mumbai → US (Initial Attempt)

```bash
# From instanceMumbaiPrivate terminal via Endpoint
ping -c 10 195.15.51.64
```

> ⚠️ If ping fails — check the troubleshooting table below

---

### Step 14 — Fixed Routes + Successful Ping

After correcting routes to `/32`:

```bash
ping -c 10 195.15.51.64
```

Expected output:

```
PING 195.15.51.64 (195.15.51.64) 56(84) bytes of data.
64 bytes from 195.15.51.64: icmp_seq=1 ttl=64 time=xx ms
64 bytes from 195.15.51.64: icmp_seq=2 ttl=64 time=xx ms
64 bytes from 195.15.51.64: icmp_seq=3 ttl=64 time=xx ms
```

> ✅ Cross-region private ping successful — Mumbai → US ✓

---

### Step 15 — Reverse Ping US → Mumbai

```bash
# From instanceUSPrivate
ping -c 10 172.12.63.169
```

Expected:

```
64 bytes from 172.12.63.169: icmp_seq=1 ttl=64 time=xx ms
```

> ✅ Reverse ping successful — US → Mumbai ✓

---

### Step 16 — Verify VPC Endpoint Status

```
VPC → Endpoints → endpoint-Mumbai-to-US-privately-connect
→ Endpoint Connections Tab → Status: Active ✓
```

> ✅ Endpoint connections confirmed active

---

## ❌ Common Issues + Fixes

| Issue | Symptom | Fix |
|---|---|---|
| **Wrong route prefix** | Ping timeout | Use `/32` (specific host) NOT `/16` (entire VPC) |
| **SG blocks ICMP** | Request timeout | Add **All ICMP - IPv4 → Anywhere** to both instance SGs |
| **Peering not accepted** | Route unreachable | Switch to accepter region and accept the peering request |
| **DNS resolution** | Name resolution fails | Peering → Edit DNS Settings → Enable DNS resolution |
| **Wrong RT associated** | No route to host | Ensure Main RT is associated with the correct private subnet |

> 🚨 **Most Common Mistake:** Using `/16` instead of `/32` in route entries — always use the exact private IP with `/32` for host-specific routes!

---

## 📊 VPC Endpoint + Peering Summary

| Component | Mumbai (ap-south-1) | N.Virginia (us-east-1) |
|---|---|---|
| VPC | VPC01-Mumbai 172.12.0.0/16 | vpc02-us 195.15.0.0/16 |
| Subnet | Subnet-Private-Mumbai | Subnet-Private-US |
| EC2 Private IP | 172.12.63.169 | 195.15.51.64 |
| Public IP | None ✗ | None ✗ |
| Endpoint | EC2 Instance Connect ✓ | — |
| Peering | pcx-[ID] Active ✓ | pcx-[ID] Active ✓ |
| Route Added | → 195.15.51.64/32 | → 172.12.63.169/32 |
| Ping Result | 64 bytes ✓ | 64 bytes ✓ |

---

## 💡 Key Concepts Learned

- **VPC Endpoints** — Access private EC2 instances from AWS Console without public IP or bastion host
- **Cross-Region VPC Peering** — Connect VPCs in different AWS regions privately
- **Host Routes (/32)** — Use specific host routes for peering, not broad CIDR blocks
- **Security Group ICMP Rules** — Must explicitly allow ICMP for ping to work
- **Private-to-Private Architecture** — Full connectivity between instances with zero public exposure

---

## 📁 File Structure

```
.
├── README.md
└── screenshots/
```

---

## 📌 References

- [EC2 Instance Connect Endpoints](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-with-ec2-instance-connect-endpoint.html)
- [VPC Peering Documentation](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html)
- [Cross-Region VPC Peering](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-basics.html)
- [VPC Route Tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
