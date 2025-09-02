# account-guardrails.yml

Creates an IAM group with administrative access, enforces resource tagging and region restrictions, and applies guardrail policies to prevent untagged or out-of-region resource operations (with exemptions for global services and a designated breakglass admin). The template provisions CloudTrail for auditing (optionally enabled via a parameter), optionally sets up budget alerts and cost summary notifications via Lambda and SNS, and ensures all resources are consistently tagged for traceability.

## Features

### 1. **Parameterization & Metadata**
- All required parameters are present and logically grouped for the AWS Console UI.

| Parameter                     | Type         | Description                                               | Example                        |
|-------------------------------|--------------|-----------------------------------------------------------|--------------------------------|
| GroupName                     | String       | IAM group name                                            | `Nortal`                       |
| UserEmails                    | List<String> | IAM user emails to add to the group                       | `enrique.bejarano@nortal.com,iris.diaz@nortal.com,kc.stegbauer@nortal.com` |
| ExemptPrincipalArn            | String       | ARN of breakglass admin (optional)                        | `arn:aws:iam::...:user/breakglass` |
| ApplicationTag                | String       | Value for `cmz:application` tag                           | `cmz-animal-chatbots`          |
| TeamTag                       | String       | Value for `cmz:team` tag                                  | `nortal`                       |
| AllowedRegion                 | String       | Region for CloudTrail logging and allowed actions         | `us-west-2`                    |
| EnableCloudTrail              | String       | Enable CloudTrail logging and resources (`true`/`false`)  | `true`                         |
| ProvisionCostMonitors         | String       | Enable provisioning of budget alarms and cost monitoring resources (`true`/`false`) | `true` |
| EnableWeeklyCostNotification  | String       | Enable weekly cost summary notifications (`true`/`false`) | `true`                         |
| BudgetCap                     | Number       | Monthly budget cap in USD                                 | `150`                          |
| TeamNotificationEmail         | String       | Email for budget/cost notifications                       | `cmz-team@nortal.com`          |

### 2. **IAM Group & User Management**
- Creates an IAM group with the specified name.
- Attaches AWS managed `AdministratorAccess` policy.
- Adds users (from `UserEmails`) to the group.

### 3. **Custom Guardrail Policies**
- **Tag Enforcement Policy:** Denies create/modify/delete actions without required tags, with exemptions for global services and breakglass principal.
- **Region Enforcement Policy:** Denies actions outside the specified region, with exemptions for global services and breakglass principal.
- **Cost Explorer Policy:** Allows cost and budget viewing actions.
- **Billing Deny Policy:** Explicitly denies access to sensitive billing/account actions.

### 4. **CloudTrail (Optional)**
- Creates a CloudTrail trail and S3 bucket for logs, scoped to a specific region, **only if `EnableCloudTrail` is set to `true`**.
- S3 bucket is named uniquely per account and stack.

### 5. **Budget & Cost Monitoring (Optional)**
- **Controlled by `ProvisionCostMonitors` parameter.**
- Sets up a monthly budget with 80% and 100% alert thresholds, sending notifications to `TeamNotificationEmail`.
- SNS topic for cost summary notifications.
- Lambda function (Python 3.12) that:
  - Retrieves month-to-date costs for resources with required tags.
  - Publishes a summary to the SNS topic.
  - Includes error handling and logging.
- CloudWatch log group for Lambda.
- Lambda execution role with permissions for Cost Explorer, SNS, and CloudWatch Logs.
- EventBridge rule to trigger Lambda weekly.
- Lambda invoke permission for EventBridge.

### 6. **Tagging**
- All resources that support tags are explicitly tagged with `cmz:application` and `cmz:team`.

### 7. **Outputs**
- Outputs the IAM group name, SNS topic ARN, Lambda ARN, CloudTrail ARN, and CloudTrail bucket name (CloudTrail and cost monitoring outputs are conditional on their respective switches).

---

## Limitations & Gaps

1. **Breakglass Admin User Not Created**
   - The template expects an ARN for the breakglass admin but does not create the user or role. This must be done manually.

2. **SNS Topic Subscription**
   - The SNS topic subscription uses only `TeamNotificationEmail`. If you want multiple recipients, you must manually subscribe additional emails.

3. **User Creation**
   - The template adds users to the group but does not create the IAM users themselves. Users must exist prior to stack deployment.

4. **Global Services Exemption**
   - The list of global services in `NotAction` is static. If AWS adds new global services, they will not be automatically exempted.

5. **Budget Notification Limitation**
   - Only a single email (`TeamNotificationEmail`) receives budget alerts. If you want more, you must update the template or add them manually in the AWS Console.

6. **No Creation of Budget Notification IAM Role**
   - If you want budget notifications to trigger Lambda or SNS directly, you may need to create an IAM role for AWS Budgets (not present here).

7. **No Automated User/Breakglass Creation**
   - No automation for creating IAM users or the breakglass admin; these must be handled outside the template.

---

## Resource Outputs

- **GuardrailsGroupName**: IAM group name
- **CostSummaryTopicArn**: SNS topic ARN for cost notifications (if cost monitors enabled)
- **CostSummaryLambdaArn**: Lambda ARN for cost summary (if cost monitors enabled)
- **CloudTrailArn**: CloudTrail ARN (only if CloudTrail is enabled)
- **CloudTrailBucketName**: S3 bucket for CloudTrail logs (only if CloudTrail is enabled)

---

## Security Considerations

- The breakglass admin is exempt from guardrail denies; ensure this account is tightly controlled.
- Tag enforcement and region restrictions help prevent accidental or non-compliant resource creation.
- Billing and account info is explicitly denied to non-exempt users.

---

## Customization Guide

- To add more budget notification recipients, use an SNS topic as the budget subscriber and subscribe multiple emails.
- Update the list of global services in the policy as AWS adds new services.
- Adjust tag keys/values to match your organization’s standards.
- Use the `EnableCloudTrail` and `ProvisionCostMonitors` parameters to control whether CloudTrail and cost monitoring resources are provisioned.

---

## Deployment Instructions

### **Prerequisites**
- AWS CLI configured with sufficient permissions.
- The breakglass admin user/role must exist (if using `ExemptPrincipalArn`).
- All IAM users in `UserEmails` must already exist.

### **Deployment Steps**

1. **Create Breakglass Admin (Manual)**
   - Create an IAM user or role to serve as the breakglass admin.
   - Note the ARN for use in the `ExemptPrincipalArn` parameter.

2. **Create IAM Users (Manual)**
   - Ensure all users listed in `UserEmails` exist in IAM.

3. **Deploy the CloudFormation Stack**
   - Use the AWS Console or CLI:
     ```sh
     aws cloudformation deploy \
       --template-file /workspaces/CMZ-chatbots/infrastructure/aws/cloudformation/account-guardrails.yml \
       --stack-name cmz-account-guardrails \
       --capabilities CAPABILITY_NAMED_IAM \
       --parameter-overrides \
         GroupName=YourGroupName \
         UserEmails='["user1@example.com","user2@example.com"]' \
         ExemptPrincipalArn=arn:aws:iam::123456789012:user/breakglass \
         ApplicationTag=your-app \
         TeamTag=your-team \
         AllowedRegion=us-west-2 \
         EnableCloudTrail=true \
         ProvisionCostMonitors=true \
         BudgetCap=1000 \
         EnableWeeklyCostNotification=true \
         TeamNotificationEmail=team@example.com \
       --tags cmz:application=your-app cmz:team=your-team
     ```
   - Adjust parameter values as needed.

4. **Manually Confirm SNS Email Subscription**
   - The recipient of `TeamNotificationEmail` will receive a confirmation email from SNS. They must confirm the subscription to receive notifications.

5. **(Optional) Add More SNS Subscribers**
   - Manually add more email subscriptions to the SNS topic if needed.

---

## Test Scenarios

### **IAM Policy Enforcement**
- Try to create a resource without required tags → Denied.
- Try to create a resource with required tags → Allowed.
- Try to modify/delete a resource without required tags → Denied.
- Try to modify/delete a resource with required tags → Allowed.
- Try to perform actions outside the allowed region → Denied.
- Try to perform actions in the allowed region → Allowed.
- Try to access billing/account info → Denied.
- Try to use Cost Explorer → Allowed.
- Try to perform restricted actions as the breakglass admin → Allowed.

### **Budget & Cost Monitoring**
- If enabled, simulate exceeding 80% and 100% of the budget cap. Confirm that `TeamNotificationEmail` receives alerts.
- If enabled, confirm that the Lambda function runs weekly (or trigger manually).
- Check CloudWatch Logs for Lambda execution.
- Confirm that the SNS topic receives cost summary emails.

### **CloudTrail**
- If enabled, confirm that CloudTrail logs are delivered to the specified S3 bucket.

### **Resource Tagging**
- Check that all resources (where supported) are tagged with `cmz:application` and `cmz:team`.

---

## Troubleshooting

- If users do not receive budget or cost notifications, ensure the email subscription to SNS is confirmed.
- If IAM users are not created, create them manually before deploying the stack.
- Check CloudWatch Logs for Lambda execution errors.
- If CloudTrail or cost monitoring resources are not created, ensure `EnableCloudTrail` and `ProvisionCostMonitors` are set to `true` and the region matches.
