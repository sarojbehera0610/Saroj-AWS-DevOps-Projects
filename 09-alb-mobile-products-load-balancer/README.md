# ⚖️ AWS Application Load Balancer — Path-Based Routing (Mobile + Products)

Route traffic to different backend services using **ALB path-based routing** — directing `/mobile` traffic to Mobile EC2 instances and `/products` traffic to Product EC2 instances on AWS.

---

## 🗂️ Project Overview

This project demonstrates how to configure an **Application Load Balancer (ALB)** with path-based routing rules to serve two different web services from a single ALB DNS endpoint — simulating a real-world multi-service web application.

---

## 🎯 ALB Path-Based Routing Architecture

```
                        Browser
                           │
                           ▼
              ┌─────────────────────────┐
              │    ALB-Mobile-Products  │
              │    (Internet-facing)    │
              │    HTTP:80 / HTTPS:443  │
              └─────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
         Path: /mobile*           Path: /products*
              │                         │
              ▼                         ▼
          TG-Mobile                TG-Products
              │                         │
       ┌──────┴──────┐          ┌───────┴───────┐
       ▼             ▼          ▼               ▼
  Mobile01       Mobile02   Product01       Product02
  (Nginx)        (Nginx)    (Nginx)         (Nginx)
```

---

## ✅ Prerequisites

- AWS Account with EC2 and ALB access
- Default VPC with public subnets
- Key pair available (e.g. `saroj-alb-key.pem`)

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — Mobile Instances + Target Group

### Step 1 — Launch Instance-Mobile01

```
EC2 → Launch Instance
├── Name:              Instance-Mobile01
├── AMI:               Ubuntu Server 24.04 LTS
├── Instance Type:     t3.micro
├── Key Pair:          saroj-alb-key.pem
├── VPC:               Default VPC
├── Subnet:            Default Subnet
└── Auto-assign IP:    ENABLE ✓
```

---

### Step 2 — Add User Data to Mobile01

**Advanced Details → User Data:**

```bash
#!/bin/bash
apt update && apt install nginx -y
echo "<h1>MOBILE WEB - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx
```

> ✅ Instance-Mobile01 launching with Nginx Mobile page

---

### Step 3 — Launch Instance-Mobile02

```
Name:       Instance-Mobile02
AMI:        Ubuntu Server 24.04 LTS
User Data:  Same as Mobile01
```

> ✅ Both Mobile instances running with Public IPs

---

### Step 4 — Create Target Group TG-Mobile

```
EC2 → Target Groups → Create Target Group
├── Target Type:   Instances
├── Name:          tg-mobile
├── Protocol:      HTTP
├── Port:          80
├── VPC:           Default VPC
├── Health Check:  /
└── Success Codes: 200-299
```

> ✅ tg-mobile created

---

### Step 5 — Register Mobile Targets

```
tg-mobile → Targets → Register Targets
├── Instance-Mobile01 → Port 80 ✓
└── Instance-Mobile02 → Port 80 ✓
→ Include as pending → Register targets
```

> ✅ 2 Mobile targets registered — wait for status: Healthy

---

## PHASE 2 — Product Instances + Target Group

### Step 6 — Launch Instance-Product01

```
Name:           Instance-Product01
AMI:            Ubuntu Server 24.04 LTS
Instance Type:  t3.micro
Auto-assign IP: ENABLE ✓
```

**User Data:**

```bash
#!/bin/bash
apt update && apt install nginx -y
mkdir -p /var/www/html/products
echo "<h1>PRODUCTS WEB - $(hostname)</h1>" > /var/www/html/products/index.html
ln -sf /var/www/html/products /usr/share/nginx/html/products
systemctl start nginx && systemctl enable nginx
```

> ✅ Instance-Product01 launching with Nginx Products page

---

### Step 7 — Launch Instance-Product02

```
Name:      Instance-Product02
User Data: Same as Product01
```

> ✅ Both Product instances running with Public IPs

---

### Step 8 — Create Target Group TG-Products

```
EC2 → Target Groups → Create Target Group
├── Name:          tg-products
├── Protocol:      HTTP
├── Port:          80
├── VPC:           Default VPC
├── Health Check:  /products
└── Success Codes: 200-299
```

> ✅ tg-products created

---

### Step 9 — Register Product Targets

```
tg-products → Targets → Register Targets
├── Instance-Product01 → Port 80 ✓
└── Instance-Product02 → Port 80 ✓
→ Register targets
```

> ✅ 2 Product targets registered — wait for status: Healthy

---

## PHASE 3 — Create Application Load Balancer

### Step 10 — Create ALB

```
EC2 → Load Balancers → Create → Application Load Balancer
├── Name:             ALB-Mobile-Products
├── Scheme:           Internet-facing
├── IP Address Type:  IPv4
├── VPC:              Default VPC
├── Subnets:          Select ALL available subnets ✓
└── Security Group:   Create new SG
                      ├── HTTP:80   → 0.0.0.0/0
                      └── HTTPS:443 → 0.0.0.0/0
```

> ✅ ALB-Mobile-Products → State: Provisioning

---

### Step 11 — Add Listener Rule for Mobile Path

```
ALB → Listeners → HTTP:80 → View/Edit Rules
→ Add Rule
├── IF:   Path is  /mobile*
├── THEN: Forward to tg-mobile
→ Save
```

> ✅ Rule 1: `/mobile*` → tg-mobile

---

### Step 12 — Add Listener Rule for Products Path

```
→ Add Rule
├── IF:   Path is  /products*
├── THEN: Forward to tg-products
└── Default Action: Forward to tg-mobile (fallback)
→ Save
```

> ✅ Rule 2: `/products*` → tg-products

---

### Step 13 — Verify ALB is Active

```
Load Balancers → ALB-Mobile-Products
→ State: Active ✓
→ Copy DNS Name: ALB-Mobile-Products-[random].elb.amazonaws.com
```

> ✅ ALB Active — DNS name ready for testing

---

## PHASE 4 — Testing

### Step 14 — Test Mobile Path

```
Browser: http://ALB-DNS/mobile
```

Expected:
```
MOBILE WEB - ip-xxx-xx-xx-xx
```

Refresh multiple times → load balances between Mobile01 and Mobile02 ✅

---

### Step 15 — Test Products Path

```
Browser: http://ALB-DNS/products
```

Expected:
```
PRODUCTS WEB - ip-xxx-xx-xx-xx
```

Refresh multiple times → load balances between Product01 and Product02 ✅

---

### Step 16 — Verify Target Health

```
EC2 → Target Groups
├── tg-mobile   → Targets: 2/2 Healthy ✓
└── tg-products → Targets: 2/2 Healthy ✓
```

> ✅ All 4 targets healthy

---

### Step 17 — ALB Monitoring

```
ALB → Monitoring Tab
→ Healthy Host Count: 4/4 ✓
→ Request Count: increasing with each browser refresh
```

> ✅ ALB metrics confirm all 4 targets are receiving traffic

---

## 📊 ALB Configuration Summary

| Component | Instances | Target Group | Path Rule | Health Check |
|---|---|---|---|---|
| **Mobile** | Mobile01, Mobile02 | tg-mobile:80 | `/mobile*` | `/` 200-299 |
| **Products** | Product01, Product02 | tg-products:80 | `/products*` | `/products` 200-299 |
| **ALB** | ALB-Mobile-Products | HTTP:80 | Path-based routing | 4/4 Healthy ✓ |

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| 502 Bad Gateway | Target group has no healthy instances — check Nginx is running |
| Health check failing on /products | Ensure `/products` directory and `index.html` exist on Product instances |
| Path routing not working | Check listener rule priority — more specific rules should have higher priority |
| ALB DNS not resolving | Wait 2–3 minutes after ALB creation for DNS propagation |
| Targets stuck in Initial state | Health check path may be wrong — verify `/` returns 200 for mobile, `/products` for products |

---

## 💡 Key Concepts Learned

- **ALB Path-Based Routing** — Single ALB DNS serves multiple backend services based on URL path
- **Target Groups** — Logical grouping of instances for routing and health checking
- **Listener Rules** — Priority-based rules that match conditions and forward to target groups
- **Health Checks** — ALB continuously monitors instances and routes only to healthy targets
- **Load Balancing** — ALB distributes requests evenly across instances in each target group

---

## 📁 File Structure

```
.
├── README.md
└── screenshots/
```

---

## 📌 References

- [ALB Listener Rules Documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-update-rules.html)
- [Target Groups for ALB](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)
- [ALB Path-Based Routing](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/tutorial-load-balancer-routing.html)
