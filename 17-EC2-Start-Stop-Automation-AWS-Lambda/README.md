# EC2 Start/Stop Automation using AWS Lambda, EventBridge & SNS

## Project Overview

This project automates the **starting and stopping of an AWS EC2 instance** using a Python-based AWS Lambda function. The function is triggered on a schedule using **Amazon EventBridge**, and sends real-time **email/SMS notifications** via **Amazon SNS** every time an action is performed on the EC2 instance.

This is a real-world **DevOps automation project** that demonstrates cloud cost optimization by automatically managing EC2 instance lifecycle based on a schedule.

---

## Architecture
Amazon EventBridge (Scheduler)
|
| triggers every 10 minutes
↓
AWS Lambda Function (Python 3.12)
|
|── checks EC2 current state
|── starts if stopped / stops if running
|
├──→ Amazon EC2 Instance (start/stop action)
|
└──→ Amazon SNS Topic
|
└──→ Email / SMS Notification to you

---

## AWS Services Used

| Service | Purpose |
|---|---|
| AWS Lambda | Runs the Python automation code |
| Amazon EC2 | The instance being started and stopped |
| Amazon EventBridge | Schedules the Lambda trigger |
| Amazon SNS | Sends email/SMS notification after each action |
| AWS IAM | Provides permissions to Lambda |
| Amazon S3 | Stores Lambda code and project assets |
| Amazon CloudWatch | Logs Lambda execution details |

---

## Project Features

- Automatically checks the **current state** of EC2 instance before taking action
- If EC2 is `running` → **stops** it
- If EC2 is `stopped` → **starts** it
- If EC2 is in `pending` or `stopping` transition state → **skips** and waits for next trigger
- Sends **SNS notification** on every action including errors
- Fully serverless — no server needed to run the automation
- Saves AWS cost by stopping EC2 when not in use

---

## Prerequisites

- AWS Account (Free tier works)
- Basic knowledge of AWS Console
- An EC2 instance already created
- Gmail or mobile number for SNS notifications

---

## Step-by-Step Setup Guide

### Step 1 — Create EC2 Instance

1. Go to **AWS Console → EC2 → Launch Instance**
2. Choose **Amazon Linux 2 AMI** (Free tier eligible)
3. Select instance type: `t2.micro`
4. Configure security group — allow SSH (port 22)
5. Launch and download the key pair `.pem` file
6. Copy the **Instance ID** (format: `i-0xxxxxxxxxxxxxxxxx`)

---

### Step 2 — Create S3 Bucket

1. Go to **AWS Console → S3 → Create bucket**
2. Enter bucket name: `ec2-lambda-project-bucket` (must be globally unique)
3. Leave default settings and click **Create bucket**

---

### Step 3 — Create SNS Topic and Subscription

1. Go to **AWS Console → SNS → Topics → Create topic**
2. Type: `Standard`
3. Name: `EC2-Notification-Topic`
4. Click **Create topic**
5. Copy the **Topic ARN** — you will need this in the Lambda code
6. Click **Create subscription**
7. Protocol: `Email` or `SMS`
8. Endpoint: your email address or `+91XXXXXXXXXX` (mobile number)
9. Click **Create subscription**
10. If Email — check inbox and click **Confirm subscription** link
11. Verify status shows **Confirmed** in SNS → Subscriptions

---

### Step 4 — Create IAM Role for Lambda

1. Go to **AWS Console → IAM → Roles → Create role**
2. Trusted entity: **AWS service → Lambda**
3. Attach the following policies:
   - `AmazonEC2FullAccess`
   - `AWSLambdaBasicExecutionRole`
   - `AmazonSNSFullAccess`
4. Role name: `EC2-Lambda-Role`
5. Click **Create role**

---

### Step 5 — Create Lambda Function

1. Go to **AWS Console → Lambda → Create function**
2. Select **Author from scratch**
3. Function name: `EC2-Start-Stop`
4. Runtime: **Python 3.12**
5. Click **Create function**

---

### Step 6 — Add Python Code to Lambda

1. In the Lambda function, go to **Code tab**
2. Delete the existing default code
3. Paste the following Python code:

```python
import boto3

INSTANCE_ID = "i-03310f0c47f48847d"
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:051997448832:EC2-Notification-Topic"
REGION = "ap-south-1"

ec2 = boto3.client("ec2", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)


def lambda_handler(event, context):
    try:
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        current_state = response["Reservations"][0]["Instances"][0]["State"]["Name"]

        print(f"[INFO] Current EC2 state: {current_state}")

        if current_state == "stopped":
            ec2.start_instances(InstanceIds=[INSTANCE_ID])
            message = f"EC2 instance {INSTANCE_ID} was STOPPED → now STARTING."
            subject = "EC2 Instance Started by Lambda"

        elif current_state == "running":
            ec2.stop_instances(InstanceIds=[INSTANCE_ID])
            message = f"EC2 instance {INSTANCE_ID} was RUNNING → now STOPPING."
            subject = "EC2 Instance Stopped by Lambda"

        elif current_state in ["pending", "stopping"]:
            message = f"EC2 instance {INSTANCE_ID} is in transition state: {current_state}. No action taken."
            subject = "EC2 Instance In Transition — No Action"

        else:
            message = f"EC2 instance {INSTANCE_ID} is in unexpected state: {current_state}. No action taken."
            subject = "EC2 Lambda — Unexpected State"

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject
        )

        print(f"[SUCCESS] {message}")
        return {"statusCode": 200, "body": message}

    except Exception as e:
        error_msg = f"[ERROR] Exception for instance {INSTANCE_ID}: {str(e)}"
        print(error_msg)
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=error_msg,
            Subject="EC2 Lambda Error"
        )
        return {"statusCode": 500, "body": error_msg}
```

4. Update `INSTANCE_ID` with your actual EC2 Instance ID
5. Update `SNS_TOPIC_ARN` with your actual SNS Topic ARN
6. Click **Deploy**

---

### Step 7 — Attach IAM Role to Lambda

1. Go to **Lambda → EC2-Start-Stop → Configuration tab**
2. Click **Permissions → Edit execution role**
3. Select existing role: `EC2-Lambda-Role`
4. Click **Save**

---

### Step 8 — Increase Lambda Timeout

1. Go to **Lambda → Configuration → General configuration → Edit**
2. Change timeout from `3 seconds` to `30 seconds`
3. Click **Save**

---

### Step 9 — Create EventBridge Rule

1. Go to **AWS Console → Amazon EventBridge → Rules → Create rule**
2. Name: `EC2-Start-Stop-Schedule`
3. Rule type: **Schedule**
4. Click **Next**
5. Schedule type: **Rate-based schedule**
6. Enter rate expression:
Every 10 minutes (for testing)
rate(10 minutes)
Start EC2 at 9:00 AM IST Monday to Friday
cron(30 3 ? * MON-FRI *)
Stop EC2 at 6:00 PM IST Monday to Friday
cron(30 12 ? * MON-FRI *)

7. Click **Next**
8. Target: **AWS service → Lambda function**
9. Select function: `EC2-Start-Stop`
10. Click **Next → Create a new role → Next → Create rule**

---

### Step 10 — Add EventBridge as Lambda Trigger

1. Go to **Lambda → EC2-Start-Stop → Configuration → Triggers**
2. Click **Add trigger**
3. Source: **EventBridge (CloudWatch Events)**
4. Select: **Use existing rule**
5. Rule: `EC2-Start-Stop-Schedule`
6. Enable trigger: **checked**
7. Click **Add**

---

### Step 11 — Test the Lambda Function

1. Go to **Lambda → Test tab**
2. Create new test event with name `TestEvent`
3. Use default empty JSON `{}`
4. Click **Test**
5. Verify output shows:
[INFO] Current EC2 state: running
[SUCCESS] EC2 instance i-xxxx was RUNNING → now STOPPING.

6. Go to **EC2 → Instances** and verify state changed
7. Check email or SMS for SNS notification

---

### Step 12 — Verify in CloudWatch Logs

1. Go to **Lambda → Monitor tab → View CloudWatch logs**
2. Click the latest log stream
3. You should see:
[INFO] Current EC2 state: stopped
[SUCCESS] EC2 instance i-xxxx was STOPPED → now STARTING.

---

## Project Output

After successful setup you will see:

- EC2 instance **automatically toggling** between started and stopped states
- **CloudWatch logs** showing every execution with timestamps
- **SNS notification** delivered to your email or mobile after every Lambda run

---

## Important Notes

- AWS EventBridge cron expressions use **UTC timezone** — subtract 5 hours 30 minutes for IST
- Always **disable the EventBridge rule** after testing to avoid unnecessary charges
- Free tier EC2 gives **750 hours/month** — frequent toggling will consume these hours faster
- Lambda itself is free for the first **1 million requests/month** under free tier

---

## Cleanup — Avoid Unnecessary Charges

| Resource | Action |
|---|---|
| EventBridge Rule | Disable or Delete |
| EC2 Instance | Stop or Terminate |
| Lambda Function | Keep (free tier) or Delete |
| SNS Topic | Delete if not needed |
| S3 Bucket | Empty and Delete |

---

## Author

**Saroj Behera**
DevOps Intern | AWS | Linux | Docker | Kubernetes

- GitHub: [github.com/sarojbehera0610](https://github.com/sarojbehera0610)
- LinkedIn: [linkedin.com/in/saroj-behera-7bb84b204](https://linkedin.com/in/saroj-behera-7bb84b204)
- Email: sarojbehera0610@gmail.com