# 🟢 09 Application Load Balancer (ALB) - Mobile + Products TGs

**2 Mobile EC2 → TG-Mobile:80 → ALB → /mobile**  
**2 Product EC2 → TG-Products:80 → ALB → /products**

## 🎯 ALB Path-Based Routing Architecture
Browser → ALB DNS
/mobile → TG-Mobile (Instance-Mobile01/02 → NGINX Mobile)
/products → TG-Products (Instance-Product01/02 → NGINX Products)

## **📋 COMPLETE PRODUCTION STEPS **

### **📱 Mobile Instances + Target Group**

**Step 1: Launch Instance-Mobile01**
EC2 → Launch Instance:
├── Name: Instance-Mobile01
├── AMI: Ubuntu Server 24.04 LTS
├── t3.micro
├── Key pair: saroj-alb-key.pem (Download)
├── Network: Default VPC → Default subnet
├── Auto-assign Public IP: ENABLE ✓

** #1: Instance-Mobile01 launching**

**Step 2: Mobile01 User Data (NGINX + Mobile Page)**
Advanced details → User data:

#!/bin/bash
apt update && apt install nginx -y
echo "<h1>MOBILE WEB - $(hostname)</h1>" > /var/www/html/index.html
systemctl start nginx && systemctl enable nginx

** #2: User data script**

**Step 3: Launch Instance-Mobile02 (Same config)**
Name: Instance-Mobile02

** #3: Both Mobile instances running → Public IPs ✓**

**Step 4: Create Target Group - TG-Mobile**
EC2 → Target Groups → Create target group:
├── Target type: Instances
├── Name: tg-mobile
├── Protocol: HTTP | Port: 80
├── VPC: Default VPC
├── Health check: / | HTTP:200-299

** #4: tg-mobile created**

**Step 5: Register Mobile Targets**
tg-mobile → Targets → Register targets:
├── Instance-Mobile01:80 ✓
├── Instance-Mobile02:80 ✓

** #5: 2 Mobile targets → Healthy ✓**

### **🛒 Product Instances + Target Group**

**Step 6: Launch Instance-Product01**
Name: Instance-Product01
User data:

bash
#!/bin/bash
apt update && apt install nginx -y
mkdir -p /var/www/html/products
echo "<h1>PRODUCTS WEB - $(hostname)</h1>" > /var/www/html/products/index.html
ln -sf /var/www/html/products /usr/share/nginx/html/products
systemctl start nginx && systemctl enable nginx

** #6: Product01 user data**

**Step 7: Launch Instance-Product02 (Same config)**
Name: Instance-Product02


** #7: Both Product instances running**

**Step 8: Create Target Group - TG-Products**
Target Groups → Create:
├── Name: tg-products
├── Protocol: HTTP | Port: 80
├── Health check: /products | HTTP:200-299

** #8: tg-products created**

**Step 9: Register Product Targets**
tg-products → Register:
├── Instance-Product01:80 ✓
├── Instance-Product02:80 ✓

** #9: 2 Product targets → Healthy ✓**

### **⚖️ Application Load Balancer (ALB)**

**Step 10: Create ALB**
EC2 → Load Balancers → Create Load Balancer → Application Load Balancer
├── Name: ALB-Mobile-Products
├── Scheme: Internet-facing
├── IP address type: IPv4
├── VPC: Default VPC → ALL subnets ✓
├── Security groups: Create new → HTTP(80), HTTPS(443)

** #10: ALB-Mobile-Products → Creating**

**Step 11: ALB Listeners - Mobile Path**
Listeners → Add listener → Forward to: tg-mobile
├── Rule: IF Path /mobile* → tg-mobile

** #11: Listener HTTP:80 → /mobile* → tg-mobile**

**Step 12: ALB Listeners - Products Path**
Add rule → IF Path /products* → tg-products
├── Default: tg-mobile (fallback)


** #12: Path `/products*` → tg-products**

**Step 13: ALB Creation Complete**
Review → Create load balancer

** #13: ALB Active → DNS name ✓**

### **🧪 Load Balancer Testing**

**Step 14: Test Mobile Path**
Browser → ALB-DNS/mobile
Expected: "MOBILE WEB - ip-xxx-xx-xx-xx"
Refresh: Load balances between Mobile01/02

** #14: ALB-DNS/mobile → Mobile instance ✓**

**Step 15: Test Products Path**
Browser → ALB-DNS/products
Expected: "PRODUCTS WEB - ip-xxx-xx-xx-xx"
Refresh: Load balances between Product01/02

** #15: ALB-DNS/products → Products instance ✓**

**Step 16: Target Health Verification**
Target Groups → tg-mobile → Targets → Healthy ✓
tg-products → Targets → Healthy ✓

** #16: All 4 targets Healthy ✓**

**Step 17: ALB Monitoring**
ALB → Monitoring → Healthy host count: 4/4

** #17: ALB metrics → 4 healthy targets**

## **📊 ALB Configuration Summary**
| Component | Instances | Target Group | Path Rule | Health Check |
|-----------|-----------|--------------|-----------|--------------|
| **Mobile** | Mobile01, Mobile02 | tg-mobile:80 | `/mobile*` | `/` 200-299 |
| **Products** | Product01, Product02 | tg-products:80 | `/products*` | `/products` 200-299 |
| **ALB** | ALB-Mobile-Products | Listeners HTTP:80 | Path-based routing | 4/4 Healthy ✓ |
