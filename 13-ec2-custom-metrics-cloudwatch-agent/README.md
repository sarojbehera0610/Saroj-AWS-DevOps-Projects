# 📊 EC2 Custom Metrics Monitoring with Amazon CloudWatch Agent

Monitor EC2 memory utilization and Nginx logs using the Amazon CloudWatch Agent with custom namespaces on Ubuntu.

---

## 🗂️ Project Overview

By default, AWS CloudWatch does **not** collect memory utilization metrics from EC2 instances. This project sets up the **CloudWatch Agent** on an Ubuntu EC2 instance to:

- Push **custom memory metrics** (`mem_used_percent`) to CloudWatch under the `Custom/EC2` namespace
- Stream **Nginx access and error logs** to CloudWatch Logs

---

## 🏗️ Architecture

```
EC2 Instance (Ubuntu)
    └── CloudWatch Agent
            ├── Metrics ──► CloudWatch (Custom/EC2 namespace)
            │                   └── mem_used_percent
            └── Logs ────► CloudWatch Logs
                                ├── nginx-access-log
                                └── nginx-error-log
```

---

## ✅ Prerequisites

- An AWS EC2 instance running **Ubuntu**
- An **IAM Role** attached to the EC2 instance with the following policies:
  - `CloudWatchAgentServerPolicy`
  - `AdministratorAccess` *(or scoped permissions as needed)*

---

## 🚀 Step-by-Step Setup

### Step 1 — Install Dependencies

```bash
sudo apt install -y curl unzip
```

---

### Step 2 — Download the CloudWatch Agent

```bash
curl -O https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
```

---

### Step 3 — Install the CloudWatch Agent

```bash
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
```

---

### Step 4 — Create the Agent Configuration File

```bash
vim cwagent-config.json
```

Paste the following configuration:

```json
{
  "metrics": {
    "namespace": "Custom/EC2",
    "metrics_collected": {
      "mem": {
        "measurement": [
          "mem_used_percent"
        ],
        "metrics_collection_interval": 60
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "nginx-access-log",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "nginx-error-log",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
```

---

### Step 5 — Attach IAM Role to EC2 Instance

1. Go to **AWS Console → EC2 → Instances**
2. Select your instance → **Actions → Security → Modify IAM Role**
3. Attach a role with the following policies:
   - `CloudWatchAgentServerPolicy`
   - `AdministratorAccess`

---

### Step 6 — Load Config and Start the Agent

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/root/cwagent-config.json \
  -s
```

> This command validates and loads your config, then starts the agent automatically.

---

### Step 7 — Verify the Agent is Running

```bash
sudo systemctl status amazon-cloudwatch-agent
```

Expected output:

```
● amazon-cloudwatch-agent.service - Amazon CloudWatch Agent
     Active: active (running)
```

---

### Step 8 — View Metrics in CloudWatch

1. Go to **AWS Console → CloudWatch → Metrics → All metrics**
2. Under **Custom Namespaces**, click **Custom/EC2**
3. Select **mem_used_percent** with your instance ID

> ⏱️ Allow **1–2 minutes** for metrics to appear after the agent starts.

---

### Step 9 — (Optional) Monitor Agent Logs Live

```bash
sudo tail -f /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```

You should see lines like:

```
I! Successfully written batch of X datapoints
```

every 60 seconds, confirming metrics are flowing to CloudWatch.

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| `status=1/FAILURE` on agent start | Config file not loaded. Re-run Step 6 with correct file path |
| `amazon-cloudwatch-agent.json does not exist` | You started the agent without running `fetch-config` first |
| Metrics not visible in CloudWatch | Check IAM Role is attached to the instance; wait 1–2 minutes |
| Wrong region in console | Ensure CloudWatch console region matches EC2 instance region |

---

## 📁 File Structure

```
.
├── README.md
└── cwagent-config.json       # CloudWatch Agent configuration
```

---

## 📌 References

- [Amazon CloudWatch Agent Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html)
- [CloudWatch Agent Configuration Reference](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html)
