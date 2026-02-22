# 🟢 05 EFS Multi-AZ Production Shared Storage

**2 EC2 Instances (ap-south-1a + ap-south-1b) → NFS 2049 → EFS "EFS-server" → Shared /efs → fstab**

## 🎯 Multi-AZ Architecture
EC2-1a (ap-south-1a) ↔ EFS-server (Multi-AZ) ↔ EC2-1b (ap-south-1b)
↓ NFS Port 2049 Security Group ↓
Shared /efs mount → Files sync across AZs ✓

## **📋 COMPLETE PRODUCTION STEPS **

### **Step 1: Create EFS Security Group (NFS 2049)**
VPC → Security Groups → Create Security Group:
├── Name: efs-securuty-group
├── Description: NFS for EFS multi-AZ
├── Inbound Rules:
│ └── Type: NFS | Port: 2049 | Source: 0.0.0.0/0

#1: Security Group created → NFS 2049 rule visible**

### **Step 2: Launch EC2 Instance 1a (ap-south-1a)**
EC2 → Launch Instance:
├── Name: efs-1
├── AMI: Ubuntu Server 24.04 LTS
├── Instance Type: t3.micro
├── Key Pair: Create new "saroj-efs-key.pem" → DOWNLOAD
├── Network: Default VPC → ap-south-1a subnet
├── Security Groups: efs-nfs-2049 + SSH (22)

#2: Instance 1a running → Public IP 1 + AZ ap-south-1a**

### **Step 3: Launch EC2 Instance 1b (ap-south-1b)**
Same as Step 2 → Name: efs-2
├── Network: Default VPC → ap-south-1b subnet (DIFFERENT AZ)

 #3: Instance 1b running → Public IP 2 + AZ ap-south-1b**

### **Step 4: Install NFS Packages (Both Instances)**
**Instance 1a SSH:**

ssh -i "saroj-efs-key.pem" ubuntu@[IP-1a]
sudo apt update && sudo apt install -y nfs-common
Instance 1b SSH:

ssh -i "saroj-efs-key.pem" ubuntu@[IP-1b]
sudo apt update && sudo apt install -y nfs-common

#4: apt install nfs-common success on Instance 1a & 1b

Step 5: Create EFS File System

EFS → Create file system:
├── Name: EFS-server
├── VPC: Default VPC
├── Availability zones: ap-south-1a + ap-south-1b ✓
├── Mount targets: Automatic
├── Security Groups: efs-nfs-2049
#5: EFS "EFS-server" created → fs-[ID] + Multi-AZ

Step 6: Mount EFS on Instance 1a

SSH Instance 1a → Copy EFS mount command:
sudo mkdir /efs
sudo mount -t nfs4 -o nfsvers=4.1 [fs-ID].efs.ap-south-1.amazonaws.com:/ /efs

# Verify mount
df -hT /efs
#6: Instance 1a → df -hT /efs → efs/nfs4 mounted

Step 7: Mount EFS on Instance 1b

SSH Instance 1b → Same mount command:
sudo mkdir /efs
sudo mount -t nfs4 -o nfsvers=4.1 [fs-ID].efs.ap-south-1.amazonaws.com:/ /efs
#7: Instance 1b → df -hT /efs → efs/nfs4 mounted

Step 8: Test File Sync Across AZs

Instance 1a:
touch file{1..10}
ls

Instance 1b:
ls /efs
#8: Instance 1b → File from 1a visible

Step 9: Permanent Mount (fstab) - Instance 1a

# Backup fstab
sudo cp /etc/fstab /etc/fstab.bak

# Edit fstab
sudo vim /etc/fstab
# Add line:
[fs-ID].efs.ap-south-1.amazonaws.com:/ /efs nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0

sudo mount -av
#9: Instance 1a → vim /etc/fstab + mount -av success

Step 10: Permanent Mount (fstab) - Instance 1b

Same fstab entry as Instance 1a
#10: Instance 1b → vim /etc/fstab + mount -av success
