# 📈 AWS Auto Scaling Groups — Manual + Dynamic Scaling Policies

Master all AWS Auto Scaling strategies — **Manual, Target Tracking, Simple, and Step Scaling** — using a Payment Service simulation on EC2 with Nginx.

---

## 🗂️ Project Overview

This project demonstrates how to configure and test all major **Auto Scaling Group (ASG) policies** on AWS. Starting from a manually scaled ASG, it progressively adds dynamic scaling policies that automatically adjust instance count based on CPU utilization thresholds.

---

## 🎯 Scaling Policies Covered

```
ASG-Payment-Service
├── 1️⃣  Manual Scaling        → Desired: 2 | Min: 1 | Max: 3
├── 2️⃣  Target Tracking       → CPU Target: 10% (auto adjust)
├── 3️⃣  Simple Scaling        → CPU ≥ 20%  → +2 instances
└── 4️⃣  Step Scaling          → CPU ≥ 40%  → +1
                               → CPU ≥ 60%  → +2
                               → CPU ≥ 80%  → +3
```

---

## 🏗️ Architecture

```
         EC2 Auto Scaling Group
         ┌───────────────────────────────────────┐
         │          ASG-Payment-Service          │
         │                                       │
         │  ┌─────────────┐  ┌─────────────┐    │
         │  │  Instance 1 │  │  Instance 2 │    │
         │  │  ap-south-  │  │  ap-south-  │    │
         │  │    1a       │  │    1b       │    │
         │  └─────────────┘  └─────────────┘    │
         │                                       │
         │  Launch Template: payment-flipkart-v1 │
         │  Desired: 2 | Min: 1 | Max: 3         │
         └───────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   CloudWatch Alarms   │
              ├───────────────────────┤
              │ CPU ≥ 20% → Simple   │
              │ CPU ≥ 40% → Step +1  │
              │ CPU ≥ 60% → Step +2  │
              │ CPU ≥ 80% → Step +3  │
              └───────────────────────┘
```

---

## ✅ Prerequisites

- AWS Account with EC2 and Auto Scaling access
- Default VPC with subnets in **ap-south-1a** and **ap-south-1b**
- Key pair available (e.g. `saroj-asg-key.pem`)

---

## 🚀 Step-by-Step Setup

---

## PHASE 1 — Launch Template + Manual ASG

### Step 1 — Create Security Group ASG-SG

```
EC2 → Security Groups → Create Security Group
├── Name:        ASG-SG
├── Inbound Rules:
│   ├── SSH   → Port 22  → 0.0.0.0/0
│   └── HTTP  → Port 80  → 0.0.0.0/0
└── Outbound:    All traffic
```

> ✅ ASG-SG created with SSH + HTTP rules

---

### Step 2 — Create Launch Template

```
EC2 → Launch Templates → Create Launch Template
├── Template Name:  payment-flipkart-v1
├── AMI:            Ubuntu Server 24.04 LTS
├── Instance Type:  t3.micro
├── Key Pair:       saroj-asg-key.pem
└── Security Group: ASG-SG
```

> ✅ Launch template payment-flipkart-v1 created

---

### Step 3 — Add User Data to Launch Template

Under **Advanced Details → User Data**, paste:

```bash
#!/bin/bash
apt update && apt install nginx -y
echo "<h1>PAYMENT SERVICE - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx
```

> ✅ Each instance launched by this template will automatically serve the Payment page on port 80

---

### Step 4 — Create Manual ASG

```
EC2 → Auto Scaling Groups → Create Auto Scaling Group
├── Name:              ASG-Payment-Service
├── Launch Template:   payment-flipkart-v1
├── VPC:               Default VPC
├── Availability Zones: ap-south-1a + ap-south-1b ✓
├── Desired Capacity:  2
├── Minimum Capacity:  1
└── Maximum Capacity:  3
```

> ✅ ASG-Payment-Service created with Min:1 Desired:2 Max:3

---

### Step 5 — Verify Instances are Running

```
Auto Scaling Groups → ASG-Payment-Service → Instance Management
```

Expected:
```
Instance 1 → InService ✓ (ap-south-1a)
Instance 2 → InService ✓ (ap-south-1b)
```

> ✅ 2 Payment Service instances running across 2 Availability Zones

---

## PHASE 2 — Dynamic Scaling: Target Tracking Policy

### Step 6 — Create Target Tracking Policy

```
ASG-Payment-Service → Automatic Scaling → Create Dynamic Scaling Policy
├── Policy Type:    Target Tracking
├── Policy Name:    TargetTracking-Policy
├── Metric Type:    Average CPU Utilization
└── Target Value:   10%
```

> ✅ Target Tracking policy created — ASG will automatically scale in/out to maintain CPU at 10%

---

### Step 7 — Verify Target Tracking is Active

```
ASG → Automatic Scaling → Dynamic Scaling Policies
→ TargetTracking-Policy → Status: Active ✓
```

> ✅ No manual alarms needed — AWS manages this automatically

---

## PHASE 3 — Dynamic Scaling: Simple Scaling Policy

### Step 8 — Create CloudWatch Alarm for Simple Scaling

```
CloudWatch → Alarms → Create Alarm
→ Select Metric → EC2 → By Auto Scaling Group
├── ASG:        ASG-Payment-Service
├── Metric:     CPUUtilization
├── Condition:  Static ≥ 20%
├── Period:     1 minute
└── Alarm Name: CPU-High-ScaleUp
```

> ✅ CloudWatch alarm triggers when CPU ≥ 20%

---

### Step 9 — Create Simple Scaling Policy

```
ASG-Payment-Service → Automatic Scaling → Create Dynamic Scaling Policy
├── Policy Type:   Simple Scaling
├── Policy Name:   ScaleUp-Simple
├── CloudWatch Alarm: CPU-High-ScaleUp
├── Action:        Add
└── Instance Count: +2
```

> ✅ Simple Scaling: CPU ≥ 20% → +2 instances added immediately

---

### Step 10 — Verify Simple Scaling Policy is Active

```
ASG → Automatic Scaling → Dynamic Scaling Policies
→ ScaleUp-Simple → Status: Active ✓
```

> ✅ Simple scaling policy is live and waiting for the alarm to trigger

---

## PHASE 4 — Dynamic Scaling: Step Scaling Policy

### Step 11 — Create CloudWatch Alarms for Step Scaling

Create **3 separate alarms** in CloudWatch:

```
Alarm 1:
├── Name:      CPU-Medium
├── Condition: CPUUtilization ≥ 40%

Alarm 2:
├── Name:      CPU-High
├── Condition: CPUUtilization ≥ 60%

Alarm 3:
├── Name:      CPU-Critical
├── Condition: CPUUtilization ≥ 80%
```

> ✅ 3 Step scaling alarms created (40% / 60% / 80%)

---

### Step 12 — Create Step Scaling Policy (Scale Up)

```
ASG → Dynamic Scaling → Create → Step Scaling
├── Policy Name: ScaleUp-Step
├── Step Adjustments:
│   ├── CPU 40% - 60%  → Add +1 instance
│   ├── CPU 60% - 80%  → Add +2 instances
│   └── CPU ≥ 80%      → Add +3 instances
```

> ✅ Step ScaleUp policy: granular scale-up based on CPU severity

---

### Step 13 — Create Step Scaling Policy (Scale Down)

```
├── Policy Name: ScaleDown-Step
├── Step Adjustments:
│   ├── CPU ≤ 15%  → Remove -1 instance
│   └── CPU ≤ 10%  → Remove -2 instances
```

> ✅ Step ScaleDown policy: gradually remove instances as CPU drops

---

### Step 14 — Attach Step Alarms to Policy

```
ScaleUp-Step → Edit → Attach Alarms:
├── CPU-Medium  (≥40%) → +1 instance
├── CPU-High    (≥60%) → +2 instances
└── CPU-Critical(≥80%) → +3 instances
```

> ✅ Step alarms attached — scaling now responds to 3 different CPU thresholds

---

## PHASE 5 — Testing All Policies

### Step 15 — Test Manual Scaling

```
ASG-Payment-Service → Edit
→ Desired Capacity: 4 → Update
```

Expected:
```
Instance Management → 4/4 InService ✓
```

> ✅ Manual scaling works — 4 instances running

---

### Step 16 — Test Target Tracking

SSH into an instance and stress the CPU:

```bash
sudo apt install stress -y
stress --cpu 4 --timeout 300
```

Then watch:

```
ASG → Monitoring → CPU Utilization spike
→ ASG automatically adds instances to bring CPU back to 10%
```

> ✅ Target Tracking auto-scales to maintain target CPU

---

### Step 17 — Test Simple Scaling

```bash
# Stress CPU above 20% on instance
stress --cpu 4 --timeout 300
```

Expected:
```
CloudWatch → CPU-High-ScaleUp alarm → ALARM state
ASG → +2 instances added automatically
```

> ✅ Simple Scaling triggered — 2 new instances added

---

### Step 18 — Test Step Scaling

```bash
# Stress CPU to different thresholds
stress --cpu 4 --timeout 300
```

Expected behavior:

```
CPU ≥ 40% → CPU-Medium alarm → +1 instance
CPU ≥ 60% → CPU-High alarm   → +2 instances
CPU ≥ 80% → CPU-Critical     → +3 instances
```

> ✅ Step Scaling responds proportionally to CPU severity

---

### Step 19 — View ASG Activity History

```
ASG-Payment-Service → Activity Tab
→ Scaling Activities logged with timestamps
```

Expected entries:
```
Launching instance i-xxxx  (scale out)
Terminating instance i-xxxx (scale in)
```

> ✅ Full audit trail of all scale up/down events visible

---

## 📊 Scaling Policies Comparison

| Policy | Trigger | Action | Best Use Case |
|---|---|---|---|
| **Manual** | Human action | Desired: 2 → 4 | Predictable/scheduled load |
| **Target Tracking** | CPU = 10% | Auto adjust | Steady state maintenance |
| **Simple Scaling** | CPU ≥ 20% | +2 fixed | Single threshold response |
| **Step Scaling** | CPU 40/60/80% | +1 / +2 / +3 | Granular, proportional response |

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| Instances not launching | Check Launch Template AMI and instance type availability in AZ |
| Scaling not triggering | Verify CloudWatch alarm is in ALARM state, not OK |
| Target Tracking not scaling | Wait — it has a cooldown period before acting |
| Instances stuck in Pending | Check Security Group allows HTTP:80 and SSH:22 |
| Step scaling wrong threshold | Review step adjustment ranges — ensure no gaps between steps |

---

## 📁 File Structure

```
.
├── README.md
└── userdata/
    └── payment-userdata.sh      # Nginx setup for Payment Service
```

---

## 💡 Key Concepts Learned

- **Launch Templates** — Reusable EC2 configuration for ASGs
- **Manual Scaling** — Direct control over desired instance count
- **Target Tracking** — AWS auto-manages scaling to hit a metric target
- **Simple Scaling** — Single alarm triggers a fixed scaling action
- **Step Scaling** — Multiple thresholds trigger proportional scaling actions
- **CloudWatch Alarms** — Bridge between metrics and scaling actions
- **Cooldown Periods** — Prevent rapid repeated scaling actions

---

## 📌 References

- [Auto Scaling Dynamic Scaling Policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scale-based-on-demand.html)
- [Target Tracking Scaling Policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html)
- [Step and Simple Scaling Policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-simple-step.html)
- [CloudWatch Alarms for Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-instance-monitoring.html)
