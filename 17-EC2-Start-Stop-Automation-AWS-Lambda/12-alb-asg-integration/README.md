# ⚖️ AWS ALB + Auto Scaling Groups with Path-Based Routing

Route traffic intelligently across 3 Auto Scaling Groups using an **Application Load Balancer** with path-based routing rules on AWS — simulating a real-world multi-service architecture (Home, Mobile, Payment).

---

## 🗂️ Project Overview

This project demonstrates how to set up a **production-grade load balancing architecture** on AWS where a single ALB routes incoming requests to different backend services based on the URL path:

| URL Path | Target Group | Auto Scaling Group | Instances |
|---|---|---|---|
| `/` | TG-Home | ASG-Home | 2 |
| `/mobilepage/*` | TG-Mobile | ASG-Mobile | 2 |
| `/payment/*` | TG-Payment | ASG-Payment | 2 |

---

## 🏗️ Architecture

```
                        Browser
                           │
                           ▼
              ┌─────────────────────────┐
              │      ALB-Amazon         │
              │  (Internet-facing)      │
              │  ap-south-1a + 1b       │
              └─────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
      Path: /        /mobilepage/*     /payment/*
           │               │               │
           ▼               ▼               ▼
       TG-Home          TG-Mobile      TG-Payment
           │               │               │
           ▼               ▼               ▼
       ASG-Home         ASG-Mobile     ASG-Payment
      (2 instances)    (2 instances)   (2 instances)
```

---

## ✅ Prerequisites

- AWS Account with EC2, ALB, and Auto Scaling access
- Default VPC with subnets in **ap-south-1a** and **ap-south-1b**
- Security Group **SG-Web-Public** with:
  - Inbound: SSH (port 22), HTTP (port 80)
  - Outbound: All traffic

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — Launch 3 Manual Instances (Baseline Testing)

### Step 1 — Launch Home-Amazon Instance

```
EC2 → Launch Instance
├── Name:             Home-Amazon
├── AMI:              Ubuntu 24.04
├── Instance Type:    t3.micro
├── Auto-assign IP:   ENABLE ✓
├── Security Group:   SG-Web-Public (SSH:22, HTTP:80)
```

**User Data:**

```bash
#!/bin/bash
apt update && apt install nginx -y
echo "<h1>AMAZON HOME - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx
```

> ✅ Verify: Hit the Public IP in browser → `AMAZON HOME - ip-xx-xx-xx-xx`

---

### Step 2 — Launch Mobile-Amazon Instance

```
Name: Mobile-Amazon
AMI: Ubuntu 24.04 | t3.micro | Auto-assign IP: ENABLE ✓
Security Group: SG-Web-Public
```

**User Data:**

```bash
#!/bin/bash
apt update && apt install nginx -y
mkdir -p /var/www/html/mobilepage
echo "<h1>MOBILE PAGE - $(hostname)</h1>" > /var/www/html/mobilepage/index.html
ln -sf /var/www/html/mobilepage /usr/share/nginx/html/mobilepage
systemctl start nginx && systemctl enable nginx
```

> ✅ Verify: Hit `http://<Public-IP>/mobilepage/` → `MOBILE PAGE - ip-xx-xx-xx-xx`

---

### Step 3 — Launch Payment-Amazon Instance

```
Name: Payment-Amazon
AMI: Ubuntu 24.04 | t3.micro | Auto-assign IP: ENABLE ✓
Security Group: SG-Web-Public
```

**User Data:**

```bash
#!/bin/bash
apt update && apt install nginx -y
mkdir -p /var/www/html/payment
echo "<h1>PAYMENT PAGE - $(hostname)</h1>" > /var/www/html/payment/index.html
ln -sf /var/www/html/payment /usr/share/nginx/html/payment
systemctl start nginx && systemctl enable nginx
```

> ✅ Verify: Hit `http://<Public-IP>/payment/` → `PAYMENT PAGE - ip-xx-xx-xx-xx`

---

## PHASE 2 — Create 3 Target Groups

### Step 4 — Create TG-Home

```
EC2 → Target Groups → Create Target Group
├── Name:           TG-Home
├── Protocol:       HTTP
├── Port:           80
├── VPC:            Default VPC
├── Health Check:   /
├── Success Codes:  200-299
```

> ✅ TG-Home created (no targets registered yet — ASG will auto-register)

---

### Step 5 — Create TG-Mobile

```
Name:          TG-Mobile
Health Check:  /mobilepage
Success Codes: 200-299
```

> ✅ TG-Mobile created

---

### Step 6 — Create TG-Payment

```
Name:          TG-Payment
Health Check:  /payment
Success Codes: 200-299
```

> ✅ TG-Payment created

---

## PHASE 3 — Create 3 Launch Templates

### Step 7 — Create Home Launch Template

```
EC2 → Launch Templates → Create
├── Name:                     home-lt (v1)
├── AMI:                      Ubuntu 24.04
├── Instance Type:            t3.micro
├── Network Interface:        Auto-assign Public IP → ENABLE ✓
├── Security Group:           SG-Web-Public
├── User Data:                Same as Home-Amazon (Step 1)
```

> ✅ home-lt created with Public IP enabled

---

### Step 8 — Create Mobile Launch Template

```
Name:       mobile-lt (v1)
User Data:  Same as Mobile-Amazon (Step 2)
```

> ✅ mobile-lt created

---

### Step 9 — Create Payment Launch Template

```
Name:       payment-lt (v1)
User Data:  Same as Payment-Amazon (Step 3)
```

> ✅ payment-lt created

---

## PHASE 4 — Create 3 Auto Scaling Groups

### Step 10 — Create ASG-Home

```
EC2 → Auto Scaling Groups → Create
├── Name:              ASG-Home
├── Launch Template:   home-lt
├── VPC:               Default VPC
├── Availability Zones: ap-south-1a + ap-south-1b ✓
├── Desired Capacity:  2
├── Minimum Capacity:  1
├── Maximum Capacity:  3
```

> ✅ ASG-Home created — 2 instances launching

---

### Step 11 — Create ASG-Mobile

```
Name:              ASG-Mobile
Launch Template:   mobile-lt
AZs:               ap-south-1a + ap-south-1b
Desired: 2 | Min: 1 | Max: 3
```

> ✅ ASG-Mobile created

---

### Step 12 — Create ASG-Payment

```
Name:              ASG-Payment
Launch Template:   payment-lt
AZs:               ap-south-1a + ap-south-1b
Desired: 2 | Min: 1 | Max: 3
```

> ✅ ASG-Payment created

---

## PHASE 5 — Attach Target Groups to ASGs

### Step 13 — Attach TG-Home to ASG-Home

```
Auto Scaling Groups → ASG-Home
→ Details Tab → Load Balancing → Edit
→ Attach Target Group: TG-Home ✓ → Save
```

> ✅ ASG-Home instances will auto-register into TG-Home

---

### Step 14 — Attach TG-Mobile to ASG-Mobile

```
ASG-Mobile → Load Balancing → TG-Mobile ✓ → Save
```

> ✅ ASG-Mobile → TG-Mobile attached

---

### Step 15 — Attach TG-Payment to ASG-Payment

```
ASG-Payment → Load Balancing → TG-Payment ✓ → Save
```

> ✅ ASG-Payment → TG-Payment attached

---

## PHASE 6 — Create ALB with Path-Based Routing

### Step 16 — Create ALB-Amazon

```
EC2 → Load Balancers → Create → Application Load Balancer
├── Name:           ALB-Amazon
├── Scheme:         Internet-facing
├── VPC:            Default VPC
├── AZ Mappings:    ap-south-1a + ap-south-1b ✓
├── Security Group: SG-Web-Public
├── Listener:       HTTP:80 → Default Forward to: TG-Home
```

> ✅ ALB-Amazon created — copy the DNS name

---

### Step 17 — Add Path Rule for Mobile

```
ALB-Amazon → Listeners → HTTP:80 → View/Edit Rules
→ Add Rule
├── IF:   Path is  /mobilepage/*
├── THEN: Forward to TG-Mobile
→ Save
```

> ✅ Rule 1: `/mobilepage/*` → TG-Mobile

---

### Step 18 — Add Path Rule for Payment

```
→ Add Another Rule
├── IF:   Path is  /payment/*
├── THEN: Forward to TG-Payment
→ Save
```

> ✅ Rule 2: `/payment/*` → TG-Payment

---

### Step 19 — Verify Health Checks

```
EC2 → Target Groups
├── TG-Home    → Targets: 2/2 Healthy ✓
├── TG-Mobile  → Targets: 2/2 Healthy ✓
├── TG-Payment → Targets: 2/2 Healthy ✓
```

> ✅ All 6 instances healthy across 3 Target Groups

---

## PHASE 7 — Test Path-Based Routing

### Step 20 — Test Home Path

```
Browser: http://<ALB-Amazon-DNS>/
```

Expected:
```
AMAZON HOME - ip-xx-xx-xx-xx
```

Refresh multiple times → load balances between 2 ASG-Home instances ✅

---

### Step 21 — Test Mobile Path

```
Browser: http://<ALB-Amazon-DNS>/mobilepage/
```

Expected:
```
MOBILE PAGE - ip-xx-xx-xx-xx
```

Refresh multiple times → load balances between 2 ASG-Mobile instances ✅

---

### Step 22 — Test Payment Path

```
Browser: http://<ALB-Amazon-DNS>/payment/
```

Expected:
```
PAYMENT PAGE - ip-xx-xx-xx-xx
```

Refresh multiple times → load balances between 2 ASG-Payment instances ✅

---

## 📊 Final Architecture Summary

| Path | Target Group | ASG | Instances | Health |
|---|---|---|---|---|
| `/` | TG-Home | ASG-Home | 2/2 | ✅ Healthy |
| `/mobilepage/*` | TG-Mobile | ASG-Mobile | 2/2 | ✅ Healthy |
| `/payment/*` | TG-Payment | ASG-Payment | 2/2 | ✅ Healthy |

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| Health check failing | Ensure Nginx is running and correct path exists on instance |
| 502 Bad Gateway | Target group has no healthy instances — check security group port 80 |
| Path routing not working | Check listener rules priority order in ALB |
| Instances not registering in TG | Verify ASG is attached to the correct Target Group |
| ALB not reachable | Check SG-Web-Public allows inbound HTTP port 80 |

---

## 📁 File Structure

```
.
├── README.md
├── userdata/
│   ├── home-userdata.sh        # Nginx config for Home page
│   ├── mobile-userdata.sh      # Nginx config for Mobile page
│   └── payment-userdata.sh     # Nginx config for Payment page
```

---

## 💡 Key Concepts Learned

- **Path-Based Routing** — ALB routes requests based on URL path patterns
- **Auto Scaling Groups** — Automatically maintain desired instance count
- **Launch Templates** — Reusable instance configuration for ASGs
- **Target Groups** — Logical grouping of instances for health checking and routing
- **Health Checks** — ALB continuously monitors instance health and routes only to healthy targets

---

## 📌 References

- [ALB Path-Based Routing Documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/tutorial-load-balancer-routing.html)
- [Auto Scaling Groups Documentation](https://docs.aws.amazon.com/autoscaling/ec2/userguide/AutoScalingGroup.html)
- [Launch Templates Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html)
