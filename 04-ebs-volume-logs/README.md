# 🟢 04 EBS Production Volume Mount (/logs)

**100GB gp3 EBS → Partition → ext4 → fstab UUID → Permanent Logs Storage**

## 🎯 Architecture Overview
AWS Console → EC2 (ap-south-1a) → Create 100GB gp3 → Attach → SSH → fdisk /dev/nvme1n1 → mkfs.ext4 → /logs → blkid UUID → /etc/fstab → mount -a

## **📋 COMPLETE PRODUCTION STEPS**

### **Step 1: Launch EC2 Instance (AWS Console)**
EC2 → Launch Instance:
├── Name: ebs-logs-demo
├── AMI: Ubuntu Server 24.04 LTS
├── Instance Type: t3.micro
├── Key Pair: Create new → "saroj-ebs-logs.pem" → DOWNLOAD
├── VPC: Default → Note AZ (ap-south-1a)
├── Storage: 20GB gp3 (root only)
├── Security Group: SSH (22) → My IP / 0.0.0.0/0

### **Step 2: Create 100GB gp3 EBS Volume**
EC2 → Volumes → Create Volume:
├── Availability Zone: ap-south-1a (MATCH instance AZ)
├── Volume type: gp3
├── Size: 100 GiB
├── IOPS: 3000
├── Throughput: 125 MiB/s

### **Step 3: Attach Volume to Instance**
Volumes → [vol-xxx] → Actions → Attach volume:
├── Instance: ebs-logs-demo
├── Device: /dev/xvdfbd (Linux: /dev/nvme1n1)

### **Step 4: SSH + Verify Volume**

ssh -i "saroj-ebs-logs.pem" ubuntu@[PUBLIC-IP]
lsblk
# Expected:
# NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
# nvme1n1   259:0    0  100G  0 disk 


Step 5: Partition Volume (fdisk)

sudo fdisk /dev/nvme1n1
# EXACT keystrokes:
# n → [Enter] → p → [Enter] → 1 → [Enter] → +50G → w

Step 6: Format Filesystem

sudo mkfs -t ext4 /dev/nvme1n1p1
sudo blkid /dev/nvme1n1p1
# Copy UUID: UUID="abcd-1234-..."

Step 7: Temporary Mount

sudo mkdir /logs
sudo mount /dev/nvme1n1p1 /logs
df -hT /logs

Step 8: Permanent Mount (fstab UUID)

sudo vim /etc/fstab
# Add this EXACT line (YOUR UUID):
UUID=abcd-1234-5678-90ef-ghij-klmn-opqr-stuv /logs ext4 defaults,nofail 0 2

# Test (CRITICAL)
sudo mount -av

📊 EBS Production Specs
Property	Value
Volume Type	gp3
Capacity	100GB
IOPS	3000
Partition	/dev/nvme1n1p1
Size Used	50GB
Filesystem	ext4
Mount Point	/logs
Persistent	fstab UUID


Production Benefits

💾 50GB dedicated /logs (separate from root)
🔄 Survives reboot (fstab UUID)
⚡ gp3 3000 IOPS performance
📈 Easy resize/snapshot/backup
🛡️ nofail prevents boot failure
Status: 🟢 EBS 100GB → 50G /logs → Persistent mount LIVE
