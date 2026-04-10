# AWS Network Load Balancer (NLB) with Auto Scaling Group — ap-south-1 (Mumbai)

> **Project Type:** AWS Networking & High Availability  
> **Region:** Asia Pacific — Mumbai (`ap-south-1`)  
> **Difficulty:** Intermediate  
> **Method:** AWS Management Console (GUI)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [AWS Services Used](#aws-services-used)
- [NLB vs ALB — Key Differences](#nlb-vs-alb--key-differences)
- [Prerequisites](#prerequisites)
- [Phase 1 — VPC & Subnet Setup](#phase-1--vpc--subnet-setup)
- [Phase 2 — Security Group](#phase-2--security-group)
- [Phase 3 — Launch Template with Nginx](#phase-3--launch-template-with-nginx)
- [Phase 4 — Auto Scaling Group](#phase-4--auto-scaling-group)
- [Phase 5 — Cross-Zone Load Balancing](#phase-5--cross-zone-load-balancing)
- [Phase 6 — Testing & Validation](#phase-6--testing--validation)
- [Troubleshooting](#troubleshooting)
- [Lessons Learned](#lessons-learned)
- [Cleanup](#cleanup)

---

## Project Overview

This project demonstrates how to deploy a **Network Load Balancer (NLB)** on AWS to distribute TCP traffic across EC2 instances running Nginx, spread across two Availability Zones in the Mumbai region. The setup uses an **Auto Scaling Group (ASG)** to ensure high availability and automatic instance replacement.

**What this project covers:**

- Setting up a custom VPC with public subnets across 2 Availability Zones
- Configuring a Security Group specifically for NLB + EC2 behaviour
- Creating a Launch Template with Nginx auto-installation via User Data
- Deploying an Auto Scaling Group with min 2 / max 4 instances
- Creating and configuring a Network Load Balancer (Layer 4 — TCP)
- Enabling Cross-Zone Load Balancing on NLB
- Validating load distribution via browser and curl

---

## Architecture

```
                        Internet
                            |
                     [NLB DNS Name]
              my-nlb-xxxx.elb.ap-south-1.amazonaws.com
                            |
                  +---------+---------+
                  |                   |
           [ap-south-1a]        [ap-south-1b]
         nlb-public-1a          nlb-public-1b
         10.0.1.0/24            10.0.2.0/24
                  |                   |
            [EC2 - Nginx]       [EC2 - Nginx]
             t3.micro             t3.micro
                  |                   |
             [Target Group: nlb-tg — TCP:80]
                  |
          [Auto Scaling Group]
          Min: 2 | Max: 4 | Desired: 2
                  |
              [nlb-vpc]
           CIDR: 10.0.0.0/16
```

**Traffic flow:** Client → NLB DNS → NLB node (per AZ) → Target Group → EC2 instance (Nginx)

---

## AWS Services Used

| Service | Purpose |
|---|---|
| VPC | Custom isolated network — `10.0.0.0/16` |
| Subnets | 2 public subnets across `ap-south-1a` and `ap-south-1b` |
| Internet Gateway | Enables internet access for public subnets |
| Route Table | Routes `0.0.0.0/0` traffic to IGW |
| Security Groups | Controls inbound TCP traffic to EC2 instances |
| EC2 Launch Template | Defines instance config + Nginx User Data |
| Auto Scaling Group | Manages EC2 fleet — min 2, max 4 instances |
| Network Load Balancer | Layer 4 TCP load balancer with static IP per AZ |
| Target Group | Routes NLB traffic to registered EC2 instances |

---

## NLB vs ALB — Key Differences

| Feature | NLB (This Project) | ALB |
|---|---|---|
| OSI Layer | Layer 4 — Transport (TCP/UDP) | Layer 7 — Application (HTTP/HTTPS) |
| Routing logic | IP + Port only | URL path, host headers, query strings |
| Performance | Ultra-low latency, millions of req/sec | Moderate latency |
| Static IP | Yes — Elastic IP per AZ | No |
| Security Group | Not on NLB itself — only on EC2 | On the ALB itself |
| Client IP | Preserved natively | Via `X-Forwarded-For` header |
| Cross-zone LB | Off by default | On by default |
| Use case | TCP/UDP apps, gaming, IoT, gRPC | Web apps, microservices, REST APIs |

**Why NLB for this project?** To demonstrate Layer 4 load balancing, static IP behaviour, and the importance of enabling cross-zone load balancing — concepts that differ fundamentally from ALB.

---

## Prerequisites

- AWS account with access to ap-south-1 (Mumbai) region
- IAM permissions for EC2, VPC, and ELB
- Basic understanding of VPC, subnets, and EC2
- A key pair created in ap-south-1 for SSH access

---

## Phase 1 — VPC & Subnet Setup

### 1.1 Create VPC

1. Go to **VPC Console** → **Your VPCs** → **Create VPC**
2. Select **VPC only**
3. Name: `nlb-vpc`
4. IPv4 CIDR: `10.0.0.0/16`
5. Click **Create VPC**

### 1.2 Create Public Subnets (one per AZ)

Go to **Subnets** → **Create subnet** → select `nlb-vpc`

| Subnet Name | Availability Zone | IPv4 CIDR |
|---|---|---|
| `nlb-public-1a` | ap-south-1a | 10.0.1.0/24 |
| `nlb-public-1b` | ap-south-1b | 10.0.2.0/24 |

> **Why 2 AZs?** NLB requires one subnet per Availability Zone. Two AZs means if one AZ goes down, traffic automatically flows to instances in the other AZ.

### 1.3 Enable Auto-assign Public IPv4

For **each subnet**:
1. Select subnet → **Actions** → **Edit subnet settings**
2. Tick **Enable auto-assign public IPv4 address**
3. Save

### 1.4 Create Internet Gateway

1. **Internet Gateways** → **Create internet gateway**
2. Name: `nlb-igw` → Create
3. **Actions** → **Attach to VPC** → select `nlb-vpc`

### 1.5 Create Route Table

1. **Route Tables** → **Create route table**
2. Name: `nlb-rt`, VPC: `nlb-vpc` → Create
3. Select `nlb-rt` → **Routes** tab → **Edit routes**
4. Add route: Destination `0.0.0.0/0` → Target: `nlb-igw` → Save
5. **Subnet associations** tab → **Edit subnet associations**
6. Tick both `nlb-public-1a` and `nlb-public-1b` → Save

> **Important:** Both subnets must appear under **Explicit subnet associations** — not under "Subnets without explicit associations". If they appear in the latter, the subnets are still using the default route table which may not have the IGW route.

---

## Phase 2 — Security Group

> **NLB-specific behaviour:** NLB does NOT have a security group of its own. You only attach a security group to the EC2 instances. Since NLB preserves the original client IP (not its own IP), you must allow `0.0.0.0/0` on port 80 — otherwise NLB health checks will fail because they originate from various IPs in the subnet.

1. Go to **EC2** → **Security Groups** → **Create security group**
2. Name: `nlb-ec2-sg`
3. Description: `Security group for NLB EC2 instances`
4. VPC: `nlb-vpc`

**Inbound Rules:**

| Type | Protocol | Port | Source | Purpose |
|---|---|---|---|---|
| HTTP | TCP | 80 | `0.0.0.0/0` | Internet traffic via NLB |
| HTTP | TCP | 80 | `10.0.0.0/16` | Internal VPC health checks |
| SSH | TCP | 22 | `0.0.0.0/0` | Management access |

5. Click **Create security group**

---

## Phase 3 — Launch Template with Nginx

1. Go to **EC2** → **Launch Templates** → **Create launch template**
2. Name: `nlb-nginx-lt`
3. Description: `NLB Nginx Launch Template`
4. Tick: *Provide guidance to help me set up a template that I can use with EC2 Auto Scaling*

**Configuration:**

| Setting | Value |
|---|---|
| AMI | Ubuntu Server 22.04 LTS (HVM), SSD Volume Type |
| Instance type | `t3.micro` |
| Key pair | Select existing or create `nlb-key` |
| Subnet | Do NOT select (ASG handles this) |
| Security group | Select `nlb-ec2-sg` |

**User Data** (paste in Advanced details → User data):

```bash
#!/bin/bash
apt update -y
apt install -y nginx

INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)

cat > /var/www/html/index.html <<EOF
<!DOCTYPE html>
<html>
<head><title>NLB Demo</title></head>
<body style="font-family:monospace;padding:40px;background:#111;color:#0f0">
<h2>NLB Project - ap-south-1 (Mumbai)</h2>
<p>Instance ID: $INSTANCE_ID</p>
<p>Availability Zone: $AZ</p>
<p>Served by: Nginx</p>
</body>
</html>
EOF

systemctl start nginx
systemctl enable nginx
```

> **Key lesson:** Match the package manager to the OS. Ubuntu uses `apt`. Amazon Linux 2/AL2023 uses `yum`/`dnf`. Using the wrong package manager causes User Data to fail silently — Nginx never installs and NLB health checks fail.

6. Click **Create launch template**

---

## Phase 4 — Auto Scaling Group

1. Go to **EC2** → **Auto Scaling Groups** → **Create Auto Scaling group**
2. Name: `nlb-asg`
3. Launch template: `nlb-nginx-lt`, Version: `Latest` → Next

**Network:**
- VPC: `nlb-vpc`
- Availability Zones and subnets: select both `nlb-public-1a` and `nlb-public-1b` → Next

**Load balancing:**
- Select **Attach to a new load balancer**
- Load balancer type: **Network Load Balancer**
- Name: `my-nlb`
- Scheme: **Internet-facing**
- Listeners and routing → Protocol: TCP, Port: 80
- Default action: **Create a target group** → Name: `nlb-tg`

**Health checks:**
- Health check type: **ELB**
- Health check grace period: `120` seconds → Next

**Group size:**

| Setting | Value |
|---|---|
| Desired capacity | 2 |
| Minimum capacity | 2 |
| Maximum capacity | 4 |

**Scaling policies (optional):**
- Target tracking → Metric: Average CPU utilization → Target: 60%

7. Review → **Create Auto Scaling group**

> AWS will now simultaneously launch 2 EC2 instances and create the NLB with the target group attached.

---

## Phase 5 — Cross-Zone Load Balancing

> **Critical NLB setting.** Unlike ALB where cross-zone load balancing is ON by default, NLB has it **OFF by default**. Without this, each NLB node only routes to instances in its own AZ — causing unequal traffic distribution.

**Without cross-zone (NLB default):**
```
NLB node (1a) → only EC2 instances in ap-south-1a
NLB node (1b) → only EC2 instances in ap-south-1b

If 1 instance in 1a and 3 in 1b:
  → 1a instance handles 50% of traffic (overloaded)
  → 3 instances in 1b share the other 50% (underutilized)
```

**With cross-zone enabled:**
```
All NLB nodes → all EC2 instances across all AZs
  → 4 instances each handle 25% of traffic (balanced)
```

**Steps to enable:**

1. Go to **EC2** → **Load Balancers** → select `my-nlb`
2. Click **Attributes** tab → **Edit**
3. Find **Cross-zone load balancing** → toggle **ON**
4. **Save changes**

**Verify Target Group health:**
1. **EC2** → **Target Groups** → `nlb-tg` → **Targets** tab
2. Wait 2–3 minutes after instances launch
3. Both targets should show status: **Healthy**

If targets show **Unhealthy**, check:
- Nginx is running on the instances (`systemctl status nginx`)
- Security group allows TCP port 80 from `0.0.0.0/0`
- Instances have a public IP and are in public subnets with IGW route

---

## Phase 6 — Testing & Validation

### 6.1 Get the NLB DNS Name

1. **EC2** → **Load Balancers** → `my-nlb`
2. Copy the **DNS name** from the Details tab
   - Format: `my-nlb-xxxx.elb.ap-south-1.amazonaws.com`

### 6.2 Browser Test

Open the DNS name in your browser. You should see:

```
NLB Project - ap-south-1 (Mumbai)
Instance ID: i-0xxxxxxxxxxxxxxxxx
Availability Zone: ap-south-1a
Served by: Nginx
```

### 6.3 Load Balancing Proof

> **Why doesn't the IP change on browser refresh?**  
> NLB uses **flow-based (connection-based) routing** at Layer 4. Your browser reuses the same TCP connection (HTTP keep-alive), so it stays on the same instance. This is fundamentally different from ALB which routes each HTTP request independently.

To prove load balancing is working, open **two different browsers** (or one normal + one incognito) simultaneously — each will connect to a different instance and show a different Instance ID.

Or use AWS CloudShell:
```bash
for i in {1..6}; do
  curl -s http://<your-nlb-dns-name> | grep "Instance ID"
  echo "---"
done
```

Expected output showing different instances:
```
Instance ID: i-0667a425d19b2dc9a   ← ap-south-1a
---
Instance ID: i-01ff071c8ff63f46d   ← ap-south-1b
---
Instance ID: i-0667a425d19b2dc9a
---
```

### 6.4 High Availability Test (Optional)

1. **EC2** → **Instances** → Stop one instance
2. Wait 60–90 seconds → check **Target Groups** → stopped instance goes **Unhealthy**
3. NLB automatically stops sending traffic to the unhealthy instance
4. All traffic routes to the remaining healthy instance
5. Start the stopped instance → it re-registers and goes **Healthy** again

### 6.5 ASG Auto-healing Test (Optional)

1. **Terminate** (not stop) one EC2 instance
2. Go to **Auto Scaling Groups** → `nlb-asg` → **Activity** tab
3. Watch ASG detect the capacity dropped below desired (2)
4. ASG automatically launches a replacement instance
5. New instance registers with the target group → goes **Healthy** within 2–3 minutes

---

## Troubleshooting

| Issue | Symptom | Fix |
|---|---|---|
| Nginx not installed | `Unit nginx.service could not be found` | Wrong package manager in User Data. Ubuntu needs `apt`, not `yum`. Connect via EC2 Instance Connect and run `apt install -y nginx && systemctl start nginx` |
| Health checks failing | Targets show Unhealthy | Check SG allows port 80 from `0.0.0.0/0`. NLB preserves client IP so you cannot restrict to NLB IP |
| NLB DNS timeout | `ERR_CONNECTION_TIMED_OUT` | Subnets not explicitly associated to the route table with IGW. Check **VPC → Route Tables → nlb-rt → Subnet associations** |
| Same instance on refresh | IP never changes in browser | Expected behaviour — NLB is flow-based. Use two browsers simultaneously or `curl` in a loop to see different instances respond |
| Targets not registering | Target group shows 0 targets | ASG may not be attached to target group. Check **ASG → Load balancing** tab — target group should be listed |

---

## Lessons Learned

1. **AMI and User Data must match** — Ubuntu uses `apt`, Amazon Linux uses `yum`/`dnf`. Wrong package manager = silent User Data failure = Nginx never installs = health checks fail.

2. **NLB has no security group** — Unlike ALB, you cannot attach an SG to NLB. Only EC2 instances get SGs. This also means you must allow `0.0.0.0/0` on the EC2 SG for health checks to pass.

3. **Cross-zone load balancing is OFF by default on NLB** — Always enable it. Without it, unequal instance distribution per AZ causes traffic imbalance.

4. **NLB is flow-based, not request-based** — A single TCP connection always goes to the same backend instance. This is a Layer 4 characteristic, not a bug.

5. **Subnet route table explicit association matters** — Creating a route table with an IGW route is not enough. You must explicitly associate the subnets to that route table, or they fall back to the default route table (which has no IGW route).

6. **Launch Template + ASG is best practice** — Not mandatory for NLB, but using ASG enables auto-healing, scaling policies, and multi-AZ instance distribution automatically.

---

## Cleanup

To avoid ongoing charges, delete resources in this order:

1. **Auto Scaling Groups** → `nlb-asg` → Delete (this terminates EC2 instances)
2. **Load Balancers** → `my-nlb` → Delete
3. **Target Groups** → `nlb-tg` → Delete
4. **Launch Templates** → `nlb-nginx-lt` → Delete
5. **Security Groups** → `nlb-ec2-sg` → Delete
6. **VPC** → `nlb-vpc` → Delete VPC (this also deletes subnets, route table, IGW)

> Wait for EC2 instances to fully terminate before deleting the VPC.

---

## Project Outcome

- NLB successfully created and active in ap-south-1 (Mumbai)
- 2 EC2 instances running Nginx registered as healthy targets across 2 AZs
- TCP traffic on port 80 load balanced across both instances
- Cross-zone load balancing enabled for even traffic distribution
- Auto Scaling Group ensuring minimum 2 instances always running
- NLB DNS publicly accessible and serving responses

---

## Author

**Saroj Behera**  
DevOps Intern | AWS & Cloud Enthusiast  
GitHub: [github.com/sarojbehera0610](https://github.com/sarojbehera0610)  
LinkedIn: [linkedin.com/in/saroj-behera-7bb84b204](https://linkedin.com/in/saroj-behera-7bb84b204)  
Email: sarojbehera0610@gmail.com