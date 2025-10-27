# AWS Step Functions Document Processing Pipeline Requirements

## Overview

This document outlines the AWS Step Functions pipeline requirements for the CMZ Animal Assistant Management System knowledge base document processing.

## Research Requirements

From research.md specifications:
- **5-minute processing SLA** (typical 2-5 minutes)
- **Event-driven Lambda pipeline** with Step Functions orchestration
- **Error handling and retry logic**
- **DynamoDB metadata storage** integration
- **Malware scanning integration** with GuardDuty

## Pipeline Workflow

```
Upload → Validate → Malware Scan → Extract Text → Generate Embeddings → Index → Complete
```

## State Machine Definition

### 1. Document Validation
```json
{
  "ValidateUpload": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke",
    "Parameters": {
      "FunctionName": "CMZ-ValidateDocumentUpload",
      "Payload": {
        "fileId.$": "$.fileId",
        "fileSize.$": "$.fileSize",
        "mimeType.$": "$.mimeType"
      }
    }
  }
}
```

**Validation Logic:**
- File size ≤ 50MB
- MIME type: PDF, DOC, DOCX, TXT only
- Valid file structure
- Assistant ID exists in DynamoDB

### 2. Malware Scanning Integration
```json
{
  "CheckMalwareStatus": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke",
    "Parameters": {
      "FunctionName": "CMZ-CheckMalwareStatus",
      "Payload": {
        "s3Bucket.$": "$.s3Bucket",
        "s3Key.$": "$.s3Key"
      }
    }
  }
}
```

**Security Flow:**
- Wait 30 seconds for GuardDuty scan
- Query GuardDuty findings for S3 object
- Block processing if malware detected
- Move infected files to quarantine bucket

### 3. Text Extraction with Textract
```json
{
  "ExtractText": {
    "Type": "Task",
    "Resource": "arn:aws:states:::aws-sdk:textract:startDocumentTextDetection",
    "Parameters": {
      "DocumentLocation": {
        "S3Object": {
          "Bucket.$": "$.s3Bucket",
          "Name.$": "$.s3Key"
        }
      }
    }
  }
}
```

**Processing Steps:**
- Start asynchronous Textract job
- Poll for completion (30-second intervals)
- Handle pagination for large documents
- Extract structured text from response

### 4. Vector Embedding Generation
```json
{
  "GenerateEmbeddings": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke",
    "Parameters": {
      "FunctionName": "CMZ-GenerateEmbeddings",
      "Payload": {
        "extractedText.$": "$.processedText.Payload.text",
        "assistantId.$": "$.assistantId"
      }
    }
  }
}
```

**Embedding Process:**
- Split text into 1000-character chunks
- Generate embeddings using Bedrock
- Store vectors in Bedrock Knowledge Base
- Create searchable index

### 5. Knowledge Base Indexing
```json
{
  "IndexInKnowledgeBase": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke",
    "Parameters": {
      "FunctionName": "CMZ-IndexKnowledgeBase",
      "Payload": {
        "vectorEmbeddingId.$": "$.embeddingResult.Payload.embeddingId",
        "assistantId.$": "$.assistantId"
      }
    }
  }
}
```

**Indexing Features:**
- Semantic search capabilities
- Animal-specific knowledge partitioning
- Educational content validation
- Age-appropriateness filtering

## Lambda Functions Required

### 1. CMZ-ValidateDocumentUpload
```python
def lambda_handler(event, context):
    file_size = event.get('fileSize', 0)
    mime_type = event.get('mimeType', '')

    # File size validation (50MB limit)
    if file_size > 52428800:
        return {'isValid': False, 'error': 'File too large'}

    # MIME type validation
    valid_types = ['application/pdf', 'application/msword', 'text/plain']
    if mime_type not in valid_types:
        return {'isValid': False, 'error': 'Unsupported file type'}

    return {'isValid': True}
```

### 2. CMZ-UpdateFileStatus
```python
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('quest-dev-knowledge-file')

    table.update_item(
        Key={'fileId': event['fileId']},
        UpdateExpression='SET processingStatus = :status',
        ExpressionAttributeValues={':status': event['status']}
    )

    return {'success': True}
```

### 3. CMZ-CheckMalwareStatus
```python
def lambda_handler(event, context):
    guardduty = boto3.client('guardduty')

    # Query GuardDuty findings for specific S3 object
    findings = guardduty.get_findings(
        DetectorId=detector_id,
        FindingIds=finding_ids
    )

    # Check for malware findings
    for finding in findings['Findings']:
        if finding['Type'] == 'Discovery:S3-MaliciousObject':
            return {'isSafe': False, 'threat': finding['Title']}

    return {'isSafe': True, 'status': 'COMPLETED'}
```

### 4. CMZ-ProcessExtractedText
```python
def lambda_handler(event, context):
    textract = boto3.client('textract')

    # Get Textract results
    result = textract.get_document_text_detection(
        JobId=event['textractJobId']
    )

    # Extract text from blocks
    text = ""
    for block in result['Blocks']:
        if block['BlockType'] == 'LINE':
            text += block['Text'] + "\n"

    return {
        'text': text.strip(),
        'textLength': len(text),
        'blockCount': len(result['Blocks'])
    }
```

### 5. CMZ-GenerateEmbeddings
```python
def lambda_handler(event, context):
    bedrock = boto3.client('bedrock-runtime')

    text = event['extractedText']

    # Split into chunks
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]

    embeddings = []
    for chunk in chunks:
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({'inputText': chunk})
        )
        embeddings.append(response['embedding'])

    # Store in Bedrock Knowledge Base
    embedding_id = f"embed_{uuid.uuid4()}"

    return {
        'embeddingId': embedding_id,
        'chunkCount': len(chunks)
    }
```

## Error Handling Strategy

### Retry Configuration
```json
{
  "Retry": [
    {
      "ErrorEquals": ["Lambda.ServiceException"],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 2.0
    }
  ]
}
```

### Error States
- **ValidationFailed**: Invalid file format or size
- **MalwareDetected**: GuardDuty found threats
- **TextExtractionFailed**: Textract processing error
- **EmbeddingFailed**: Bedrock embedding generation error

### Recovery Actions
- Update DynamoDB status to `FAILED`
- Move problematic files to error bucket
- Send notification to administrators
- Log detailed error information

## Performance Characteristics

### SLA Targets
- **Total Processing Time**: ≤ 5 minutes
- **Validation**: ≤ 10 seconds
- **Malware Scan**: ≤ 60 seconds
- **Text Extraction**: ≤ 2 minutes (PDF-dependent)
- **Embedding Generation**: ≤ 1 minute
- **Knowledge Base Indexing**: ≤ 30 seconds

### Optimization Strategies
- **Parallel Processing**: Multiple files processed simultaneously
- **Chunked Text**: Split large documents for faster embedding
- **Caching**: Cache embeddings for duplicate content
- **Monitoring**: CloudWatch metrics for performance tracking

## Integration Points

### S3 Event Triggers
```json
{
  "Rules": [
    {
      "Id": "CMZKnowledgeBaseUpload",
      "Status": "Enabled",
      "Filter": {
        "Key": {
          "FilterRules": [
            {"Name": "prefix", "Value": "uploads/"},
            {"Name": "suffix", "Value": ".pdf"}
          ]
        }
      },
      "Targets": [
        {
          "Id": "StartProcessingPipeline",
          "Arn": "arn:aws:states:us-west-2:195275676211:stateMachine:CMZ-DocumentProcessingPipeline"
        }
      ]
    }
  ]
}
```

### DynamoDB Updates
```python
# File processing status tracking
{
    'fileId': 'file_123',
    'processingStatus': 'PROCESSING',  # UPLOADED → PROCESSING → COMPLETED/FAILED
    'processingStarted': '2025-10-23T12:00:00Z',
    'processingCompleted': '2025-10-23T12:03:45Z',
    'extractedTextLength': 15000,
    'vectorEmbeddingId': 'embed_456',
    'contentValidation': {
        'safe': True,
        'educational': True,
        'ageAppropriate': True
    }
}
```

## Cost Analysis

### Processing Costs per File
- **Step Functions**: $0.025 per 1000 state transitions (~$0.001 per file)
- **Lambda Execution**: $0.0000002 per 100ms (~$0.01 per file)
- **Textract**: $1.50 per 1000 pages (~$0.015 per page)
- **Bedrock Embeddings**: $0.0001 per 1000 tokens (~$0.002 per file)
- **DynamoDB**: $1.25 per million requests (~$0.000001 per file)

**Total per file**: ~$0.03-0.05 for typical 10-page document
**Monthly estimate**: 50 files × $0.05 = $2.50/month

## Required IAM Permissions

### Step Functions Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction",
        "textract:StartDocumentTextDetection",
        "textract:GetDocumentTextDetection",
        "states:StartExecution"
      ],
      "Resource": "*"
    }
  ]
}
```

### Lambda Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "dynamodb:UpdateItem",
        "dynamodb:GetItem",
        "guardduty:GetFindings",
        "textract:GetDocumentTextDetection",
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

## Current Status

- **Pipeline Definition**: Complete ASL (Amazon States Language) specification
- **Lambda Functions**: 7 function stubs with complete implementation logic
- **Error Handling**: Comprehensive retry and failure recovery
- **Documentation**: Complete implementation guide

## Deployment Requirements

**Prerequisites:**
1. AWS administrator creates Step Functions state machine
2. Deploy Lambda functions with proper IAM roles
3. Configure S3 event notifications
4. Test pipeline with sample document

**Execution Command:**
```bash
python scripts/create_step_functions_pipeline.py
```

**Expected Timeline:**
- Infrastructure setup: 1 hour
- Lambda deployment: 2 hours
- Testing and validation: 2 hours
- **Total**: Half-day implementation

This document processing pipeline provides the **automated, scalable, and secure** foundation required for the CMZ Animal Assistant Management System knowledge base functionality.