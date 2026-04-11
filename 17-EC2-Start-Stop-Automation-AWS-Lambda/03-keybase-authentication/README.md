# 🔑 AWS EC2 — Key-Based Authentication Production Setup (Passwordless SSH)

Set up **production-grade SSH key-based authentication** on an EC2 instance — generate an RSA key pair locally, deploy the public key to the server, and achieve fully passwordless SSH access.

---

## 🗂️ Project Overview

This project demonstrates how to configure **SSH key-based authentication** from scratch on a Linux server — the standard security practice used in all production environments. Password-based SSH is disabled in most production servers; key-based authentication is faster, more secure, and essential for automation.

---

## 🎯 Architecture Overview

```
  Local Workstation
  ┌─────────────────────────────────────┐
  │                                     │
  │  ssh-keygen -f ~/.ssh/saroj_key     │
  │                                     │
  │  ~/.ssh/saroj_key      ← PRIVATE   │
  │  ~/.ssh/saroj_key.pub  ← PUBLIC    │
  │                                     │
  └──────────────┬──────────────────────┘
                 │
                 │  Copy PUBLIC key (.pub)
                 │  to server
                 ▼
  EC2 Server (Ubuntu)
  ┌─────────────────────────────────────┐
  │                                     │
  │  /home/saroj/.ssh/                  │
  │  ├── authorized_keys  ← .pub here  │
  │  Permissions:                       │
  │  ├── .ssh/            drwx------   │
  │  └── authorized_keys  -rw-------   │
  │                                     │
  └─────────────────────────────────────┘
                 │
                 │  ssh -i saroj_key saroj@public_ip
                 ▼
  ✅ Passwordless SSH Access — NO PASSWORD PROMPT!
```

---

## ✅ Prerequisites

- AWS EC2 instance running Ubuntu (with existing SSH access)
- Local terminal (Windows CMD / PowerShell / Linux / Mac)
- Existing key pair to initially access the server

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — Generate SSH Key Pair (Local Workstation)

### Step 1 — Generate RSA Key Pair

Run this on your **local machine** (CMD / Terminal):

```bash
ssh-keygen -f ~/.ssh/saroj_key
```

When prompted:

```
Enter passphrase (empty for no passphrase): [Press ENTER]
Enter same passphrase again:               [Press ENTER]
```

Expected output:

```
Generating public/private rsa key pair.
Your identification has been saved in /home/user/.ssh/saroj_key
Your public key has been saved in /home/user/.ssh/saroj_key.pub
The key fingerprint is:
SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx user@local
```

Two files are created:

```
~/.ssh/saroj_key        ← PRIVATE KEY  (keep secret, never share)
~/.ssh/saroj_key.pub    ← PUBLIC KEY   (safe to share with servers)
```

---

### Step 2 — Verify Keys and Copy Public Key

```bash
# Verify both files exist
ls -la ~/.ssh/saroj_key*
```

Expected:
```
-rw-------  ~/.ssh/saroj_key      ← Private key (600 permissions)
-rw-r--r--  ~/.ssh/saroj_key.pub  ← Public key
```

```bash
# Display and COPY the entire public key line
cat ~/.ssh/saroj_key.pub
```

Expected output (copy this entire line):
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... saroj@local
```

> ✅ RSA key pair generated — keep private key safe, copy public key content

---

## PHASE 2 — Server User Setup

### Step 3 — Connect to Server with Existing Access

```bash
# SSH into EC2 using your existing key pair
ssh -i "Key_pair.pem" ubuntu@[PUBLIC-IP]
```

> ✅ Connected to EC2 as ubuntu

---

### Step 4 — Create Production User 'saroj'

```bash
sudo adduser saroj
```

Follow the prompts:

```
New password:         [Enter a password]
Retype new password:  [Confirm password]
Full Name:            [Enter or press ENTER]
...
Is the information correct? [Y/n]: Y
```

> ✅ User 'saroj' created

---

### Step 5 — Create SSH Directory with Correct Permissions

```bash
# Create .ssh directory for saroj user
sudo mkdir -p /home/saroj/.ssh

# Create authorized_keys file
sudo touch /home/saroj/.ssh/authorized_keys

# Set EXACT permissions (SSH rejects wrong permissions)
sudo chmod 700 /home/saroj/.ssh              # drwx------
sudo chmod 600 /home/saroj/.ssh/authorized_keys   # -rw-------
```

Verify permissions:

```bash
ls -la /home/saroj/.ssh/
```

Expected:
```
drwx------  .ssh/
-rw-------  authorized_keys
```

> ✅ SSH directory structure created with correct permissions
> ⚠️ Wrong permissions = SSH will silently reject key authentication

---

## PHASE 3 — Deploy Public Key to Server

### Step 6 — Paste Public Key into authorized_keys

```bash
sudo vim /home/saroj/.ssh/authorized_keys
```

Inside vim:

```
Press 'i'          → Enter INSERT mode
Paste the ENTIRE public key line from Step 2:
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... saroj@local
Press ESC          → Exit INSERT mode
Type ':wq'         → Save and quit
Press ENTER
```

Verify key was saved correctly:

```bash
sudo cat /home/saroj/.ssh/authorized_keys
```

Expected:
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... saroj@local
```

> ✅ Public key deployed to authorized_keys

---

### Step 7 — Set Correct Ownership

```bash
# SSH strictly checks file ownership
sudo chown -R saroj:saroj /home/saroj
```

Verify ownership:

```bash
ls -la /home/saroj/
```

Expected:
```
drwxr-xr-x  saroj saroj  .ssh/
```

> ✅ Ownership set to saroj:saroj — SSH will now accept key authentication

---

## PHASE 4 — Test Passwordless SSH Access

### Step 8 — Connect from Local Machine Using Private Key

Open a **new terminal on your local machine**:

```bash
ssh -i ~/.ssh/saroj_key saroj@[PUBLIC-IP]
```

Expected — **no password prompt**:

```
saroj@ip-172-31-47-200:~$
```

> ✅ Passwordless SSH access confirmed — authenticated via key 🎉

---

### Step 9 — Verify User and Permissions

```bash
# Confirm you are the correct user
whoami
```
```
saroj
```

```bash
# Check user ID and groups
id
```
```
uid=1001(saroj) gid=1001(saroj) groups=1001(saroj)
```

```bash
# Verify home directory
pwd
```
```
/home/saroj
```

> ✅ Key-based authentication fully working — user, ID, and home directory confirmed

---

## 📊 Key-Based Authentication Summary

| Component | Location | Permission | Purpose |
|---|---|---|---|
| Private Key | `~/.ssh/saroj_key` | 600 (-rw-------) | Stays on local machine only |
| Public Key | `~/.ssh/saroj_key.pub` | 644 (-rw-r--r--) | Copied to server |
| authorized_keys | `/home/saroj/.ssh/authorized_keys` | 600 (-rw-------) | Holds public keys on server |
| .ssh directory | `/home/saroj/.ssh/` | 700 (drwx------) | SSH config directory |

---

## 🔒 Security Best Practices

| Practice | Why |
|---|---|
| **Never share private key** | Anyone with private key can access your server |
| **Use passphrase on private key** | Adds second layer of protection if key is stolen |
| **chmod 600 on private key** | SSH refuses to use keys with loose permissions |
| **chmod 700 on .ssh directory** | Prevents other users from reading SSH config |
| **One key per authorized_keys line** | Add multiple keys for multiple users/machines |
| **Disable password auth** | After key setup, disable passwords in sshd_config |

---

## 🔧 Troubleshooting

| Issue | Symptom | Fix |
|---|---|---|
| Still prompted for password | Key not working | Check authorized_keys has correct public key content |
| `Permission denied (publickey)` | Auth rejected | Verify `.ssh` = 700, `authorized_keys` = 600, ownership = saroj:saroj |
| `WARNING: UNPROTECTED PRIVATE KEY` | SSH refuses key | Run `chmod 600 ~/.ssh/saroj_key` locally |
| Key accepted but wrong user | Logged in as ubuntu | Ensure you specify `saroj@` not `ubuntu@` in SSH command |
| authorized_keys empty | File exists but no key | Re-paste public key — ensure full line was copied including `ssh-rsa` prefix |

---

## 🔧 Useful Commands Reference

```bash
# Generate key pair
ssh-keygen -f ~/.ssh/saroj_key

# Connect with private key
ssh -i ~/.ssh/saroj_key saroj@[PUBLIC-IP]

# Copy public key to server (alternative method)
ssh-copy-id -i ~/.ssh/saroj_key.pub saroj@[PUBLIC-IP]

# Check SSH service status on server
sudo systemctl status ssh

# View SSH login attempts
sudo tail -f /var/log/auth.log

# Disable password authentication (production hardening)
sudo vim /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
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

- [SSH Key-Based Authentication](https://www.ssh.com/academy/ssh/public-key-authentication)
- [AWS EC2 Key Pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)
- [Linux SSH Configuration](https://man.openbsd.org/sshd_config)
- [OpenSSH Best Practices](https://infosec.mozilla.org/guidelines/openssh)
