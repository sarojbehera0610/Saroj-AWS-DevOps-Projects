# 🟢 12 ALB + Auto Scaling Groups (3 ASGs → 3 TGs → Path Routing)

**ASG-Home(2) → TG-Home → ALB → /**  
**ASG-Mobile(2) → TG-Mobile → ALB → /mobilepage/**  
**ASG-Payment(2) → TG-Payment → ALB → /payment/**

## 🎯 Multi-ASG Path-Based Architecture
Browser
↓ ALB-Amazon (1a+1b)
├── / → TG-Home → ASG-Home (2 instances)
├── /mobilepage/* → TG-Mobile → ASG-Mobile (2 instances)
└── /payment/* → TG-Payment → ASG-Payment (2 instances)

## **📋 COMPLETE PRODUCTION STEPS **

### **🖥️ 3 Manual Instances (Baseline Testing)**

**Step 1: Launch Home-Amazon Instance**
EC2 → Launch:
├── Name: Home-Amazon
├── Ubuntu 24.04 | t3.micro | Public IP: ENABLE ✓
├── Security Group: SG-Web-Public (SSH:22, HTTP:80)
├── User data:

#!/bin/bash
apt update && apt install nginx -y
echo "<h1>AMAZON HOME - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx

** #1: Home-Amazon Public IP ✓**

**Step 2: Launch Mobile-Amazon Instance**
Name: Mobile-Amazon
User data:

#!/bin/bash
apt update && apt install nginx -y
mkdir -p /var/www/html/mobilepage
echo "<h1>MOBILE PAGE - $(hostname)</h1>" > /var/www/html/mobilepage/index.html
ln -sf /var/www/html/mobilepage /usr/share/nginx/html/mobilepage
systemctl start nginx && systemctl enable nginx

** #2: Mobile-Amazon running**

**Step 3: Launch Payment-Amazon Instance**
Name: Payment-Amazon
User data:

#!/bin/bash
apt update && apt install nginx -y
mkdir -p /var/www/html/payment
echo "<h1>PAYMENT PAGE - $(hostname)</h1>" > /var/www/html/payment/index.html
ln -sf /var/www/html/payment /usr/share/nginx/html/payment
systemctl start nginx && systemctl enable nginx

** #3: Payment-Amazon running**
🎯 3 Target Groups
Step 4: Create TG-Home

Target Groups → Create:
├── Name: TG-Home
├── Protocol: HTTP:80 | VPC: Default
├── Health check: / | 200-299
**No targets registered yet**
 #4: TG-Home created

Step 5: Create TG-Mobile

Name: TG-Mobile
├── Health check: /mobilepage | 200-299
 #5: TG-Mobile created

Step 6: Create TG-Payment

Name: TG-Payment
├── Health check: /payment | 200-299
 #6: TG-Payment created

🚀 3 Launch Templates (Public IP Enabled)
Step 7: Create Home-LT

Launch Templates → Create:
├── Name: home-lt (v1)
├── Ubuntu 24.04 | t3.micro
├── **Network Interface → Auto-assign Public IP: ENABLE ✓**
├── Security Group: SG-Web-Public
├── User data: **Same as Home-Amazon**
 #7: home-lt → Public IP ENABLE ✓

Step 8: Create Mobile-LT

Name: mobile-lt (v1)
├── User data: **Same as Mobile-Amazon**
#8: mobile-lt created

Step 9: Create Payment-LT

Name: payment-lt (v1)
├── User data: **Same as Payment-Amazon**
 #9: payment-lt created

⚙️ 3 Auto Scaling Groups
Step 10: Create ASG-Home

Auto Scaling → Create ASG:
├── Name: ASG-Home
├── Launch template: home-lt
├── VPC: Default → AZs: ap-south-1a + ap-south-1b ✓
├── Desired: **2** | Min: **1** | Max: **3**
 #10: ASG-Home 2/1/3 ✓

Step 11: Create ASG-Mobile

Name: ASG-Mobile
├── Launch template: mobile-lt
├── Same AZs + Capacity
 #11: ASG-Mobile created

Step 12: Create ASG-Payment

Name: ASG-Payment
├── Launch template: payment-lt
 #12: ASG-Payment created

🔗 Attach Target Groups to ASGs
Step 13: ASG-Home → TG-Home

ASG-Home → Integrations → Load balancer:
├── Target group: **TG-Home** ✓ → Save
 #13: ASG-Home → TG-Home attached

Step 14: ASG-Mobile → TG-Mobile

ASG-Mobile → Integrations → **TG-Mobile** ✓
 #14: ASG-Mobile → TG-Mobile

Step 15: ASG-Payment → TG-Payment

ASG-Payment → Integrations → **TG-Payment** ✓
 #15: ASG-Payment → TG-Payment

⚖️ ALB with Path-Based Routing
Step 16: Create ALB-Amazon

Load Balancers → ALB:
├── Name: ALB-Amazon
├── Internet-facing | Default VPC
├── AZ Mappings: ap-south-1a + ap-south-1b ✓
├── Security Group: SG-Web-Public
├── Listener HTTP:80 → **Forward to: TG-Home** (Default)
 #16: ALB-Amazon creating

Step 17: ALB Listener Rules - Mobile Path

Listeners → HTTP:80 → **View/edit rules**:
├── **Add rule** → IF Path `/mobilepage/*` → **TG-Mobile**
 #17: Rule 1: /mobilepage/ → TG-Mobile*

Step 18: ALB Listener Rules - Payment Path

**Add another rule** → IF Path `/payment/*` → **TG-Payment**
 #18: Rule 2: /payment/ → TG-Payment*

Step 19: ALB DNS + Health Checks

ALB-Amazon → **DNS name** copied
Target Groups → **3 TGs → 2/2 Healthy each** ✓
 #19: ALB DNS + 6/6 Healthy targets

🧪 Multi-Path Testing
Step 20: Test Home Path

Browser: http://ALB-Amazon-DNS/
→ "AMAZON HOME - ip-xx-xx-xx-xx"
Refresh → Load balances 2 ASG-Home instances
 #20: ALB/ → Home ✓

Step 21: Test Mobile Path

http://ALB-Amazon-DNS/mobilepage/
→ "MOBILE PAGE - ip-xx-xx-xx-xx" 
Refresh → 2 ASG-Mobile instances
 #21: ALB/mobilepage/ → Mobile ✓

Step 22: Test Payment Path

http://ALB-Amazon-DNS/payment/
→ "PAYMENT PAGE - ip-xx-xx-xx-xx"
Refresh → 2 ASG-Payment instances
 #22: ALB/payment/ → Payment ✓

📊 ALB + ASG Integration Summary
Path	Target Group	ASG	Instances	Status
/	TG-Home	ASG-Home	2/2	✅ Healthy
/mobilepage/	TG-Mobile	ASG-Mobile	2/2	✅ Healthy
/payment/	TG-Payment	ASG-Payment	2/2	✅ Healthy
