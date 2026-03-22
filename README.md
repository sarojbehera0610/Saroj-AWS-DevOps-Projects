# 🚀 Saroj AWS DevOps Projects

**A hands-on portfolio of production-grade AWS infrastructure deployments — built from scratch, documented step-by-step.**

---

## 👨‍💻 About Me

I am a DevOps Engineer in the making — currently mastering **Linux** and **AWS** with a focus on building real production-ready infrastructure. Every project in this repository is something I have personally deployed, debugged, and documented.

**My Learning Path:**

```
✅ Linux Administration     → Completed
🔄 AWS Cloud (Core + Advanced) → 95% Complete (1-2 topics remaining)
⏳ DevOps Tools             → Coming Next
   ├── Git & GitHub
   ├── Docker & Containers
   ├── Kubernetes (K8s)
   ├── Terraform (IaC)
   ├── Jenkins / GitHub Actions (CI/CD)
   └── Prometheus + Grafana (Monitoring)
```

---

## 🛠️ Tech Stack

![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)

---

## 📚 AWS Projects Portfolio

### ✅ Completed Projects (14/14)

| # | Project | Key Concepts | Difficulty |
|---|---|---|---|
| 01 | [Ubuntu EC2 Production Deployment](./01-ubuntu-ec2-fresh/) | EC2, Nginx, UFW, Security Groups | 🟢 Beginner |
| 02 | [MobaXterm SSH Access](./02-mobaxterm-ssh-access/) | GUI SSH, PEM Keys, Remote Access | 🟢 Beginner |
| 03 | [Key-Based Authentication](./03-keybase-authentication/) | ssh-keygen, authorized_keys, Passwordless SSH | 🟡 Intermediate |
| 04 | [EBS Production Volume Mount](./04-ebs-volume-logs/) | gp3, fdisk, ext4, fstab UUID | 🟡 Intermediate |
| 05 | [EFS Multi-AZ Shared Storage](./05-efs-multi-az/) | NFS, Multi-AZ, Shared Mount, fstab | 🟡 Intermediate |
| 06 | [VPC Public/Private + NAT Gateway](./06-vpc-public-private/) | Custom VPC, Subnets, IGW, NAT, 2-Tier | 🟡 Intermediate |
| 07 | [VPC Cross-Region Peering](./07-vpc-peering-cross-region/) | VPC Peering, Mumbai↔Virginia, /32 Routes | 🔴 Advanced |
| 08 | [VPC Endpoints + Cross-Region Peering](./08-vpc-endpoints-peering/) | EC2 Connect Endpoint, Private Access | 🔴 Advanced |
| 09 | [ALB Path-Based Routing](./09-alb-mobile-products-load-balancer/) | ALB, Target Groups, Path Rules | 🟡 Intermediate |
| 10 | [VPC Best Practices + ALB](./10-vpc-best-practices-alb/) | Private Web Servers, SG Chaining, HA | 🔴 Advanced |
| 11 | [Auto Scaling — Manual + Dynamic](./11-autoscaling-policies/) | ASG, Target Tracking, Simple, Step Scaling | 🔴 Advanced |
| 12 | [ALB + ASG Path-Based Integration](./12-alb-asg-integration/) | 3 ASGs, 3 TGs, ALB Path Routing | 🔴 Advanced |
| 13 | [CloudWatch Agent — Manual Setup](./13-ec2-custom-metrics-cloudwat.../) | Custom Metrics, CWAgent, Namespace | 🟡 Intermediate |
| 14 | [CloudWatch Agent — Wizard Setup](./14-ec2-cloudwatch-agent-wizard-setup/) | Wizard Config, Logs, mem_used_percent | 🟡 Intermediate |

---

## 🏗️ Architecture Skills Demonstrated

```
Networking
├── Custom VPC Design (CIDR, Subnets, Route Tables)
├── Internet Gateway + NAT Gateway
├── VPC Peering (Same Region + Cross-Region)
├── VPC Endpoints (EC2 Instance Connect)
└── Security Group Chaining

Compute
├── EC2 Launch (AMI, Instance Types, User Data)
├── Auto Scaling Groups (Manual + Dynamic Policies)
├── Launch Templates (v1, Public IP config)
└── Multi-AZ High Availability

Load Balancing
├── Application Load Balancer (ALB)
├── Path-Based Routing (/home, /mobile, /payment)
├── Target Groups (Health Checks, Registration)
└── ALB + ASG Integration

Storage
├── EBS (gp3, fdisk, ext4, UUID fstab mount)
└── EFS (Multi-AZ NFS shared storage)

Monitoring
├── CloudWatch Custom Metrics (mem_used_percent)
├── CloudWatch Agent (Manual JSON + Wizard)
├── CloudWatch Logs (Nginx access + error)
└── CloudWatch Alarms (CPU thresholds)

Security
├── Key-Based SSH Authentication
├── SSH Key Generation (ssh-keygen)
├── UFW Firewall Configuration
└── IAM Roles (CloudWatch Agent)
```

---

## 📈 Learning Progress

```
Linux Administration
████████████████████  100% ✅ Complete

AWS Core Services
████████████████████  100% ✅ Complete
  ✅ EC2, EBS, EFS
  ✅ VPC, Subnets, IGW, NAT
  ✅ Security Groups, IAM
  ✅ ALB, Target Groups

AWS Advanced Services
██████████████████░░   90% 🔄 In Progress
  ✅ Auto Scaling Groups
  ✅ CloudWatch Agent + Metrics
  ✅ VPC Peering + Endpoints
  ⏳ Route 53 (DNS)
  ⏳ S3 + CloudFront

DevOps Tools
░░░░░░░░░░░░░░░░░░░░    0% ⏳ Coming Next
  ⏳ Docker + Containers
  ⏳ Kubernetes (K8s)
  ⏳ Terraform (IaC)
  ⏳ Jenkins / GitHub Actions
  ⏳ Prometheus + Grafana
```

---

## 🎯 What's Coming Next

```
Phase 3 — DevOps Tools (Starting Soon)
├── 🐳 Docker          → Containerize applications
├── ☸️  Kubernetes      → Container orchestration
├── 🏗️  Terraform       → Infrastructure as Code
├── 🔄 CI/CD Pipelines → Jenkins + GitHub Actions
└── 📊 Monitoring      → Prometheus + Grafana
```

---

## 💡 Key Takeaways From This Journey

- **Built everything from scratch** — no wizards skipped, no shortcuts taken
- **Debugged real production issues** — IAM role not attached, /16 vs /32 routes, missing config files
- **Documented every step** — each project has a complete README with architecture diagrams
- **Multi-region deployments** — Mumbai + N.Virginia cross-region setups
- **Security-first mindset** — private subnets, SG chaining, key-based auth throughout

---

## 📬 Connect With Me

[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sarojbehera0610)

---

> **"Learning by doing — every error is a lesson, every fix is a win."** 🚀
