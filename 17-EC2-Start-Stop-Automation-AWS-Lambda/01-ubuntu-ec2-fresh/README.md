# 🚀 AWS EC2 — Production Ubuntu Server Deployment (Nginx + Security Hardening)

Launch and configure a **production-ready Ubuntu EC2 instance** on AWS — with Nginx web server, UFW firewall hardening, and live verification via SSH and browser.

---

## 🗂️ Project Overview

This is the **foundation project** of the AWS DevOps series — launching a production Ubuntu EC2 instance from scratch, hardening it with UFW firewall rules, deploying Nginx as a web server, and verifying the live deployment via SSH and public IP.

---

## 🎯 Architecture Overview

```
         Internet
              │
              │  Port 22 (SSH)
              │  Port 80 (HTTP)
              ▼
  ┌───────────────────────────────────┐
  │   Security Group                  │
  │   ├── SSH  → Port 22 → 0.0.0.0/0 │
  │   └── HTTP → Port 80 → 0.0.0.0/0 │
  └──────────────┬────────────────────┘
                 │
                 ▼
  ┌───────────────────────────────────┐
  │   Ubuntu EC2 Instance             │
  │   Ubuntu Server 24.04 LTS         │
  │   t3.micro                        │
  │                                   │
  │   Public IP:  13.235.245.235      │
  │   Private IP: 172.31.47.200       │
  │                                   │
  │   ├── UFW Firewall ✓              │
  │   ├── Nginx Web Server ✓          │
  │   └── 20GB gp3 EBS ✓             │
  └───────────────────────────────────┘
                 │
                 ▼
  http://13.235.245.235
  "Ubuntu Production Live ✅ 13.235.245.235"
```

---

## 📊 Live Infrastructure Details

| Property | Value |
|---|---|
| AMI | Ubuntu Server 24.04 LTS |
| Instance Type | t3.micro |
| Public IP | 13.235.245.235 |
| Private IP | 172.31.47.200 |
| Storage | 20 GB gp3 EBS |
| Key Pair | saroj-ubuntu-prod-2026.pem |
| Security Group | SSH (22) + HTTP (80) → Anywhere |
| Web Server | Nginx |
| Status | 🟢 3/3 checks passed |

---

## ✅ Prerequisites

- AWS Account with EC2 access
- Region: **ap-south-1 (Mumbai)**
- Local terminal with SSH access

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — Launch EC2 Instance

### Step 1 — Launch Ubuntu EC2 Instance

```
EC2 → Launch Instance
├── Name:            ubuntu-production
├── AMI:             Ubuntu Server 24.04 LTS
├── Instance Type:   t3.micro
├── Key Pair:        saroj-ubuntu-prod-2026.pem  ← Create new and DOWNLOAD
├── Auto-assign IP:  ENABLE ✓
└── Storage:         20 GB gp3
```

**Security Group:**

```
├── SSH  → Port 22  → 0.0.0.0/0
└── HTTP → Port 80  → 0.0.0.0/0
```

> ✅ Instance launching — wait for Status: 3/3 checks passed

---

### Step 2 — Verify Instance is Running

```
EC2 → Instances → ubuntu-production
├── Instance State:  Running ✓
├── Status Checks:   3/3 passed ✓
├── Public IP:       13.235.245.235
└── Private IP:      172.31.47.200
```

> ✅ EC2 instance live — note the Public IP for SSH and browser access

---

## PHASE 2 — SSH Access + Production Hardening

### Step 3 — SSH into the Instance

```bash
ssh -i "saroj-ubuntu-prod-2026.pem" ubuntu@13.235.245.235
```

Expected:
```
ubuntu@ip-172-31-47-200:~$
```

> ✅ Connected to production EC2 instance

---

### Step 4 — Update and Upgrade System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

> ✅ All packages up to date — production security baseline established

---

### Step 5 — Install Nginx and UFW Firewall

```bash
sudo apt install nginx ufw -y
```

> ✅ Nginx web server and UFW firewall installed

---

### Step 6 — Configure UFW Firewall Rules

```bash
# Allow Nginx through firewall (HTTP + HTTPS)
sudo ufw allow 'Nginx Full'

# Allow SSH to prevent lockout
sudo ufw allow ssh

# Enable firewall
sudo ufw --force enable

# Verify rules
sudo ufw status
```

Expected output:
```
Status: active

To                         Action      From
--                         ------      ----
Nginx Full                 ALLOW       Anywhere
22/tcp                     ALLOW       Anywhere
```

> ✅ UFW firewall active — only SSH and Nginx traffic allowed

---

### Step 7 — Start and Enable Nginx

```bash
# Start and enable Nginx on boot
sudo systemctl enable --now nginx

# Verify Nginx is running
sudo systemctl status nginx
```

Expected output:
```
● nginx.service - A high performance web server
   Active: active (running) ✓
```

> ✅ Nginx running and enabled — will auto-start on reboot

---

## PHASE 3 — Deploy Custom Web Page

### Step 8 — Customize the Nginx Default Page

```bash
# View the default Nginx page
sudo cat /var/www/html/index.nginx-debian.html

# Replace with custom production page
echo "<h1>Ubuntu Production Live ✅ 13.235.245.235</h1>" | \
  sudo tee /var/www/html/index.nginx-debian.html
```

> ✅ Custom production page deployed

---

## PHASE 4 — Live Verification

### Step 9 — Verify EC2 Instance Metadata

```bash
# Get IMDSv2 token
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Verify Public IP
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/public-ipv4
```

Expected:
```
13.235.245.235 ✓
```

```bash
# Verify Private IP
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4
```

Expected:
```
172.31.47.200 ✓
```

> ✅ Instance metadata confirmed — Public and Private IPs verified

---

### Step 10 — Verify Web Server in Browser

```
Open browser → http://13.235.245.235
```

Expected:
```
Ubuntu Production Live ✅ 13.235.245.235
```

> ✅ Production web server live and accessible from the internet 🎉

---

## ✅ Final Verification Checklist

| Check | Command | Expected Result |
|---|---|---|
| SSH Access | `ssh -i key.pem ubuntu@13.235.245.235` | `ubuntu@ip-172-31-47-200:~$` ✓ |
| Nginx Status | `sudo systemctl status nginx` | `active (running)` ✓ |
| Firewall Status | `sudo ufw status` | `Status: active` ✓ |
| Public IP | `curl ifconfig.me` | `13.235.245.235` ✓ |
| Web Access | Browser → `http://13.235.245.235` | Custom page visible ✓ |

---

## 🔧 Troubleshooting

| Issue | Symptom | Fix |
|---|---|---|
| SSH connection refused | `Connection refused` | Check Security Group has port 22 open |
| Web page not loading | Browser timeout | Check Security Group has port 80 open |
| Nginx not running | `inactive (dead)` | Run `sudo systemctl start nginx` |
| UFW blocked SSH | Locked out | Use EC2 Instance Connect from AWS Console to re-allow SSH |
| Permission denied (key) | Auth rejected | Run `chmod 400 saroj-ubuntu-prod-2026.pem` locally |

---

## 💡 Key Concepts Learned

- **EC2 Instance Launch** — AMI selection, instance type, storage, and key pair configuration
- **Security Groups** — AWS firewall rules controlling inbound/outbound traffic
- **UFW Firewall** — Linux-level firewall as second layer of security
- **Nginx** — Industry-standard web server setup and configuration
- **IMDSv2** — Secure way to query EC2 instance metadata from inside the instance
- **Production Hardening** — System updates, firewall rules, and auto-start services

---

## 📁 File Structure

```
.
├── README.md
└── screenshots/
```

---

## 📌 References

- [EC2 Getting Started](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html)
- [Ubuntu UFW Firewall](https://help.ubuntu.com/community/UFW)
- [Nginx on Ubuntu](https://nginx.org/en/linux_packages.html#Ubuntu)
- [EC2 Instance Metadata](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)
