# 🟢 02 MobaXterm Production SSH Access

**GUI Terminal → Ubuntu EC2 13.203.156.167**

## 🎬 Exact MobaXterm Connection Steps (Production Ready)

### **Step 1: Launch MobaXterm**
📱 Open MobaXterm Professional/Personal Edition
📂 Sessions → New session

### **Step 2: SSH Session Configuration** 
🔗 Session type: SSH
🌐 Remote host: 13.203.156.167
👤 Specify username: ubuntu
🔌 Port: 22

### **Step 3: Advanced SSH Settings**
⚙️ Click: "Advanced SSH settings" tab
🔑 ☑ "Use private key"
📄 Private key: Browse → saroj-ubuntu-prod-2026.pem
❌ NO Jump host / port forwarding

### **Step 4: Connect to Production**
✅ Click: OK
🔐 Accept host fingerprint (first time only)
🟢 Success: ubuntu@ip-172-31-47-200:~$

### **Step 5: Production Verification**
```bash
# Verify correct infrastructure
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
http://169.254.169.254/latest/meta-data/public-ipv4
# Output: 13.235.245.235 ✓

# Web server status
sudo systemctl status nginx
# Output: Active (running) ✓

Dual Terminal Production Strategy

MobaXterm	Interactive ops, SFTP, tabs	✅ Live
CMD SSH	CI/CD automation	✅ Verified
AWS Console	Emergency rescue	✅ Available

Target Infrastructure

Ubuntu EC2: 13.203.156.167 (Public IP)
Private IP: 172.31.12.91
User: ubuntu
Key: saroj-ubuntu-prod-2026.pem
Nginx: Active (Production web)
