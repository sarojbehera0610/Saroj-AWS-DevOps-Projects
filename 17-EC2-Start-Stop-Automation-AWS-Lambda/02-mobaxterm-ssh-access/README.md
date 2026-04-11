# 🖥️ AWS EC2 — MobaXterm Production SSH Access (GUI Terminal Setup)

Connect to an **Ubuntu EC2 instance** using **MobaXterm** — a powerful GUI SSH terminal — with PEM key authentication for a production-ready remote access setup.

---

## 🗂️ Project Overview

This project demonstrates how to configure **MobaXterm** for SSH access to an AWS EC2 Ubuntu instance using key-based authentication. MobaXterm is widely used in production environments for its built-in SFTP browser, multi-tab sessions, and X11 forwarding capabilities — making it the preferred GUI terminal for DevOps engineers on Windows.

---

## 🎯 Architecture Overview

```
  Local Workstation (Windows)
  ┌─────────────────────────────────────────┐
  │                                         │
  │   MobaXterm                             │
  │   ├── SSH Session                       │
  │   │   ├── Host: 13.203.156.167          │
  │   │   ├── User: ubuntu                  │
  │   │   ├── Port: 22                      │
  │   │   └── Key:  saroj-ubuntu-prod.pem   │
  │   │                                     │
  │   ├── Built-in SFTP Browser ✓           │
  │   ├── Multi-tab Sessions ✓              │
  │   └── X11 Forwarding ✓                 │
  │                                         │
  └───────────────┬─────────────────────────┘
                  │
                  │  SSH Port 22
                  │  PEM Key Auth
                  ▼
  AWS EC2 Instance (ap-south-1)
  ┌─────────────────────────────────────────┐
  │                                         │
  │  ubuntu@ip-172-31-47-200                │
  │  ├── Public IP:  13.203.156.167         │
  │  ├── Private IP: 172.31.12.91           │
  │  ├── User:       ubuntu                 │
  │  └── Nginx:      Active (running) ✓     │
  │                                         │
  └─────────────────────────────────────────┘

  Result: ubuntu@ip-172-31-47-200:~$ ✅
```

---

## ✅ Prerequisites

- **MobaXterm** installed (Personal or Professional Edition)
- AWS EC2 Ubuntu instance running with a **Public IP**
- PEM key file downloaded (e.g. `saroj-ubuntu-prod-2026.pem`)
- Security Group with **SSH port 22** open

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — MobaXterm SSH Session Configuration

### Step 1 — Launch MobaXterm

```
Open MobaXterm (Personal / Professional Edition)
→ Click: Sessions
→ Click: New Session
```

---

### Step 2 — Configure SSH Session

```
Session Type: SSH  ← Select SSH tab at the top

Basic SSH Settings:
├── Remote Host:       13.203.156.167   ← EC2 Public IP
├── Specify Username:  ☑ ubuntu          ← Ubuntu AMI default user
└── Port:              22
```

---

### Step 3 — Configure Advanced SSH Settings (PEM Key)

```
Click: "Advanced SSH settings" tab

├── ☑ Use private key
└── Private key: Browse → saroj-ubuntu-prod-2026.pem

Leave these UNCHECKED:
├── ☐ Jump host
└── ☐ Port forwarding
```

> ✅ PEM key configured — MobaXterm will use key authentication (no password needed)

---

### Step 4 — Connect to EC2

```
→ Click: OK
→ Accept host fingerprint prompt (first connection only) → Accept
```

Expected terminal output:

```
Connecting to 13.203.156.167:22...
Authenticating with public key "saroj-ubuntu-prod-2026.pem"

ubuntu@ip-172-31-47-200:~$
```

> ✅ Successfully connected to EC2 via MobaXterm — no password required!

---

## PHASE 2 — Production Verification

### Step 5 — Verify EC2 Instance Metadata

```bash
# Get IMDSv2 token
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Verify Public IP
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/public-ipv4
```

Expected output:
```
13.203.156.167 ✓
```

```bash
# Verify Instance ID
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id
```

```bash
# Verify Private IP
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/local-ipv4
```

Expected output:
```
172.31.12.91 ✓
```

---

### Step 6 — Verify Nginx Web Server Status

```bash
sudo systemctl status nginx
```

Expected output:

```
● nginx.service - A high performance web server
   Loaded: loaded (/lib/systemd/system/nginx.service)
   Active: active (running) ✓
```

> ✅ Production web server confirmed running

---

## 📊 Target Infrastructure Summary

| Property | Value |
|---|---|
| EC2 Public IP | 13.203.156.167 |
| EC2 Private IP | 172.31.12.91 |
| SSH User | ubuntu |
| SSH Port | 22 |
| Key File | saroj-ubuntu-prod-2026.pem |
| OS | Ubuntu Server 24.04 LTS |
| Web Server | Nginx — Active (running) ✓ |
| Region | ap-south-1 (Mumbai) |

---

## 💡 Dual Terminal Production Strategy

| Tool | Best For | Status |
|---|---|---|
| **MobaXterm** | Interactive ops, SFTP file transfer, multi-tab sessions | ✅ Primary |
| **CMD / Terminal SSH** | CI/CD automation, scripting, pipelines | ✅ Backup |
| **AWS Console (EC2 Connect)** | Emergency rescue when key is lost | ✅ Available |

---

## 🌟 MobaXterm Key Features Used

| Feature | Benefit |
|---|---|
| **Built-in SFTP Browser** | Drag-and-drop file transfer between local and EC2 |
| **Multi-tab Sessions** | Connect to multiple EC2 instances simultaneously |
| **Session Manager** | Save and reuse SSH sessions without re-entering details |
| **PEM Key Support** | Direct support for AWS PEM key files |
| **X11 Forwarding** | Run GUI applications from remote server on local display |
| **Macro Recording** | Automate repetitive SSH commands |

---

## 🔧 Troubleshooting

| Issue | Symptom | Fix |
|---|---|---|
| `Connection refused` | Port 22 blocked | Check EC2 Security Group has SSH port 22 open |
| `Permission denied (publickey)` | Wrong key | Verify correct `.pem` file selected in Advanced SSH settings |
| `Host unreachable` | Can't connect | Verify EC2 instance is running and Public IP is correct |
| PEM key greyed out | Can't browse to key | Ensure `.pem` file is saved locally — not on network drive |
| Fingerprint warning | First connection | Click Accept — this is normal for first-time connections |
| Session disconnects | Timeout | MobaXterm → Settings → SSH → Keep alive interval: 30s |

---

## 🔧 Useful Commands After Connection

```bash
# Check current user
whoami

# Check server uptime
uptime

# Check disk usage
df -hT

# Check memory usage
free -h

# Check running processes
htop

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log

# Check public IP from inside server
curl ifconfig.me
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

- [MobaXterm Official Download](https://mobaxterm.mobatek.net/download.html)
- [AWS EC2 SSH Access](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html)
- [EC2 Instance Metadata](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)
- [MobaXterm Documentation](https://mobaxterm.mobatek.net/documentation.html)
