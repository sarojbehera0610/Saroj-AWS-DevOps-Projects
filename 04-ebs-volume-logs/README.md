# 💾 AWS EBS — Production Volume Mount (/logs) with UUID + fstab

Attach a **100GB gp3 EBS volume** to an EC2 instance, partition it, format with ext4, and configure a **permanent persistent mount** for production log storage using UUID in fstab.

---

## 🗂️ Project Overview

This project demonstrates how to set up a **dedicated EBS volume** for log storage on an EC2 instance — completely separate from the root volume. Using UUID-based fstab configuration ensures the volume remounts automatically after every reboot, making it production-ready and reliable.

---

## 🎯 Architecture Overview

```
AWS Console
     │
     ▼
EC2 Instance (ap-south-1a)          EBS Volume (ap-south-1a)
┌─────────────────────────┐         ┌──────────────────────┐
│      ebs-logs-demo      │         │   100GB gp3 Volume   │
│                         │◄────────│   vol-[ID]           │
│  Root: /dev/nvme0n1     │  Attach │   3000 IOPS          │
│  20GB gp3               │         │   125 MiB/s          │
│                         │         └──────────────────────┘
│  Logs: /dev/nvme1n1p1   │
│  50GB ext4              │
│  Mount: /logs           │
│  fstab UUID ✓           │
└─────────────────────────┘

Flow:
Create Volume → Attach → fdisk → mkfs.ext4 → mkdir /logs
→ mount → blkid UUID → /etc/fstab → mount -av → Persistent ✓
```

---

## 📊 EBS Volume Specifications

| Property | Value |
|---|---|
| Volume Type | gp3 |
| Total Capacity | 100 GB |
| IOPS | 3000 |
| Throughput | 125 MiB/s |
| Partition | /dev/nvme1n1p1 |
| Partition Size | 50 GB |
| Filesystem | ext4 |
| Mount Point | /logs |
| Persistence | fstab UUID ✓ |

---

## ✅ Prerequisites

- AWS Account with EC2 and EBS access
- Region: **ap-south-1 (Mumbai)**
- Key pair downloaded locally (e.g. `saroj-ebs-logs.pem`)

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — Launch EC2 + Create EBS Volume

### Step 1 — Launch EC2 Instance

```
EC2 → Launch Instance
├── Name:            ebs-logs-demo
├── AMI:             Ubuntu Server 24.04 LTS
├── Instance Type:   t3.micro
├── Key Pair:        saroj-ebs-logs.pem  ← Create new and DOWNLOAD
├── VPC:             Default VPC
├── AZ:              ap-south-1a  ← ⚠️ Note this AZ carefully
├── Storage:         20 GB gp3   (root volume only)
└── Security Group:
    └── SSH → Port 22 → 0.0.0.0/0
```

> ✅ ebs-logs-demo running — note the **Availability Zone** (ap-south-1a)

---

### Step 2 — Create 100GB gp3 EBS Volume

```
EC2 → Elastic Block Store → Volumes → Create Volume
├── Volume Type:        gp3
├── Size:               100 GiB
├── IOPS:               3000
├── Throughput:         125 MiB/s
└── Availability Zone:  ap-south-1a  ← ⚠️ MUST match EC2 instance AZ
→ Create Volume
```

> ✅ EBS Volume created — vol-[ID] — Status: Available
> ⚠️ EBS volumes can only attach to EC2 instances in the **same AZ**

---

### Step 3 — Attach Volume to EC2 Instance

```
Volumes → Select vol-[ID] → Actions → Attach Volume
├── Instance: ebs-logs-demo
└── Device:   /dev/xvdf  (appears as /dev/nvme1n1 on Linux)
→ Attach
```

> ✅ Volume attached — Status: In-use

---

## PHASE 2 — Configure Volume via SSH

### Step 4 — SSH into EC2 and Verify Volume

```bash
ssh -i "saroj-ebs-logs.pem" ubuntu@[PUBLIC-IP]
```

Verify the new volume is detected:

```bash
lsblk
```

Expected output:

```
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
nvme0n1     259:0    0    20G  0 disk
└─nvme0n1p1 259:1    0    20G  0 part /
nvme1n1     259:2    0   100G  0 disk         ← New EBS volume (no mount yet)
```

> ✅ nvme1n1 visible — 100G — unpartitioned and unmounted

---

### Step 5 — Partition the Volume (fdisk)

```bash
sudo fdisk /dev/nvme1n1
```

Inside fdisk, enter these keystrokes **exactly**:

```
n        → New partition
[Enter]  → Default (primary)
p        → Primary partition
[Enter]  → Default partition number (1)
[Enter]  → Default first sector
+50G     → Partition size: 50GB
w        → Write and exit
```

Verify the partition was created:

```bash
lsblk
```

Expected:
```
nvme1n1     259:2    0   100G  0 disk
└─nvme1n1p1 259:3    0    50G  0 part   ← Partition created ✓
```

> ✅ /dev/nvme1n1p1 — 50GB partition created

---

### Step 6 — Format Partition with ext4

```bash
sudo mkfs -t ext4 /dev/nvme1n1p1
```

Expected output:
```
mke2fs 1.47.0
Creating filesystem with 13107200 4k blocks
Writing superblocks and filesystem accounting information: done
```

Get the UUID of the partition:

```bash
sudo blkid /dev/nvme1n1p1
```

Expected output:
```
/dev/nvme1n1p1: UUID="abcd-1234-5678-90ef-ghij-klmn-opqr-stuv" TYPE="ext4"
```

> ✅ ext4 filesystem created — **copy the UUID** for fstab configuration

---

### Step 7 — Create Mount Point and Temporary Mount

```bash
# Create the /logs directory
sudo mkdir /logs

# Mount the partition
sudo mount /dev/nvme1n1p1 /logs

# Verify the mount
df -hT /logs
```

Expected output:
```
Filesystem        Type  Size  Used Avail Use% Mounted on
/dev/nvme1n1p1    ext4   49G   24K   47G   1% /logs
```

> ✅ /logs mounted successfully — 50GB available for log storage

---

## PHASE 3 — Permanent Mount via fstab

### Step 8 — Configure fstab with UUID

```bash
# Backup fstab before editing
sudo cp /etc/fstab /etc/fstab.bak

# Open fstab for editing
sudo vim /etc/fstab
```

Add this line at the bottom (replace UUID with YOUR actual UUID from Step 6):

```
UUID=abcd-1234-5678-90ef-ghij-klmn-opqr-stuv /logs ext4 defaults,nofail 0 2
```

**Test the fstab entry:**

```bash
sudo mount -av
```

Expected output:
```
/                 : ignored
/boot/efi         : already mounted
/logs             : successfully mounted  ✓
```

> ✅ fstab configured — /logs will auto-mount on every reboot

---

## ✅ Production Verification

**Verify mount persists:**

```bash
# Write a test log file
echo "EBS /logs mount working - $(date)" | sudo tee /logs/test.log

# Check file exists
cat /logs/test.log

# Verify disk usage
df -hT /logs
```

**Simulate reboot test:**

```bash
sudo reboot
```

After reboot, SSH back in and verify:

```bash
df -hT /logs
# /logs should be automatically mounted ✓
cat /logs/test.log
# File should still exist ✓
```

> ✅ EBS volume persistently mounted at /logs — survives reboots 🎉

---

## 💡 Production Benefits

| Feature | Benefit |
|---|---|
| **Separate /logs volume** | Log growth never fills root volume — prevents system crashes |
| **gp3 3000 IOPS** | High-performance I/O for heavy log write workloads |
| **UUID in fstab** | Device name-independent — survives instance stop/start |
| **nofail option** | Instance boots even if EBS volume is temporarily unavailable |
| **ext4 filesystem** | Industry-standard, reliable, journaled filesystem |
| **Easy snapshot** | Take EBS snapshots for log backup and disaster recovery |
| **Easy resize** | Extend volume size without downtime using `resize2fs` |

---

## 🔧 Troubleshooting

| Issue | Symptom | Fix |
|---|---|---|
| Volume not visible | `lsblk` shows no nvme1n1 | Verify volume is in same AZ as EC2 and is attached |
| fdisk partition not saving | Changes lost | Always press `w` to write before exiting fdisk |
| Mount fails after reboot | `/logs` empty | Check UUID in fstab matches `sudo blkid` output exactly |
| Boot failure after fstab edit | Instance unreachable | `nofail` option prevents this — always use it |
| `df -h` shows wrong size | Partition smaller than expected | Verify `+50G` was entered correctly in fdisk |

---

## 🔧 Useful Commands Reference

```bash
# List all block devices
lsblk

# Show disk usage
df -hT /logs

# Check filesystem UUID
sudo blkid /dev/nvme1n1p1

# Check fstab entries
cat /etc/fstab

# Mount all fstab entries
sudo mount -av

# Unmount volume
sudo umount /logs

# Extend filesystem after resize (no downtime)
sudo resize2fs /dev/nvme1n1p1
```

---

## 📁 File Structure

```
.
├── README.md
└── screenshots/
```

---

## 📌 References

- [Amazon EBS Documentation](https://docs.aws.amazon.com/ebs/latest/userguide/what-is-ebs.html)
- [EBS Volume Types](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html)
- [Make EBS Mount Persistent](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-using-volumes.html)
- [Linux fstab Reference](https://manpages.ubuntu.com/manpages/focal/man5/fstab.5.html)
