# cloudformation/

Directory containing CloudFormation templates. The templates are written in YAML, with an accompanying README markdown document similarly named for each template.

## Contents

| Name                 | Links                                   | Description                                                                                   |
|----------------------|-----------------------------------------|-----------------------------------------------------------------------------------------------|
| `account-guardrails` | [Template](account-guardrails.yml) &#124; [Doc](account-guardrails.md) | Guardrails for IAM, tagging, budgets, CloudTrail, and notifications.                          |

---

## Documentation Guidelines for CloudFormation Templates

Each CloudFormation template in this directory should have a corresponding Markdown documentation file (`.md`) with the same base name. The documentation should include:

1. **Overview**
   - A concise summary of what the template provisions and its intended use case.

2. **Architecture Diagram**
   - Visual representation of the resources and their relationships.

3. **Parameter Reference**
   - Table listing all parameters, types, descriptions, and example values.

4. **Resource Outputs**
   - List and describe all outputs provided by the template.

5. **Security Considerations**
   - Highlight important security controls, exemptions, and best practices.

6. **Customization Guide**
   - Instructions for adapting the template to different teams, tags, or workflows.

7. **Deployment Instructions**
   - Step-by-step guide for deploying the template, including any manual prerequisites.

8. **Test Scenarios**
   - Suggested tests to validate the deployed resources and policies.

9. **Troubleshooting**
   - Common issues and solutions.

10. **Change Log**
    - Track significant updates to the template and documentation.

---

**Tip:**
Keep documentation up to date as templates evolve. Use clear, concise language and provide
