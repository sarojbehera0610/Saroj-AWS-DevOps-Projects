# 🟢 11 Auto Scaling Groups - Manual + Dynamic (Target/Simple/Step)

**ASG-Payment-Service → Launch Template → Manual(2) → Dynamic Policies**

## 🎯 Auto Scaling Policies Tree
Auto Scaling Policies
├── 1️⃣ MANUAL Scaling (Desired:2, Min:1, Max:3)
├── 2️⃣ DYNAMIC Scaling
│ ├── Target Tracking (CPU:10% - No conditions)
│ ├── Simple Scaling (CPU≥20% → +2 instances)
│ └── Step Scaling (Multiple CPU thresholds)

## **📋 COMPLETE PRODUCTION STEPS **

### **🚀 Launch Template + Manual ASG**

**Step 1: Create Security Group ASG-SG**
Security Groups → Create:
├── Name: ASG-SG
├── Inbound:
│ ├── SSH:22 | 0.0.0.0/0
│ └── HTTP:80 | 0.0.0.0/0

**#1: ASG-SG → SSH+HTTP rules**

**Step 2: Create Launch Template**
EC2 → Launch Templates → Create:
├── Template name: payment-flipkart-v1
├── AMI: Ubuntu Server 24.04 LTS
├── Instance type: t3.micro
├── Key pair: saroj-asg-key.pem
├── Security groups: ASG-SG

** #2: Launch template create**

**Step 3: Launch Template User Data**
Advanced → User data:

#!/bin/bash
apt update && apt install nginx -y
echo "<h1>PAYMENT SERVICE - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx

** #3: payment-flipkart-v1 → User data ✓**

**Step 4: Create Manual ASG**
Auto Scaling → Auto Scaling Groups → Create:
├── Name: ASG-Payment-Service
├── Launch template: payment-flipkart-v1
├── VPC: Default → AZs: ap-south-1a + ap-south-1b ✓
├── Desired: 2 | Min: 1 | Max: 3

** #4: ASG-Payment-Service → Min:1 Desired:2 Max:3**

**Step 5: Manual ASG Instances Launch**
ASG → Instance management → 2 instances launching

** #5: 2 Payment instances → InService ✓**

### **🎯 1️⃣ DYNAMIC - Target Tracking Policy**

**Step 6: Create Target Tracking Policy**
ASG-Payment-Service → Automatic scaling → Create dynamic scaling policy
├── Policy type: Target tracking
├── Metric type: Average CPU
├── Target value: 10%

** #6: Target Tracking → CPU 10% ✓**

**Step 7: Target Tracking Active**
Dynamic scaling → TargetTracking-Policy → Active

** #7: Target Tracking policy created**

### **⚡ 2️⃣ DYNAMIC - Simple Scaling Policy**

**Step 8: CloudWatch Alarm for Simple Scaling**
CloudWatch → Alarms → Create alarm → Select metric:
├── EC2 → Auto Scaling → ASG-Payment-Service
├── Metric: CPUUtilization
├── Condition: Static ≥ 20%
├── Alarm name: CPU-High-ScaleUp

** #8: CloudWatch CPU ≥20% alarm**

**Step 9: Create Simple Scaling Policy**
ASG → Dynamic scaling → Create → Simple scaling
├── Policy name: ScaleUp-Simple
├── Scale up → Instance count: +2
├── Alarm: CPU-High-ScaleUp

** #9: Simple Scaling → CPU≥20% → +2 ✓**

**Step 10: Simple Scaling Policy Active**
Dynamic scaling → ScaleUp-Simple → Active

** #10: Simple scaling policy created**

### **📈 3️⃣ DYNAMIC - Step Scaling Policy**

**Step 11: CloudWatch Alarms for Step Scaling**
Create 3 alarms:

CPU-Medium: ≥40%

CPU-High: ≥60%

CPU-Critical: ≥80%

** #11: 3 Step alarms (40%/60%/80%)**

**Step 12: Create Step Scaling Policy - Scale Up**
ASG → Dynamic scaling → Create → Step scaling
├── Policy name: ScaleUp-Step
├── Step adjustments:
│ ├── Lower threshold: 40% → +1
│ ├── Lower threshold: 60% → +2
│ └── Lower threshold: 80% → +3

** #12: Step ScaleUp → Multi-step ✓**

**Step 13: Create Step Scaling Policy - Scale Down**
Policy name: ScaleDown-Step
├── Step adjustments:
│ ├── Upper threshold: 15% → -1
│ └── Upper threshold: 10% → -2

** #13: Step ScaleDown → Multi-step ✓**

**Step 14: Attach Step Alarms**
ScaleUp-Step → Edit → Alarms:
├── CPU-Medium (40%) → +1
├── CPU-High (60%) → +2
├── CPU-Critical (80%) → +3

** #14: Step alarms attached**

### **🧪 Policy Testing**

**Step 15: Test Manual Scaling**
ASG → Edit → Desired capacity: 4 → Update
Instances → 4/4 InService ✓

**#15: Manual → 4 instances ✓**

**Step 16: Test Target Tracking**
Stress EC2 CPU → Monitoring → CPU spikes → Instances scale

** #16: Target Tracking scaling ✓**

**Step 17: Test Simple Scaling**
CPU >20% → Alarm triggers → +2 instances

** #17: Simple scaling → 6 instances ✓**

**Step 18: Test Step Scaling**
CPU 40% → +1 | 60% → +2 | 80% → +3

** #18: Step scaling → Dynamic instances ✓**

**Step 19: ASG Activity History**
ASG → Activity → Scaling activities logged

** #19: Activity history → Scale up/down ✓**

### **📊 Policies Comparison Table**
| Policy | Conditions | Scale Action | Use Case |
|--------|------------|--------------|----------|
| **Manual** | None | Desired:2→4 | Predictable load |
| **Target Tracking** | CPU=10% | Auto adjust | Steady state |
| **Simple Scaling** | CPU≥20% | +2 fixed | Single threshold |
| **Step Scaling** | CPU 40/60/80% | +1/+2/+3 | Granular control |
