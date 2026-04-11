# 🗂️ AWS EFS — Multi-AZ Production Shared Storage (NFS Mount + fstab)

Set up **Amazon Elastic File System (EFS)** shared across two EC2 instances in different Availability Zones — files written on one instance instantly appear on the other through NFS mount.

---

## 🗂️ Project Overview

This project demonstrates how to configure **Amazon EFS** as a shared, persistent storage layer across multiple EC2 instances in different Availability Zones. This is the standard pattern used in production for shared application files, configuration, media storage, and more.

---

## 🎯 Multi-AZ Architecture

```
        ap-south-1a                        ap-south-1b
  ┌──────────────────┐              ┌──────────────────┐
  │     efs-1        │              │     efs-2        │
  │  EC2 Instance    │              │  EC2 Instance    │
  │  (Ubuntu 24.04)  │              │  (Ubuntu 24.04)  │
  │                  │              │                  │
  │  /efs mounted ✓  │              │  /efs mounted ✓  │
  └────────┬─────────┘              └────────┬─────────┘
           │                                 │
           │     NFS Port 2049               │
           │   (efs-security-group)          │
           └──────────────┬──────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │      EFS-server       │
              │  (Amazon EFS)         │
              │  fs-[ID]              │
              │  Multi-AZ ✓           │
              │  ap-south-1a ✓        │
              │  ap-south-1b ✓        │
              └───────────────────────┘

  Write file on efs-1 ──────────────────► Instantly visible on efs-2 ✓
```

---

## ✅ Prerequisites

- AWS Account with EC2 and EFS access
- Region: **ap-south-1 (Mumbai)**
- Key pair downloaded locally (e.g. `saroj-efs-key.pem`)

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — Security Group + EC2 Instances

### Step 1 — Create EFS Security Group (NFS Port 2049)

```
VPC → Security Groups → Create Security Group
├── Name:        efs-security-group
├── Description: NFS for EFS Multi-AZ
└── Inbound Rules:
    ├── NFS  → Port 2049 → 0.0.0.0/0
    └── SSH  → Port 22   → 0.0.0.0/0
```

> ✅ efs-security-group created — NFS port 2049 open

---

### Step 2 — Launch EC2 Instance in ap-south-1a

```
EC2 → Launch Instance
├── Name:            efs-1
├── AMI:             Ubuntu Server 24.04 LTS
├── Instance Type:   t3.micro
├── Key Pair:        saroj-efs-key.pem  ← Create new and DOWNLOAD
├── VPC:             Default VPC
├── Subnet:          ap-south-1a  ← ⚠️ Select 1a specifically
├── Auto-assign IP:  ENABLE ✓
└── Security Groups: efs-security-group
```

> ✅ efs-1 running — Public IP assigned — AZ: ap-south-1a

---

### Step 3 — Launch EC2 Instance in ap-south-1b

```
EC2 → Launch Instance
├── Name:            efs-2
├── AMI:             Ubuntu Server 24.04 LTS
├── Instance Type:   t3.micro
├── Key Pair:        saroj-efs-key.pem
├── VPC:             Default VPC
├── Subnet:          ap-south-1b  ← ⚠️ DIFFERENT AZ from efs-1
├── Auto-assign IP:  ENABLE ✓
└── Security Groups: efs-security-group
```

> ✅ efs-2 running — Public IP assigned — AZ: ap-south-1b

---

### Step 4 — Install NFS Packages on Both Instances

**On efs-1 (ap-south-1a):**

```bash
ssh -i "saroj-efs-key.pem" ubuntu@[IP-of-efs-1]
sudo apt update && sudo apt install -y nfs-common
```

**On efs-2 (ap-south-1b):**

```bash
ssh -i "saroj-efs-key.pem" ubuntu@[IP-of-efs-2]
sudo apt update && sudo apt install -y nfs-common
```

> ✅ nfs-common installed on both instances — required for NFS mounting

---

## PHASE 2 — Create EFS File System

### Step 5 — Create EFS File System

```
AWS Console → EFS → Create File System
├── Name:               EFS-server
├── VPC:                Default VPC
├── Availability Zones: ap-south-1a + ap-south-1b ✓
├── Mount Targets:      Automatic (one per AZ)
└── Security Groups:    efs-security-group
→ Create
```

> ✅ EFS-server created — fs-[ID] — Multi-AZ mount targets available
> ⏱️ Wait 2–3 minutes for mount targets to become available

**Copy the EFS DNS Name:**
```
fs-[ID].efs.ap-south-1.amazonaws.com
```

---

## PHASE 3 — Mount EFS on Both Instances

### Step 6 — Mount EFS on efs-1 (ap-south-1a)

```bash
# SSH into efs-1
ssh -i "saroj-efs-key.pem" ubuntu@[IP-of-efs-1]

# Create mount directory
sudo mkdir /efs

# Mount EFS
sudo mount -t nfs4 -o nfsvers=4.1 \
  fs-[ID].efs.ap-south-1.amazonaws.com:/ /efs

# Verify mount
df -hT /efs
```

Expected output:
```
Filesystem                                    Type  Size  Used Avail Use% Mounted on
fs-[ID].efs.ap-south-1.amazonaws.com:/  nfs4  8.0E     0  8.0E   0% /efs
```

> ✅ efs-1 → /efs mounted successfully via NFS4

---

### Step 7 — Mount EFS on efs-2 (ap-south-1b)

```bash
# SSH into efs-2
ssh -i "saroj-efs-key.pem" ubuntu@[IP-of-efs-2]

# Create mount directory
sudo mkdir /efs

# Mount EFS (same command — EFS is multi-AZ)
sudo mount -t nfs4 -o nfsvers=4.1 \
  fs-[ID].efs.ap-south-1.amazonaws.com:/ /efs

# Verify mount
df -hT /efs
```

> ✅ efs-2 → /efs mounted successfully via NFS4

---

## PHASE 4 — Test File Sync Across AZs

### Step 8 — Create Files on efs-1 and Verify on efs-2

**On efs-1 (ap-south-1a) — Create files:**

```bash
cd /efs
sudo touch file{1..10}
ls
```

Expected output:
```
file1  file2  file3  file4  file5  file6  file7  file8  file9  file10
```

**On efs-2 (ap-south-1b) — Verify files are visible:**

```bash
ls /efs
```

Expected output:
```
file1  file2  file3  file4  file5  file6  file7  file8  file9  file10
```

> ✅ Files written on efs-1 (ap-south-1a) instantly visible on efs-2 (ap-south-1b) — shared storage confirmed! 🎉

---

## PHASE 5 — Permanent Mount via fstab

### Step 9 — Configure fstab on efs-1

```bash
# SSH into efs-1
ssh -i "saroj-efs-key.pem" ubuntu@[IP-of-efs-1]

# Backup existing fstab
sudo cp /etc/fstab /etc/fstab.bak

# Edit fstab
sudo vim /etc/fstab
```

Add this line at the bottom of the file:

```
fs-[ID].efs.ap-south-1.amazonaws.com:/ /efs nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0
```

Verify the fstab entry works:

```bash
sudo mount -av
```

Expected output:
```
/efs : successfully mounted
```

> ✅ efs-1 fstab configured — EFS will auto-mount on every reboot

---

### Step 10 — Configure fstab on efs-2

```bash
# SSH into efs-2
ssh -i "saroj-efs-key.pem" ubuntu@[IP-of-efs-2]

# Backup existing fstab
sudo cp /etc/fstab /etc/fstab.bak

# Edit fstab
sudo vim /etc/fstab
```

Add the same line:

```
fs-[ID].efs.ap-south-1.amazonaws.com:/ /efs nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0
```

```bash
sudo mount -av
```

> ✅ efs-2 fstab configured — EFS will auto-mount on every reboot

---

## 📊 EFS Configuration Summary

| Component | Details |
|---|---|
| EFS Name | EFS-server |
| EFS ID | fs-[ID] |
| VPC | Default VPC |
| Mount Targets | ap-south-1a + ap-south-1b |
| Protocol | NFS4 (Port 2049) |
| Security Group | efs-security-group |
| Mount Point | /efs |
| Persistence | fstab configured ✓ |

| Instance | AZ | Mount | File Sync |
|---|---|---|---|
| efs-1 | ap-south-1a | /efs ✓ | Write ✓ |
| efs-2 | ap-south-1b | /efs ✓ | Read ✓ |

---

## 🔧 Troubleshooting

| Issue | Symptom | Fix |
|---|---|---|
| Mount fails | `Connection timed out` | Check efs-security-group has NFS port 2049 open |
| Files not syncing | Files missing on 2nd instance | Ensure both instances mounted the **same** EFS DNS name |
| fstab mount fails | `mount -av` error | Check EFS DNS name is correct in fstab entry |
| NFS package missing | `mount: unknown filesystem type 'nfs4'` | Run `sudo apt install nfs-common` |
| Mount target not ready | `No route to host` | Wait 2–3 mins for EFS mount targets to become available |

---

## 💡 Key Concepts Learned

- **Amazon EFS** — Fully managed, elastic NFS file system for Linux workloads
- **Multi-AZ Shared Storage** — Single EFS file system accessible from multiple AZs simultaneously
- **NFS Protocol** — Network File System over port 2049 for shared file access
- **fstab Persistence** — Configure auto-mount so EFS remounts after instance reboot
- **Security Groups for EFS** — NFS port 2049 must be open between EC2 and EFS mount targets

---

## 📁 File Structure

```
.
├── README.md
└── screenshots/
```

---

## 📌 References

- [Amazon EFS Documentation](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html)
- [Mounting EFS on EC2](https://docs.aws.amazon.com/efs/latest/ug/mounting-fs.html)
- [EFS Security Groups](https://docs.aws.amazon.com/efs/latest/ug/network-access.html)
- [fstab Auto-Mount](https://docs.aws.amazon.com/efs/latest/ug/mount-fs-auto-mount-onreboot.html)
