# Project 15: AWS RDS MySQL Database Setup with EC2 Access

## Project Overview
This project covers the complete setup of an AWS RDS MySQL instance from scratch,
configuring networking, security groups, and accessing the database securely 
from an EC2 instance using the MySQL CLI.

---

## Tech Stack
- AWS RDS (MySQL 8.0)
- AWS EC2 (Ubuntu, t3.micro)
- AWS VPC, Subnets, Security Groups
- MySQL Client (CLI)
- Linux/Ubuntu Terminal

---

## Architecture
```
Local Laptop
     ↓ SSH
EC2 Instance (Ubuntu t3.micro)
     ↓ Port 3306 (Same VPC + Same Security Group)
RDS MySQL Instance
     ↓
Database: myapp_db / newsarojdb
```

---

## Step-by-Step Setup

### Step 1 — Created RDS Instance
- Went to AWS Console → RDS → Create Database
- Selected **Standard Create**
- Engine: **MySQL 8.0**
- Template: **Free Tier**
- DB Instance Identifier: `myapp-prod-db-instance-identifier`
- Master Username: `myapp_admin`
- Master Password: (self managed)
- Instance Class: `db.t3.micro` (Free Tier eligible)
- Storage: 20GB gp2
- Public Access: **No** 

### Step 2 — Networking Configuration
- VPC: `vpc-08015a2b827c4656d` (default VPC)
- Subnet Group: default
- Availability Zone: `ap-south-1a` (Mumbai)
- Security Group: `sg-0653a4bfaaa4fcbc8` (default)

### Step 3 — Additional Configuration
- Initial Database Name: `myapp_db`
- Backup Retention: 7 days
- Deletion Protection: Disabled (dev environment)

### Step 4 — Launched EC2 Instance
- Name: `db instance`
- AMI: Ubuntu
- Instance Type: t3.micro
- Same VPC as RDS: `vpc-08015a2b827c4656d`
- Same Security Group as RDS: `sg-0653a4bfaaa4fcbc8`
- Key Pair: created and downloaded

### Step 5 — Installed MySQL Client on EC2
```bash
sudo apt update
sudo apt install mysql-client -y
```

### Step 6 — Connected to RDS from EC2
```bash
mysql -h myapp-prod-db-instance-identifier.cto44y8iy755.ap-south-1.rds.amazonaws.com \
      -u myapp_admin \
      -p
```

### Step 7 — Created Database
```sql
CREATE DATABASE newsarojdb;
SHOW DATABASES;
USE newsarojdb;
```

---

## Troubleshooting — Issues Faced & How I Fixed Them

### Issue 1 — ERROR 2003: Can't connect to MySQL server (110)
**What it means:** Connection timed out — firewall blocking port 3306

**First Attempt:**
- Checked RDS Console → saw **Internet Access Gateway: Disabled**
- Thought IGW was missing

**What I found:**
- VPC Route Table `rtb-0d2c12f22b9aa85c4` already had:
  - `0.0.0.0/0 → igw-0ed047a744db2b838` ✅
- IGW was already attached and working
- Root cause was actually the **Security Group**, not the IGW

---

### Issue 2 — Security Group Source IP Was Wrong
**What happened:**
- Added inbound rule for MySQL port 3306
- Source IP was set to `3.110.62.101/32`
- This was an **AWS CloudShell server IP**, not my real laptop IP

**Why it happened:**
- Ran `curl ifconfig.me` inside AWS CloudShell
- CloudShell gave its own server IP instead of my real public IP

**How I fixed it:**
- Ran `curl ifconfig.me` from my **local terminal** (not CloudShell)
- Got real IP: `223.185.37.121`
- Updated Security Group inbound rule source to `223.185.37.121/32`

---

### Issue 3 — Still Could Not Connect (Wrong IP for EC2 Access)
**What happened:**
- Security group had my laptop IP `223.185.37.121/32`
- But I was connecting **from EC2 instance**, not from laptop
- EC2 has a different IP — so RDS was still blocking it

**How I fixed it:**
- Launched new EC2 instance with **same Security Group** as RDS (`sg-0653a4bfaaa4fcbc8`)
- Added port 3306 inbound rule with **EC2's public IP** as source
- Since both EC2 and RDS shared the same VPC and Security Group,
  traffic was allowed internally

**Key Learning:**
> Always connect to RDS **from EC2**, not from your laptop directly.
> Use the same VPC and Security Group for both EC2 and RDS.
> This is the correct production architecture.

---

### Issue 4 — SQL Syntax Error While Creating Database
**Error:**
```
ERROR 1064 (42000): You have an error in your SQL syntax
```

**What I typed wrong:**
```sql
create databases newsarojdb;   -- WRONG (databases is plural)
```

**Correct command:**
```sql
CREATE DATABASE newsarojdb;    -- correct (database is singular)
```

---

## Key Learnings from This Project

1. **IGW alone is not enough** — the Route Table must also have `0.0.0.0/0 → IGW`
2. **Never run `curl ifconfig.me` in CloudShell** to get your real IP — it gives AWS server IP
3. **Security Group is the most common cause** of RDS connection failures (Error 110)
4. **EC2 and RDS should share the same VPC and Security Group** for clean private access
5. **Public Accessibility = Yes** is needed only when connecting from outside AWS
6. **SQL syntax** — `CREATE DATABASE` not `CREATE DATABASES`
7. The correct production flow is: **Laptop → SSH → EC2 → MySQL Client → RDS**

---

## Commands Reference

### Install MySQL Client
```bash
sudo apt update
sudo apt install mysql-client -y
```

### Connect to RDS
```bash
mysql -h <rds-endpoint> -u <master-username> -p
```

### Basic MySQL Commands
```sql
SHOW DATABASES;          -- list all databases
CREATE DATABASE dbname;  -- create new database
USE dbname;              -- switch to database
SHOW TABLES;             -- list tables
SELECT DATABASE();       -- check active database
SELECT USER();           -- check current user
```

---

## Project Status
✅ RDS Instance Created  
✅ EC2 Instance Launched  
✅ Security Group Configured  
✅ MySQL Client Installed  
✅ RDS Connected via EC2  
✅ Database Created (newsarojdb)  

---

## Author
**Saroj Behera**  
GitHub: [sarojbehera0610](https://github.com/sarojbehera0610)  


