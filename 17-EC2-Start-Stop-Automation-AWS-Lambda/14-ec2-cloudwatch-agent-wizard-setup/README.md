# 📊 EC2 Custom Metrics Monitoring with Amazon CloudWatch Agent (Wizard Setup)

Monitor EC2 memory, disk, swap utilization and Nginx logs using the Amazon CloudWatch Agent configured via the **interactive wizard** on Ubuntu.

---

## 🗂️ Project Overview

By default, AWS CloudWatch does **not** collect memory utilization metrics from EC2 instances. This project sets up the **CloudWatch Agent** on an Ubuntu EC2 instance using the built-in **configuration wizard** to:

- Push **custom metrics** (`mem_used_percent`, `disk_used_percent`, `swap_used_percent`, `diskio`) to CloudWatch under the **CWAgent** namespace
- Stream **Nginx access and error logs** to CloudWatch Logs with **7-day retention**

---

## 🏗️ Architecture

```
EC2 Instance (Ubuntu)
    └── CloudWatch Agent (Wizard Configured)
            ├── Metrics ──► CloudWatch (CWAgent namespace)
            │                   ├── mem_used_percent
            │                   ├── disk_used_percent
            │                   ├── disk_inodes_free
            │                   ├── diskio_io_time
            │                   └── swap_used_percent
            └── Logs ────► CloudWatch Logs
                                ├── nginx-access-log  (7 days retention)
                                └── nginx-error-log   (7 days retention)
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

### Step 4 — Attach IAM Role to EC2 Instance

1. Go to **AWS Console → EC2 → Instances**
2. Select your instance → **Actions → Security → Modify IAM Role**
3. Attach a role with the following policies:
   - `CloudWatchAgentServerPolicy`
   - `AdministratorAccess`

---

### Step 5 — Run the Configuration Wizard

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

Answer the wizard questions as follows:

```
On which OS are you planning to use the agent?
► 1. linux

Are you using EC2 or On-Premises hosts?
► 1. EC2

Which user are you planning to run the agent?
► 2. root

Do you want to turn on StatsD daemon?
► 2. no

Do you want to monitor metrics from CollectD?
► 2. no

Do you want to monitor any host metrics? e.g. CPU, memory, etc.
► 1. yes

Do you want to monitor cpu metrics per core?
► 2. no

Do you want to add ec2 dimensions (ImageId, InstanceId, InstanceType, AutoScalingGroupName)?
► 1. yes

Do you want to aggregate ec2 dimensions (InstanceId)?
► 1. yes

Would you like to collect your metrics at high resolution (sub-minute resolution)?
► 4. 60s

Which default metrics config do you want?
► 2. Standard

Are you satisfied with the above config?
► 1. yes

Do you have any existing CloudWatch Log Agent configuration file to import for migration?
► 2. no

Do you want to monitor any log files?
► 1. yes

Log file path:
► /var/log/nginx/access.log

Log group name:
► nginx-access-log

Log group class:
► 1. STANDARD

Log stream name:
► {instance_id}

Log Group Retention in days:
► 5  (which maps to 7 days)

Do you want to specify any additional log files to monitor?
► 1. yes

Log file path:
► /var/log/nginx/error.log

Log group name:
► nginx-error-log

Log group class:
► 1. STANDARD

Log stream name:
► {instance_id}

Log Group Retention in days:
► 5  (which maps to 7 days)

Do you want to specify any additional log files to monitor?
► 2. no

Do you want the CloudWatch agent to also retrieve X-ray traces?
► 2. no

Do you want to store the config in the SSM parameter store?
► 2. no
```

> ✅ The wizard saves the config automatically to `/opt/aws/amazon-cloudwatch-agent/bin/config.json`

---

### Step 6 — Verify the Generated Config (Optional)

```bash
cat /opt/aws/amazon-cloudwatch-agent/bin/config.json
```

The generated config should look like this:

```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_class": "STANDARD",
            "log_group_name": "nginx-access-log",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 7
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_class": "STANDARD",
            "log_group_name": "nginx-error-log",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 7
          }
        ]
      }
    }
  },
  "metrics": {
    "aggregation_dimensions": [["InstanceId"]],
    "append_dimensions": {
      "AutoScalingGroupName": "${aws:AutoScalingGroupName}",
      "ImageId": "${aws:ImageId}",
      "InstanceId": "${aws:InstanceId}",
      "InstanceType": "${aws:InstanceType}"
    },
    "metrics_collected": {
      "disk": {
        "measurement": ["used_percent", "inodes_free"],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "diskio": {
        "measurement": ["io_time"],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "mem": {
        "measurement": ["mem_used_percent"],
        "metrics_collection_interval": 60
      },
      "swap": {
        "measurement": ["swap_used_percent"],
        "metrics_collection_interval": 60
      }
    }
  }
}
```

---

### Step 7 — Start the Agent with the Generated Config

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json \
  -s
```

---

### Step 8 — Verify the Agent is Running

```bash
sudo systemctl status amazon-cloudwatch-agent
```

Expected output:

```
● amazon-cloudwatch-agent.service - Amazon CloudWatch Agent
     Active: active (running)
```

---

### Step 9 — Monitor Agent Logs Live (Optional)

```bash
sudo tail -f /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log
```

You should see lines like:

```
I! Successfully written batch of X datapoints
```

every 60 seconds confirming metrics are flowing to CloudWatch.

---

### Step 10 — View Metrics and Logs in CloudWatch

**Metrics:**
1. Go to **AWS Console → CloudWatch → Metrics → All metrics**
2. Under **Custom Namespaces** → click **CWAgent**
3. You should see `mem_used_percent`, `disk_used_percent`, `swap_used_percent` etc.

**Logs:**
1. Go to **AWS Console → CloudWatch → Log groups**
2. You should see:
   - `nginx-access-log`
   - `nginx-error-log`

> ⏱️ Allow **1–2 minutes** after starting the agent for metrics and logs to appear.

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| `Active: activating (auto-restart)` | Config not loaded. Re-run Step 7 with correct file path |
| Metrics not visible in CloudWatch | Check IAM Role is attached to the instance; wait 1–2 minutes |
| Wrong namespace shown | Wizard uses `CWAgent` namespace by default (not `Custom/EC2`) |
| Logs not appearing | Ensure Nginx is running and log files exist at the specified paths |
| Wrong region in console | Ensure CloudWatch console region matches your EC2 instance region |

---

## 📁 File Structure

```
.
├── README.md
└── /opt/aws/amazon-cloudwatch-agent/bin/config.json   # Auto-generated by wizard
```

---

## 🆚 Wizard vs Manual Config

| | Wizard | Manual JSON |
|---|---|---|
| Namespace | `CWAgent` | `Custom/EC2` (customizable) |
| Setup | Interactive Q&A | Edit JSON directly |
| Metrics | Standard preset | Fully custom |
| Best for | Quick setup | Fine-grained control |

---

## 📌 References

- [Amazon CloudWatch Agent Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html)
- [CloudWatch Agent Configuration Wizard](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create-cloudwatch-agent-configuration-file-wizard.html)
- [CloudWatch Agent Configuration Reference](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html)
