# 🌍 AWS VPC Peering — Cross-Region (Mumbai ↔ N. Virginia)

Establish a **cross-region VPC peering connection** between Mumbai (ap-south-1) and N.Virginia (us-east-1) — enabling private EC2 instances in different regions to communicate with each other without traversing the public internet.

---

## 🗂️ Project Overview

This project demonstrates how to set up **cross-region VPC peering** on AWS. A public EC2 instance in Mumbai acts as a jump host to reach a private EC2 instance, which then pings a completely private EC2 instance in N.Virginia — all through a secure VPC peering connection with precise `/32` host routes.

---

## 🎯 Cross-Region Architecture

```
      Local Machine
           │
           │ SCP + SSH
           ▼
  ┌─────────────────────────────────────┐
  │         VPC-A — Mumbai              │
  │         ap-south-1                  │
  │         172.15.0.0/16               │
  │                                     │
  │  ┌──────────────────┐               │
  │  │  Public Subnet   │               │
  │  │  172.15.0.0/17   │               │
  │  │                  │               │
  │  │ Instance01-      │               │
  │  │ Public-VPC-Mumbai│               │
  │  │ (Nginx + SSH)    │               │
  │  └────────┬─────────┘               │
  │           │ SSH jump                │
  │  ┌────────▼─────────┐               │
  │  │  Private Subnet  │               │
  │  │  172.15.128.0/17 │               │
  │  │                  │               │
  │  │ Instance02-      │               │
  │  │ Private-VPC-     │               │
  │  │ Mumbai           │               │
  │  │ 172.15.156.82    │               │
  │  └────────┬─────────┘               │
  └───────────┼─────────────────────────┘
              │
              │ VPC Peering (pcx-xxx)
              │ Cross-Region Active ✓
              │
  ┌───────────┼─────────────────────────┐
  │           ▼                         │
  │  ┌─────────────────┐                │
  │  │  Private Subnet │                │
  │  │  175.12.0.0/16  │                │
  │  │                 │                │
  │  │ Instance01-     │                │
  │  │ Private-VPC-B   │                │
  │  │ 175.12.246.82   │                │
  │  │ ← PING ✓        │                │
  │  └─────────────────┘                │
  │         VPC-B — N.Virginia          │
  │         us-east-1                   │
  │         175.12.0.0/16               │
  └─────────────────────────────────────┘

  PING: 172.15.156.82 ──────────────────► 175.12.246.82
        VPC-A Private                      VPC-B Private
        64 bytes ✓   0% packet loss        64 bytes ✓
```

---

## ✅ Prerequisites

- AWS Account with access to **ap-south-1 (Mumbai)** and **us-east-1 (N.Virginia)**
- Key pair downloaded locally (e.g. `saroj-peering-key.pem`)
- Local terminal with `ssh` and `scp` available

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — VPC-A Mumbai Setup (ap-south-1)

### Step 1 — Create VPC-A

```
Region: ap-south-1 (Mumbai)
VPC → Create VPC
├── Name: VPC-A
└── CIDR: 172.15.0.0/16
```

> ✅ VPC-A created — 172.15.0.0/16

---

### Step 2 — Create VPC-A Public Subnet

```
VPC → Subnets → Create Subnet
├── Name: Subnet-01-VPC-A-Public
├── VPC:  VPC-A
├── AZ:   ap-south-1a
└── CIDR: 172.15.0.0/17
```

> ✅ Subnet-01-VPC-A-Public created — 172.15.0.0/17

---

### Step 3 — Create VPC-A Private Subnet

```
├── Name: Subnet-02-VPC-A-Private
├── VPC:  VPC-A
├── AZ:   ap-south-1a
└── CIDR: 172.15.128.0/17
```

> ✅ Subnet-02-VPC-A-Private created — 172.15.128.0/17

---

### Step 4 — Create and Attach Internet Gateway

```
VPC → Internet Gateways → Create
├── Name: IGW-VPC-A
→ Actions → Attach to VPC → VPC-A
```

> ✅ IGW-VPC-A attached to VPC-A

---

### Step 5 — Configure Route Table for Public Internet Access

```
VPC → Route Tables → VPC-A Main RT → Edit Routes
→ Add Route
├── Destination: 0.0.0.0/0
└── Target:      IGW-VPC-A
→ Save
```

> ✅ VPC-A RT: 0.0.0.0/0 → IGW-VPC-A (Public internet access)

---

### Step 6 — Launch VPC-A Public EC2

```
EC2 → Launch Instance
├── Name:            Instance01-Public-VPC-Mumbai
├── AMI:             Ubuntu 24.04 LTS
├── Instance Type:   t3.micro
├── Key Pair:        saroj-peering-key.pem  ← Download and save locally
├── VPC:             VPC-A
├── Subnet:          Subnet-01-VPC-A-Public
└── Auto-assign IP:  ENABLE ✓
```

> ✅ Instance01-Public-VPC-Mumbai running — Public IP assigned

---

### Step 7 — Add User Data + Security Group Rules

**User Data:**

```bash
#!/bin/bash
apt update && apt install nginx -y
echo "<h1>Welcome VPC-A</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx
```

**Security Group Inbound Rules:**

```
├── SSH   → Port 22  → 0.0.0.0/0
├── HTTP  → Port 80  → 0.0.0.0/0
└── ICMP  → All IPv4 → 0.0.0.0/0
```

> ✅ Nginx running — verify: `http://<Public-IP>` → "Welcome VPC-A"

---

### Step 8 — Launch VPC-A Private EC2

```
EC2 → Launch Instance
├── Name:            Instance02-Private-VPC-Mumbai
├── AMI:             Ubuntu 24.04 LTS
├── Instance Type:   t3.micro
├── VPC:             VPC-A
├── Subnet:          Subnet-02-VPC-A-Private
├── Auto-assign IP:  DISABLE ✗  (private only)
└── Security Group:
    ├── SSH  → Port 22  → 0.0.0.0/0
    └── ICMP → All IPv4 → 0.0.0.0/0
```

> ✅ Instance02-Private-VPC-Mumbai launched — Private IP: `172.15.156.82`

---

## PHASE 2 — VPC-B N.Virginia Setup (us-east-1)

### Step 9 — Switch Region → Create VPC-B

```
⚠️ Switch AWS Console Region to: us-east-1 (N.Virginia)

VPC → Create VPC
├── Name: VPC-B
└── CIDR: 175.12.0.0/16
```

> ✅ VPC-B created — 175.12.0.0/16

---

### Step 10 — Create VPC-B Private Subnet

```
VPC → Subnets → Create Subnet
├── Name: Subnet-01-VPC-B-Private
├── VPC:  VPC-B
├── AZ:   us-east-1a
└── CIDR: 175.12.0.0/16
```

> ✅ Subnet-01-VPC-B-Private created

---

### Step 11 — Associate VPC-B Route Table with Private Subnet

```
VPC → Route Tables → VPC-B Main RT
→ Subnet Associations → Edit
└── Subnet-01-VPC-B-Private ✓ → Save
```

> ✅ VPC-B Main RT associated with private subnet

---

### Step 12 — Launch VPC-B Private EC2

```
EC2 → Launch Instance
├── Name:            Instance01-Private-VPC-B
├── AMI:             Ubuntu 24.04 LTS
├── Instance Type:   t3.micro
├── VPC:             VPC-B
├── Subnet:          Subnet-01-VPC-B-Private
├── Auto-assign IP:  DISABLE ✗  (private only)
└── Security Group:
    ├── SSH  → Port 22  → 0.0.0.0/0
    └── ICMP → All IPv4 → 0.0.0.0/0
```

> ✅ Instance01-Private-VPC-B launched — Private IP: `175.12.246.82`

---

## PHASE 3 — Cross-Region VPC Peering

### Step 13 — Create Peering Connection (Mumbai → N.Virginia)

```
⚠️ Switch back to: ap-south-1 (Mumbai)

VPC → Peering Connections → Create Peering Connection
├── Name:             Mumbai-to-Virginia-Peering
├── VPC (Requester):  vpc-[VPC-A-ID]
├── Account:          My Account
├── Region:           us-east-1 (N.Virginia)
└── VPC (Accepter):   vpc-[VPC-B-ID]
→ Create Peering Connection
```

> ✅ Peering Connection created — Status: Pending Acceptance

---

### Step 14 — Accept Peering Request (N.Virginia)

```
⚠️ Switch to: us-east-1 (N.Virginia)

VPC → Peering Connections
→ Select pcx-[ID] → Actions → Accept Request → Confirm
```

> ✅ Peering Connection — Status: Active ✓

---

## PHASE 4 — Configure Route Tables

### Step 15 — VPC-A Route Table → Add VPC-B Private IP

```
⚠️ Switch back to: ap-south-1 (Mumbai)

VPC → Route Tables → VPC-A Main RT → Edit Routes
→ Add Route
├── Destination: 175.12.246.82/32   ← ⚠️ /32 NOT /16
└── Target:      pcx-[Peering-ID]
→ Save
```

> ✅ VPC-A RT: 175.12.246.82/32 → pcx-[ID]

---

### Step 16 — VPC-B Route Table → Add VPC-A Private IP

```
⚠️ Switch to: us-east-1 (N.Virginia)

VPC → Route Tables → VPC-B Main RT → Edit Routes
→ Add Route
├── Destination: 172.15.156.82/32   ← ⚠️ /32 NOT /16
└── Target:      pcx-[Peering-ID]
→ Save
```

> ✅ VPC-B RT: 172.15.156.82/32 → pcx-[ID]

---

## PHASE 5 — SSH Access Chain + Cross-Region Ping

### Step 17 — SCP Key from Local → VPC-A Public EC2

```bash
# Run from your LOCAL terminal
scp -i saroj-peering-key.pem saroj-peering-key.pem \
  ubuntu@[VPC-A-Public-IP]:~/.ssh/
```

Expected:
```
saroj-peering-key.pem    100%  ...  → transfer complete
```

> ✅ Key copied to VPC-A Public EC2

---

### Step 18 — SSH into VPC-A Public EC2

```bash
ssh -i saroj-peering-key.pem ubuntu@[VPC-A-Public-IP]
```

> ✅ Connected to Instance01-Public-VPC-Mumbai

---

### Step 19 — SSH from VPC-A Public → VPC-A Private

```bash
# From inside VPC-A Public EC2
chmod 600 ~/.ssh/saroj-peering-key.pem
ssh -i ~/.ssh/saroj-peering-key.pem ubuntu@172.15.156.82
```

> ✅ Connected to Instance02-Private-VPC-Mumbai (172.15.156.82)

---

### Step 20 — Ping VPC-B Private from VPC-A Private

```bash
# From inside VPC-A Private EC2 (172.15.156.82)
ping -c 10 175.12.246.82
```

Expected output:

```
PING 175.12.246.82 (175.12.246.82) 56(84) bytes of data.
64 bytes from 175.12.246.82: icmp_seq=1 ttl=64 time=xx ms
64 bytes from 175.12.246.82: icmp_seq=2 ttl=64 time=xx ms
64 bytes from 175.12.246.82: icmp_seq=3 ttl=64 time=xx ms

--- 175.12.246.82 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss
```

> ✅ Cross-region private ping successful — 0% packet loss 🎉

---

## 📊 VPC Peering Summary

| Component | VPC-A Mumbai | VPC-B N.Virginia |
|---|---|---|
| Region | ap-south-1 | us-east-1 |
| VPC CIDR | 172.15.0.0/16 | 175.12.0.0/16 |
| Public EC2 | 172.15.0.x (Nginx) | — |
| Private EC2 | 172.15.156.82 | 175.12.246.82 |
| Public IP | ✅ Yes (jump host) | ❌ None |
| Peering | pcx-[ID] Active ✓ | pcx-[ID] Active ✓ |
| Route Added | → 175.12.246.82/32 | → 172.15.156.82/32 |
| Ping Result | 64 bytes ✓ | 64 bytes ✓ |

---

## 🔧 Troubleshooting

| Issue | Symptom | Fix |
|---|---|---|
| **Wrong route prefix** | Ping timeout | Use `/32` (host route) NOT `/16` (VPC CIDR) |
| **ICMP blocked** | Request timeout | Add **All ICMP - IPv4 → Anywhere** to both SGs |
| **Peering not accepted** | Route unreachable | Switch to us-east-1 and accept the peering request |
| **SCP fails** | Permission denied | Ensure key file permissions: `chmod 400 saroj-peering-key.pem` |
| **SSH to private fails** | Connection refused | Ensure key was copied via SCP to public instance first |
| **Peering pending** | Can't add routes | Must accept peering before adding routes |

---

## 💡 Key Concepts Learned

- **Cross-Region VPC Peering** — Connect VPCs across different AWS regions privately
- **SSH Jump Host** — Use a public EC2 as a bastion to reach private instances
- **SCP File Transfer** — Securely copy SSH keys across instances
- **Host Routes (/32)** — Use specific IP routes for peering, not broad VPC CIDRs
- **Security Group ICMP** — Must explicitly allow ICMP traffic for ping to work
- **Multi-Region Architecture** — Resources in Mumbai and N.Virginia communicating privately

---

## 📁 File Structure

```
.
├── README.md
└── screenshots/
```

---

## 📌 References

- [VPC Peering Documentation](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html)
- [Cross-Region VPC Peering](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-basics.html)
- [SSH Bastion Host Pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/access-a-bastion-host-by-using-session-manager-and-amazon-ec2-instance-connect.html)
- [VPC Route Tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
