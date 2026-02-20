# 🟢 03 Key-Based Authentication Production Setup

**Local ssh-keygen → Server authorized_keys → Passwordless SSH Access**

## 🎯 Architecture Overview
Local Workstation → ssh-keygen (.pem + .pub) → Copy .pub → Server → /home/user/.ssh/authorized_keys
↓
SSH -i private_key user@public_ip ✅

## **📋 COMPLETE PRODUCTION STEPS**

### **PHASE 1: Local Key Generation (locally in cmd)**

# Generate RSA key pair (2048-bit production standard)
ssh-keygen -f ~/.ssh/saroj_key
# Prompts:
# Enter passphrase (optional): [ENTER for none]
# Enter same passphrase: [ENTER]
# Generated:
# ~/.ssh/saroj_key                  ← PRIVATE KEY (.pem equivalent)
# ~/.ssh/saroj_key.pub              ← PUBLIC KEY (send to server)

# Verify keys created
ls -la ~/.ssh/saroj_key*
cat ~/.ssh/saroj_key.pub  # Copy this ENTIRE line

PHASE 2: Server User Setup (Production Server )

# Connect as ubuntu (existing access)
ssh -i "Key_pair" user@public_ip

# Create production user 'saroj'
sudo adduser saroj
# Enter password + details → Complete user creation

# Create SSH directory structure (EXACT permissions)
sudo mkdir -p /home/saroj/.ssh
sudo touch /home/saroj/.ssh/authorized_keys
sudo chmod 700 /home/saroj/.ssh           # drwx------
sudo chmod 600 /home/saroj/.ssh/authorized_keys  # -rw-------

PHASE 3: Deploy Public Key to Server

# Edit authorized_keys (CRITICAL: Paste ENTIRE public key line)
sudo vim /home/saroj/.ssh/authorized_keys
# Press 'i' → Paste: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... saroj@local
# Press ESC → :wq → Enter

# Verify key deployed correctly
sudo cat /home/saroj/.ssh/authorized_keys

# Set CORRECT ownership (SSH rejects wrong owner)
sudo chown -R saroj:saroj /home/saroj

PHASE 4: Production Access Test (Local Workstation)

# Test passwordless SSH (key authentication)
ssh -i saroj_key saroj@public_ip
# Expected: saroj@ip-172-31-47-200:~$  ✅ NO PASSWORD!

# Verify correct user + permissions working
whoami     # saroj
id         # uid=1001(saroj) gid=1001(saroj)
pwd        # /home/saroj


