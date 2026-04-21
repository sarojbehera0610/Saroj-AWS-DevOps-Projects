import boto3

INSTANCE_ID = "i-03310f0c47f48847d"          # Replace with your EC2 Instance ID
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:051997448832:EC2-Notification-Topic"  # Replace with your SNS ARN
REGION = "ap-south-1"                         # Your AWS region

ec2 = boto3.client("ec2", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)


def lambda_handler(event, context):
    try:
        # Step 1 — Check current state of the EC2 instance
        response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
        current_state = response["Reservations"][0]["Instances"][0]["State"]["Name"]

        print(f"[INFO] Current EC2 state: {current_state}")

        # Step 2 — Toggle based on current state
        if current_state == "stopped":
            # Instance is stopped → START it
            ec2.start_instances(InstanceIds=[INSTANCE_ID])
            message = f"EC2 instance {INSTANCE_ID} was STOPPED → now STARTING."
            subject = "EC2 Instance Started by Lambda"

        elif current_state == "running":
            # Instance is running → STOP it
            ec2.stop_instances(InstanceIds=[INSTANCE_ID])
            message = f"EC2 instance {INSTANCE_ID} was RUNNING → now STOPPING."
            subject = "EC2 Instance Stopped by Lambda"

        elif current_state in ["pending", "stopping"]:
            # Instance is in transition — do nothing, wait for next trigger
            message = f"EC2 instance {INSTANCE_ID} is currently in transition state: {current_state}. No action taken."
            subject = "EC2 Instance In Transition — No Action"

        else:
            message = f"EC2 instance {INSTANCE_ID} is in unexpected state: {current_state}. No action taken."
            subject = "EC2 Lambda — Unexpected State"

        # Step 3 — Send SNS notification
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject
        )

        print(f"[SUCCESS] {message}")
        return {
            "statusCode": 200,
            "body": message
        }

    except Exception as e:
        error_msg = f"[ERROR] Exception occurred for instance {INSTANCE_ID}: {str(e)}"
        print(error_msg)

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=error_msg,
            Subject="EC2 Lambda Error"
        )

        return {
            "statusCode": 500,
            "body": error_msg
        }