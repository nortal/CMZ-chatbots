# Knowledge Base Architecture Research for CMZ Animal Assistant System

**Document Version**: 1.0
**Date**: 2025-10-23
**Author**: Claude Code Research
**Status**: Architectural Research & Recommendations

---

## Executive Summary

This document provides comprehensive architectural guidance for implementing a document processing and knowledge base management system for the CMZ Animal Assistant chatbot platform. The system must support secure upload of educational documents, process them within 5 minutes, store up to 500MB per animal assistant, and make content searchable during conversations.

**Key Recommendations**:
- **Managed Services First**: Use AWS Bedrock Knowledge Bases for RAG implementation (vs custom)
- **Serverless Architecture**: Lambda + EventBridge for scalable, pay-per-use processing
- **Security-First**: GuardDuty Malware Protection + two-bucket quarantine pattern
- **Cost Optimization**: Binary embeddings reduce vector storage costs by 30-50%
- **Existing Pattern Alignment**: Integrate with CMZ DynamoDB/S3 utilities and OpenAPI patterns

**Estimated Monthly Cost**: $15-30 for moderate usage (100 documents/month, 1000 queries/month)

---

## 1. File Upload and Validation

### Architectural Decision: Two-Bucket Quarantine Pattern with GuardDuty

**Recommended Approach**: Implement a security-focused upload workflow that separates untrusted uploads from production storage.

#### Architecture Components

```
User Upload → S3 Quarantine Bucket → GuardDuty Scan → S3 Production Bucket
                                    ↓
                              EventBridge → Lambda → DynamoDB (metadata)
```

#### AWS Services

1. **Amazon S3 (Two Buckets)**
   - **Quarantine Bucket**: `cmz-knowledge-quarantine` - Temporary storage for uploaded files
   - **Production Bucket**: `cmz-knowledge-production` - Validated, safe files only

2. **AWS GuardDuty Malware Protection for S3**
   - Automatic scanning on upload (near real-time)
   - 100GB file size limit (far exceeds 500MB requirement)
   - Predefined tagging: `GuardDutyMalwareScanStatus`

3. **Amazon EventBridge**
   - Capture GuardDuty scan completion events
   - Trigger Lambda for post-scan processing

#### Implementation Pattern

**S3 Quarantine Bucket Policy** (Tag-Based Access Control):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnscannedObjectAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::cmz-knowledge-quarantine/*",
      "Condition": {
        "StringNotEquals": {
          "s3:ExistingObjectTag/GuardDutyMalwareScanStatus": "NO_THREATS_FOUND"
        }
      }
    }
  ]
}
```

**Lambda Handler for Upload Validation** (Python):
```python
import boto3
import mimetypes
from typing import Dict, Tuple

# File type validation
ALLOWED_MIME_TYPES = {
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'text/plain': ['.txt']
}

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB per assistant limit

def validate_upload(event: Dict) -> Tuple[bool, str]:
    """
    Validate uploaded file before processing.
    Integrates with existing CMZ impl/utils/dynamo.py patterns.
    """
    s3_client = boto3.client('s3')

    bucket = event['detail']['bucket']['name']
    key = event['detail']['object']['key']

    # Get object metadata
    response = s3_client.head_object(Bucket=bucket, Key=key)

    # Size validation
    size = response['ContentLength']
    if size > MAX_FILE_SIZE:
        return False, f"File exceeds 500MB limit: {size / 1024 / 1024:.2f}MB"

    # MIME type validation
    content_type = response.get('ContentType', '')
    if content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid file type: {content_type}"

    # GuardDuty scan status check
    tags = s3_client.get_object_tagging(Bucket=bucket, Key=key)
    scan_status = next(
        (tag['Value'] for tag in tags['TagSet']
         if tag['Key'] == 'GuardDutyMalwareScanStatus'),
        None
    )

    if scan_status != 'NO_THREATS_FOUND':
        return False, f"Security scan failed: {scan_status}"

    return True, "Validation passed"
```

**DynamoDB Table Schema for Knowledge Base Metadata**:
```python
# Integrates with existing CMZ DynamoDB patterns (impl/utils/dynamo.py)
KNOWLEDGE_TABLE_SCHEMA = {
    "TableName": "quest-dev-knowledge",
    "KeySchema": [
        {"AttributeName": "animalId", "KeyType": "HASH"},  # Partition key
        {"AttributeName": "documentId", "KeyType": "RANGE"}  # Sort key
    ],
    "AttributeDefinitions": [
        {"AttributeName": "animalId", "AttributeType": "S"},
        {"AttributeName": "documentId", "AttributeType": "S"},
        {"AttributeName": "uploadStatus", "AttributeType": "S"},
        {"AttributeName": "uploadedAt", "AttributeType": "S"}
    ],
    "GlobalSecondaryIndexes": [
        {
            "IndexName": "UploadStatusIndex",
            "KeySchema": [
                {"AttributeName": "animalId", "KeyType": "HASH"},
                {"AttributeName": "uploadStatus", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ],
    "BillingMode": "PAY_PER_REQUEST"  # Aligns with existing CMZ tables
}

# Example document metadata item
DOCUMENT_METADATA_EXAMPLE = {
    "animalId": "animal_001",  # Links to Animals table
    "documentId": "doc_20251023_001",
    "fileName": "red_panda_diet.pdf",
    "fileSize": 2457600,  # bytes
    "mimeType": "application/pdf",
    "s3Bucket": "cmz-knowledge-production",
    "s3Key": "animal_001/doc_20251023_001.pdf",
    "uploadStatus": "validated",  # quarantined, validated, processing, ready, failed
    "scanStatus": "NO_THREATS_FOUND",
    "uploadedBy": "user_zookeeper_001",
    "uploadedAt": "2025-10-23T10:30:00Z",
    "processedAt": None,
    "vectorStoreId": None,  # Bedrock Knowledge Base ID (populated after processing)
    "pageCount": None,
    "wordCount": None,
    "created": {"at": "2025-10-23T10:30:00Z"},
    "modified": {"at": "2025-10-23T10:30:00Z"}
}
```

#### Security Best Practices

1. **Pre-Signed URLs for Upload**: Generate time-limited upload URLs from backend
2. **Server-Side Encryption**: Enable S3 SSE-KMS for all buckets
3. **Lifecycle Policies**: Auto-delete quarantine files after 7 days
4. **Access Logging**: Enable S3 access logs for audit trail
5. **IAM Least Privilege**: Separate roles for upload, scan, and processing

#### Cost Optimization

- **GuardDuty Malware Protection**: Free tier includes 1,000 scans/month + 1GB/month
- **S3 Storage**: Intelligent-Tiering for production bucket (auto-optimization)
- **85% Price Reduction**: Recent GuardDuty improvements (as of 2025)

---

## 2. Document Processing Pipeline

### Architectural Decision: Event-Driven Asynchronous Processing with Lambda + Textract

**Recommended Approach**: Serverless, event-driven pipeline using AWS Step Functions for orchestration.

#### Architecture Components

```
S3 Production Upload → EventBridge → Step Functions State Machine
                                    ↓
                              [Lambda: Start Textract Job]
                                    ↓
                              SNS Topic (Textract Completion)
                                    ↓
                              [Lambda: Process Results]
                                    ↓
                              [Lambda: Generate Embeddings via Bedrock]
                                    ↓
                              OpenSearch Serverless (Vector Storage)
                                    ↓
                              DynamoDB (Update Metadata: status=ready)
```

#### AWS Services

1. **AWS Lambda**
   - **Function 1**: `cmz-kb-start-textract` - Initiate async text extraction
   - **Function 2**: `cmz-kb-process-textract` - Handle extraction results
   - **Function 3**: `cmz-kb-generate-embeddings` - Create vector embeddings
   - **Function 4**: `cmz-kb-update-metadata` - Update DynamoDB

2. **Amazon Textract**
   - Asynchronous operations for documents >10MB
   - Supports up to 500MB PDFs with 3,000 pages
   - Table and structure preservation (Layout feature)

3. **AWS Step Functions**
   - Orchestrate multi-step processing workflow
   - Built-in error handling and retry logic
   - Visual monitoring of processing status

4. **Amazon SNS/SQS**
   - SNS topic for Textract completion notifications
   - SQS queue for reliable message delivery to Lambda

#### Implementation Pattern

**Step Functions State Machine Definition**:
```json
{
  "Comment": "CMZ Knowledge Base Document Processing Pipeline",
  "StartAt": "ValidateDocument",
  "States": {
    "ValidateDocument": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-2:195275676211:function:cmz-kb-validate",
      "Next": "StartTextractJob",
      "Catch": [{
        "ErrorEquals": ["ValidationError"],
        "Next": "MarkFailed"
      }]
    },
    "StartTextractJob": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-2:195275676211:function:cmz-kb-start-textract",
      "Next": "WaitForTextract",
      "ResultPath": "$.textractJobId",
      "Retry": [{
        "ErrorEquals": ["Throttling"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }]
    },
    "WaitForTextract": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish.waitForTaskToken",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-west-2:195275676211:cmz-textract-completion",
        "Message": {
          "JobId.$": "$.textractJobId",
          "TaskToken.$": "$$.Task.Token"
        }
      },
      "Next": "ProcessTextractResults"
    },
    "ProcessTextractResults": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-2:195275676211:function:cmz-kb-process-textract",
      "Next": "GenerateEmbeddings",
      "ResultPath": "$.extractedText"
    },
    "GenerateEmbeddings": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-2:195275676211:function:cmz-kb-generate-embeddings",
      "Next": "UpdateMetadata",
      "ResultPath": "$.vectorStoreId"
    },
    "UpdateMetadata": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-2:195275676211:function:cmz-kb-update-metadata",
      "End": true
    },
    "MarkFailed": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-2:195275676211:function:cmz-kb-mark-failed",
      "End": true
    }
  }
}
```

**Lambda Function: Start Textract Async Job**:
```python
import boto3
from typing import Dict

textract = boto3.client('textract')
sns = boto3.client('sns')

def lambda_handler(event: Dict, context) -> Dict:
    """
    Start asynchronous Textract job for document text extraction.
    Handles large documents (up to 500MB) efficiently.
    """
    document_id = event['documentId']
    animal_id = event['animalId']
    s3_bucket = event['s3Bucket']
    s3_key = event['s3Key']

    # SNS topic for completion notification
    sns_topic_arn = 'arn:aws:sns:us-west-2:195275676211:cmz-textract-completion'

    # Start async text detection (for documents, not forms)
    response = textract.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': s3_bucket,
                'Name': s3_key
            }
        },
        NotificationChannel={
            'SNSTopicArn': sns_topic_arn,
            'RoleArn': 'arn:aws:iam::195275676211:role/TextractServiceRole'
        },
        JobTag=f"{animal_id}:{document_id}"
    )

    job_id = response['JobId']

    # Update DynamoDB metadata with processing status
    from openapi_server.impl.utils.dynamo import table, to_ddb, now_iso

    knowledge_table = table('quest-dev-knowledge')
    knowledge_table.update_item(
        Key=to_ddb({'animalId': animal_id, 'documentId': document_id}),
        UpdateExpression='SET uploadStatus = :status, textractJobId = :jobId, modified.#at = :now',
        ExpressionAttributeNames={'#at': 'at'},
        ExpressionAttributeValues=to_ddb({
            ':status': 'processing',
            ':jobId': job_id,
            ':now': now_iso()
        })
    )

    return {
        'jobId': job_id,
        'status': 'STARTED',
        'documentId': document_id,
        'animalId': animal_id
    }
```

**Lambda Function: Process Textract Results**:
```python
import boto3
from typing import Dict, List

textract = boto3.client('textract')

def lambda_handler(event: Dict, context) -> Dict:
    """
    Retrieve and process Textract job results.
    Extracts text while preserving structure (tables, headings).
    """
    job_id = event['jobId']
    document_id = event['documentId']
    animal_id = event['animalId']

    # Get text detection results
    response = textract.get_document_text_detection(JobId=job_id)

    # Extract blocks while preserving structure
    extracted_text = []
    tables = []
    page_count = 0

    # Process all pages (pagination if needed)
    while True:
        blocks = response.get('Blocks', [])

        for block in blocks:
            if block['BlockType'] == 'PAGE':
                page_count += 1
            elif block['BlockType'] == 'LINE':
                extracted_text.append(block['Text'])
            elif block['BlockType'] == 'TABLE':
                tables.append(extract_table_data(block, blocks))

        # Check for more pages
        next_token = response.get('NextToken')
        if not next_token:
            break
        response = textract.get_document_text_detection(
            JobId=job_id,
            NextToken=next_token
        )

    # Combine text with structure preservation
    full_text = '\n'.join(extracted_text)
    word_count = len(full_text.split())

    # Store extracted text in S3 for further processing
    s3 = boto3.client('s3')
    text_key = f"{animal_id}/{document_id}/extracted_text.txt"
    s3.put_object(
        Bucket='cmz-knowledge-production',
        Key=text_key,
        Body=full_text.encode('utf-8'),
        ContentType='text/plain'
    )

    # Update DynamoDB with extraction results
    from openapi_server.impl.utils.dynamo import table, to_ddb, now_iso

    knowledge_table = table('quest-dev-knowledge')
    knowledge_table.update_item(
        Key=to_ddb({'animalId': animal_id, 'documentId': document_id}),
        UpdateExpression='SET pageCount = :pages, wordCount = :words, '
                        'extractedTextS3Key = :key, modified.#at = :now',
        ExpressionAttributeNames={'#at': 'at'},
        ExpressionAttributeValues=to_ddb({
            ':pages': page_count,
            ':words': word_count,
            ':key': text_key,
            ':now': now_iso()
        })
    )

    return {
        'documentId': document_id,
        'animalId': animal_id,
        'pageCount': page_count,
        'wordCount': word_count,
        'textS3Key': text_key,
        'tableCount': len(tables)
    }

def extract_table_data(table_block: Dict, all_blocks: List[Dict]) -> Dict:
    """Extract structured table data from Textract blocks."""
    # Implementation for table extraction with cell relationships
    # Returns structured table data for potential knowledge base enhancement
    pass
```

#### Performance Optimization

1. **Chunking Strategy**: Break large documents into smaller chunks (1000-2000 words)
2. **Parallel Processing**: Use Lambda concurrency for multiple documents
3. **Caching**: Store extracted text to avoid re-processing
4. **Progress Tracking**: Update DynamoDB at each pipeline stage

#### Meeting 5-Minute Requirement

**Estimated Processing Times**:
- GuardDuty Scan: 30-60 seconds
- Textract Async Job: 1-3 minutes (depends on pages)
- Embedding Generation: 30-90 seconds
- Vector Storage: 10-20 seconds
- **Total**: 2-5 minutes for typical documents (well within requirement)

**Optimization for Large Documents**:
- Use Textract async mode (required for >10MB)
- Parallel chunk processing for embeddings
- Batch vector insertion to OpenSearch

---

## 3. Knowledge Base Storage

### Architectural Decision: Hybrid DynamoDB + S3 + OpenSearch Serverless

**Recommended Approach**: Three-tier storage strategy optimized for different data types.

#### Storage Strategy

| Data Type | Storage Service | Rationale |
|-----------|----------------|-----------|
| Document Files (PDF, DOC, TXT) | Amazon S3 | Cost-effective bulk storage, 99.999999999% durability |
| Metadata & Status | DynamoDB | Fast queries, existing CMZ patterns, pay-per-request |
| Vector Embeddings | OpenSearch Serverless | Semantic search, managed vector engine, auto-scaling |
| Extracted Text Cache | S3 | Avoid re-processing, enable debugging |

#### DynamoDB Table Design (Metadata)

**Table: `quest-dev-knowledge`** (Follows existing CMZ patterns)
```python
# Primary access pattern: Get all documents for an animal
{
    "animalId": "animal_red_panda_001",  # Partition Key
    "documentId": "doc_2025_10_23_001",   # Sort Key

    # File Information
    "fileName": "red_panda_diet_guide.pdf",
    "fileSize": 2457600,
    "mimeType": "application/pdf",

    # S3 References
    "s3Bucket": "cmz-knowledge-production",
    "s3Key": "animal_red_panda_001/doc_2025_10_23_001.pdf",
    "extractedTextS3Key": "animal_red_panda_001/doc_2025_10_23_001/extracted_text.txt",

    # Processing Status
    "uploadStatus": "ready",  # quarantined, validated, processing, ready, failed
    "processingStage": "complete",  # scan, extract, embed, index
    "textractJobId": "abc123...",

    # Content Metadata
    "pageCount": 15,
    "wordCount": 3500,
    "language": "en",
    "contentType": "educational_diet",  # Categorization for content validation

    # Vector Store References
    "vectorStoreId": "bedrock-kb-abc123",
    "embeddingModel": "amazon.titan-embed-text-v2",
    "chunkCount": 12,

    # Version Control
    "version": 1,
    "previousVersion": None,
    "isLatest": True,

    # Audit Fields
    "uploadedBy": "user_zookeeper_001",
    "uploadedAt": "2025-10-23T10:30:00Z",
    "processedAt": "2025-10-23T10:34:30Z",
    "validatedBy": "auto",
    "validationScore": 0.95,

    # CMZ Standard Fields
    "created": {"at": "2025-10-23T10:30:00Z", "by": "user_zookeeper_001"},
    "modified": {"at": "2025-10-23T10:34:30Z", "by": "system"}
}
```

**Global Secondary Index: Storage Quota Tracking**
```python
GSI_NAME = "AnimalStorageIndex"
{
    "IndexName": "AnimalStorageIndex",
    "KeySchema": [
        {"AttributeName": "animalId", "KeyType": "HASH"}
    ],
    "Projection": {
        "ProjectionType": "INCLUDE",
        "NonKeyAttributes": ["fileSize", "uploadStatus", "isLatest"]
    }
}

# Query to check storage quota (500MB per animal)
def check_storage_quota(animal_id: str) -> Dict:
    """
    Verify animal hasn't exceeded 500MB storage limit.
    Only counts 'ready' documents with isLatest=True.
    """
    from openapi_server.impl.utils.dynamo import table, from_ddb

    knowledge_table = table('quest-dev-knowledge')

    response = knowledge_table.query(
        IndexName='AnimalStorageIndex',
        KeyConditionExpression='animalId = :aid',
        FilterExpression='uploadStatus = :status AND isLatest = :latest',
        ExpressionAttributeValues={
            ':aid': {'S': animal_id},
            ':status': {'S': 'ready'},
            ':latest': {'BOOL': True}
        }
    )

    total_bytes = sum(
        int(item.get('fileSize', {}).get('N', 0))
        for item in response['Items']
    )

    total_mb = total_bytes / (1024 * 1024)
    limit_mb = 500

    return {
        'animalId': animal_id,
        'totalMB': round(total_mb, 2),
        'limitMB': limit_mb,
        'percentUsed': round((total_mb / limit_mb) * 100, 1),
        'documentsCount': response['Count'],
        'withinLimit': total_mb < limit_mb
    }
```

#### S3 Bucket Structure

```
cmz-knowledge-production/
├── animal_red_panda_001/
│   ├── doc_2025_10_23_001.pdf           # Original document
│   ├── doc_2025_10_23_001/
│   │   ├── extracted_text.txt            # Textract output
│   │   ├── chunks/                       # Text chunks for embeddings
│   │   │   ├── chunk_001.txt
│   │   │   ├── chunk_002.txt
│   │   │   └── ...
│   │   └── metadata.json                 # Processing metadata
│   └── ...
├── animal_lion_002/
│   └── ...
└── shared/
    └── educational_standards.pdf         # Shared reference materials
```

**S3 Lifecycle Policy** (Cost Optimization):
```json
{
  "Rules": [
    {
      "Id": "TransitionExtractedText",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "INTELLIGENT_TIERING"
        }
      ],
      "Filter": {
        "Prefix": ""
      }
    },
    {
      "Id": "DeleteFailedUploads",
      "Status": "Enabled",
      "Expiration": {
        "Days": 7
      },
      "Filter": {
        "And": {
          "Tags": [
            {
              "Key": "uploadStatus",
              "Value": "failed"
            }
          ]
        }
      }
    }
  ]
}
```

#### Version Control Pattern

**Implementing Document Versioning** (Sort Key Prefix Pattern):
```python
def create_document_version(animal_id: str, document_id: str, version: int) -> str:
    """
    Create versioned sort key for document updates.
    Allows tracking document history without replacing old versions.
    """
    # Sort key format: doc_YYYY_MM_DD_NNN#v{version}
    return f"{document_id}#v{version}"

# Example: Query all versions of a document
def get_document_versions(animal_id: str, document_id: str) -> List[Dict]:
    """Get all versions of a document for version history."""
    from openapi_server.impl.utils.dynamo import table

    knowledge_table = table('quest-dev-knowledge')

    response = knowledge_table.query(
        KeyConditionExpression='animalId = :aid AND begins_with(documentId, :did)',
        ExpressionAttributeValues={
            ':aid': {'S': animal_id},
            ':did': {'S': document_id}
        },
        ScanIndexForward=False  # Most recent first
    )

    return [from_ddb(item) for item in response['Items']]

# Example version metadata
VERSION_EXAMPLE = {
    "animalId": "animal_red_panda_001",
    "documentId": "doc_2025_10_23_001#v2",  # Version 2
    "version": 2,
    "previousVersion": "doc_2025_10_23_001#v1",
    "isLatest": True,
    "versionCreatedAt": "2025-10-24T14:20:00Z",
    "versionCreatedBy": "user_zookeeper_001",
    "versionNotes": "Updated feeding schedule section"
}
```

---

## 4. Text Extraction

### Architectural Decision: AWS Textract with Structure Preservation

**Recommended Approach**: Use Textract's Layout and Table features for educational content structure.

#### Best Practices for Educational Documents

1. **Quality Requirements**
   - Minimum 150 DPI for uploaded documents
   - Validate text is upright (not rotated)
   - Ensure tables have clear visual separation

2. **Structure Preservation**
   - Use `AnalyzeDocument` API with `LAYOUT` feature (added late 2023)
   - Extract headings, subheadings, paragraphs, titles
   - Preserve table structures with cell relationships

3. **Confidence Thresholds**
   - Educational content: 95% confidence minimum
   - Flag low-confidence extractions for manual review

#### Implementation Pattern

**Textract Configuration for Educational Content**:
```python
import boto3
from typing import Dict, List, Optional

textract = boto3.client('textract')

def analyze_educational_document(s3_bucket: str, s3_key: str) -> Dict:
    """
    Extract text from educational documents with structure preservation.
    Optimized for zoo educational materials (guides, fact sheets, curricula).
    """
    response = textract.analyze_document(
        Document={
            'S3Object': {
                'Bucket': s3_bucket,
                'Name': s3_key
            }
        },
        FeatureTypes=['LAYOUT', 'TABLES']  # Enable structure extraction
    )

    # Process blocks with structure awareness
    structured_content = {
        'title': None,
        'sections': [],
        'tables': [],
        'metadata': {
            'total_pages': 0,
            'avg_confidence': 0.0,
            'low_confidence_sections': []
        }
    }

    blocks = response['Blocks']
    current_section = None
    confidences = []

    for block in blocks:
        confidence = block.get('Confidence', 0)
        confidences.append(confidence)

        block_type = block['BlockType']

        if block_type == 'LAYOUT_TITLE':
            # Document title (highest level heading)
            structured_content['title'] = block.get('Text', '')

        elif block_type == 'LAYOUT_SECTION_HEADER':
            # Section heading - start new section
            if current_section:
                structured_content['sections'].append(current_section)
            current_section = {
                'heading': block.get('Text', ''),
                'paragraphs': [],
                'confidence': confidence
            }

        elif block_type == 'LAYOUT_TEXT':
            # Paragraph content
            if current_section:
                current_section['paragraphs'].append({
                    'text': block.get('Text', ''),
                    'confidence': confidence
                })

        elif block_type == 'TABLE':
            # Extract table structure
            table_data = extract_educational_table(block, blocks)
            structured_content['tables'].append(table_data)

    # Add final section
    if current_section:
        structured_content['sections'].append(current_section)

    # Calculate metadata
    structured_content['metadata']['avg_confidence'] = sum(confidences) / len(confidences)
    structured_content['metadata']['total_pages'] = sum(1 for b in blocks if b['BlockType'] == 'PAGE')

    # Flag low-confidence sections (< 95%)
    for section in structured_content['sections']:
        if section['confidence'] < 95:
            structured_content['metadata']['low_confidence_sections'].append({
                'heading': section['heading'],
                'confidence': section['confidence']
            })

    return structured_content

def extract_educational_table(table_block: Dict, all_blocks: List[Dict]) -> Dict:
    """
    Extract table data optimized for educational content.
    Common in zoo materials: feeding schedules, habitat specs, etc.
    """
    table_data = {
        'rows': [],
        'column_count': 0,
        'has_headers': False
    }

    # Build block ID lookup
    block_map = {block['Id']: block for block in all_blocks}

    # Get table cells
    if 'Relationships' in table_block:
        for relationship in table_block['Relationships']:
            if relationship['Type'] == 'CHILD':
                cells = []
                for cell_id in relationship['Ids']:
                    cell_block = block_map.get(cell_id)
                    if cell_block and cell_block['BlockType'] == 'CELL':
                        cells.append(cell_block)

                # Organize cells by row/column
                cells.sort(key=lambda c: (c['RowIndex'], c['ColumnIndex']))

                current_row = []
                current_row_index = 1

                for cell in cells:
                    if cell['RowIndex'] != current_row_index:
                        table_data['rows'].append(current_row)
                        current_row = []
                        current_row_index = cell['RowIndex']

                    # Extract cell text
                    cell_text = ''
                    if 'Relationships' in cell:
                        for rel in cell['Relationships']:
                            if rel['Type'] == 'CHILD':
                                for word_id in rel['Ids']:
                                    word_block = block_map.get(word_id)
                                    if word_block and word_block['BlockType'] == 'WORD':
                                        cell_text += word_block['Text'] + ' '

                    current_row.append(cell_text.strip())

                if current_row:
                    table_data['rows'].append(current_row)

    if table_data['rows']:
        table_data['column_count'] = len(table_data['rows'][0])
        table_data['has_headers'] = True  # Assume first row is headers

    return table_data
```

#### Handling Common Educational Content Patterns

**Chunking Strategy for Embeddings**:
```python
def chunk_educational_content(structured_content: Dict, max_words: int = 1500) -> List[Dict]:
    """
    Split extracted content into chunks optimized for embeddings.
    Preserves section boundaries and context.
    """
    chunks = []

    # Add title as context prefix for all chunks
    title_context = structured_content.get('title', '')

    for section in structured_content['sections']:
        section_heading = section['heading']
        section_text = ' '.join(p['text'] for p in section['paragraphs'])

        # Split long sections while preserving context
        words = section_text.split()

        if len(words) <= max_words:
            # Section fits in one chunk
            chunks.append({
                'title': title_context,
                'section': section_heading,
                'content': section_text,
                'metadata': {
                    'chunk_type': 'full_section',
                    'word_count': len(words),
                    'confidence': section['confidence']
                }
            })
        else:
            # Split into sub-chunks with overlap
            overlap = 100  # Words to overlap for context
            start = 0
            chunk_num = 1

            while start < len(words):
                end = min(start + max_words, len(words))
                chunk_words = words[start:end]

                chunks.append({
                    'title': title_context,
                    'section': f"{section_heading} (Part {chunk_num})",
                    'content': ' '.join(chunk_words),
                    'metadata': {
                        'chunk_type': 'partial_section',
                        'word_count': len(chunk_words),
                        'confidence': section['confidence'],
                        'chunk_index': chunk_num
                    }
                })

                start = end - overlap
                chunk_num += 1

    return chunks
```

---

## 5. Embedding and Search

### Architectural Decision: Amazon Bedrock Knowledge Bases with OpenSearch Serverless

**Recommended Approach**: Fully managed RAG solution using Bedrock Knowledge Bases (vs custom implementation).

#### Why Bedrock Knowledge Bases over Custom RAG

| Aspect | Custom RAG | Bedrock Knowledge Bases |
|--------|-----------|------------------------|
| Setup Time | 2-3 weeks | 1-2 days |
| Embedding Management | Manual | Automatic |
| Vector Store | Self-managed | Managed (OpenSearch) |
| Chunking | Custom code | Built-in + custom options |
| Updates | Manual reindex | Automatic sync |
| Cost (100 docs) | ~$30-50/month | ~$15-25/month |
| Maintenance | High | Low |

#### Architecture Components

```
Document Upload → S3 → Bedrock Knowledge Base (Auto-sync)
                                ↓
                      [Bedrock: Text Chunking]
                                ↓
                      [Bedrock: Generate Embeddings]
                      (Amazon Titan Text Embeddings V2)
                                ↓
                      OpenSearch Serverless (Vector Engine)
                                ↓
                      DynamoDB Metadata (vectorStoreId, chunkCount)

User Query → Bedrock Retrieve API → OpenSearch Semantic Search
                                ↓
                      [Top K Documents Retrieved]
                                ↓
                      Bedrock RetrieveAndGenerate → Claude Response
```

#### Implementation Pattern

**1. Create Bedrock Knowledge Base**:
```python
import boto3
from typing import Dict, List

bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')

def create_knowledge_base_for_animal(animal_id: str, animal_name: str) -> Dict:
    """
    Create dedicated Bedrock Knowledge Base for an animal assistant.
    Each animal gets its own KB to prevent cross-contamination.
    """

    kb_name = f"cmz-kb-{animal_id.replace('_', '-')}"

    # Create OpenSearch Serverless collection first
    opensearch_collection = create_opensearch_collection(kb_name)

    # Create knowledge base
    response = bedrock_agent.create_knowledge_base(
        name=kb_name,
        description=f"Knowledge base for {animal_name} at Cougar Mountain Zoo",
        roleArn='arn:aws:iam::195275676211:role/BedrockKnowledgeBaseRole',
        knowledgeBaseConfiguration={
            'type': 'VECTOR',
            'vectorKnowledgeBaseConfiguration': {
                'embeddingModelArn': 'arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v2:0'
            }
        },
        storageConfiguration={
            'type': 'OPENSEARCH_SERVERLESS',
            'opensearchServerlessConfiguration': {
                'collectionArn': opensearch_collection['arn'],
                'vectorIndexName': f'{kb_name}-index',
                'fieldMapping': {
                    'vectorField': 'embedding',
                    'textField': 'text',
                    'metadataField': 'metadata'
                }
            }
        }
    )

    kb_id = response['knowledgeBase']['knowledgeBaseId']

    # Update animal record with KB reference
    from openapi_server.impl.utils.dynamo import table, to_ddb, now_iso

    animals_table = table('quest-dev-animals')
    animals_table.update_item(
        Key=to_ddb({'animalId': animal_id}),
        UpdateExpression='SET knowledgeBaseId = :kbid, modified.#at = :now',
        ExpressionAttributeNames={'#at': 'at'},
        ExpressionAttributeValues=to_ddb({
            ':kbid': kb_id,
            ':now': now_iso()
        })
    )

    return {
        'knowledgeBaseId': kb_id,
        'knowledgeBaseName': kb_name,
        'status': 'CREATING'
    }

def create_opensearch_collection(collection_name: str) -> Dict:
    """Create OpenSearch Serverless collection for vector storage."""
    opensearch = boto3.client('opensearchserverless', region_name='us-west-2')

    response = opensearch.create_collection(
        name=collection_name,
        type='VECTORSEARCH',
        description=f'Vector storage for {collection_name}'
    )

    return {
        'id': response['createCollectionDetail']['id'],
        'arn': response['createCollectionDetail']['arn'],
        'name': collection_name
    }
```

**2. Create Data Source and Ingest Documents**:
```python
def create_data_source_for_animal(kb_id: str, animal_id: str) -> Dict:
    """
    Create S3 data source for automatic document ingestion.
    Bedrock will auto-sync documents from S3 prefix.
    """
    data_source_name = f"cmz-ds-{animal_id.replace('_', '-')}"
    s3_prefix = f"s3://cmz-knowledge-production/{animal_id}/"

    response = bedrock_agent.create_data_source(
        knowledgeBaseId=kb_id,
        name=data_source_name,
        dataSourceConfiguration={
            'type': 'S3',
            's3Configuration': {
                'bucketArn': 'arn:aws:s3:::cmz-knowledge-production',
                'inclusionPrefixes': [f"{animal_id}/"]
            }
        },
        vectorIngestionConfiguration={
            'chunkingConfiguration': {
                'chunkingStrategy': 'SEMANTIC',  # Intelligent chunking
                'semanticChunkingConfiguration': {
                    'maxTokens': 300,
                    'bufferSize': 1,
                    'breakpointPercentileThreshold': 95
                }
            }
        }
    )

    data_source_id = response['dataSource']['dataSourceId']

    return {
        'dataSourceId': data_source_id,
        'status': 'AVAILABLE'
    }

def ingest_document(kb_id: str, data_source_id: str) -> Dict:
    """
    Trigger ingestion job to process new documents.
    Bedrock handles chunking, embedding, and indexing automatically.
    """
    response = bedrock_agent.start_ingestion_job(
        knowledgeBaseId=kb_id,
        dataSourceId=data_source_id
    )

    return {
        'ingestionJobId': response['ingestionJob']['ingestionJobId'],
        'status': response['ingestionJob']['status']
    }
```

**3. Query Knowledge Base During Conversations**:
```python
def retrieve_relevant_knowledge(
    kb_id: str,
    query: str,
    top_k: int = 5
) -> List[Dict]:
    """
    Retrieve relevant documents for a user query.
    Used during conversation to augment responses with knowledge base.
    """
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={
            'text': query
        },
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': top_k,
                'overrideSearchType': 'SEMANTIC'  # vs HYBRID
            }
        }
    )

    # Extract retrieved chunks with metadata
    retrieved_docs = []
    for result in response['retrievalResults']:
        retrieved_docs.append({
            'content': result['content']['text'],
            'score': result['score'],
            'location': result['location']['s3Location'],
            'metadata': result.get('metadata', {})
        })

    return retrieved_docs

def generate_response_with_rag(
    kb_id: str,
    model_id: str,
    query: str
) -> Dict:
    """
    Generate response using Retrieve-and-Generate (RAG).
    Bedrock automatically retrieves relevant docs and augments prompt.
    """
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

    response = bedrock_agent_runtime.retrieve_and_generate(
        input={
            'text': query
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': f'arn:aws:bedrock:us-west-2::foundation-model/{model_id}',
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5
                    }
                }
            }
        }
    )

    return {
        'response': response['output']['text'],
        'citations': response.get('citations', []),
        'sessionId': response.get('sessionId')
    }
```

#### Binary Embeddings for Cost Optimization

**Enable Binary Embeddings** (30-50% cost reduction):
```python
def create_knowledge_base_with_binary_embeddings(animal_id: str) -> Dict:
    """
    Create KB with binary embeddings for cost optimization.
    Trade-off: ~5% accuracy reduction for significant cost savings.
    """
    response = bedrock_agent.create_knowledge_base(
        name=f"cmz-kb-{animal_id.replace('_', '-')}",
        # ... other config ...
        storageConfiguration={
            'type': 'OPENSEARCH_SERVERLESS',
            'opensearchServerlessConfiguration': {
                # ... collection config ...
                'fieldMapping': {
                    'vectorField': 'embedding',
                    'textField': 'text',
                    'metadataField': 'metadata'
                }
            }
        },
        vectorKnowledgeBaseConfiguration={
            'embeddingModelArn': 'arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v2:0',
            'embeddingModelConfiguration': {
                'embeddingDataType': 'BINARY'  # Enable binary embeddings
            }
        }
    )

    return response
```

**Note**: Binary embeddings require OpenSearch Serverless 2.16+

#### Integration with Conversation System

**Augment Conversation Turns**:
```python
# In impl/conversation.py (existing CMZ conversation handler)

def handle_conversation_turn_with_knowledge(
    animal_id: str,
    user_message: str,
    conversation_history: List[Dict]
) -> Dict:
    """
    Enhanced conversation handler with knowledge base integration.
    Integrates with existing CMZ conversation system.
    """
    from openapi_server.impl.utils.dynamo import table, from_ddb

    # Get animal's knowledge base ID
    animals_table = table('quest-dev-animals')
    animal = from_ddb(animals_table.get_item(
        Key={'animalId': animal_id}
    )['Item'])

    kb_id = animal.get('knowledgeBaseId')

    if kb_id:
        # Retrieve relevant knowledge
        relevant_docs = retrieve_relevant_knowledge(
            kb_id=kb_id,
            query=user_message,
            top_k=3
        )

        # Build augmented prompt with citations
        context = '\n\n'.join([
            f"[Source: {doc['location']['uri']}]\n{doc['content']}"
            for doc in relevant_docs
        ])

        augmented_prompt = f"""You are {animal['name']}, a {animal['species']} at Cougar Mountain Zoo.

Relevant educational information:
{context}

User question: {user_message}

Provide an accurate, engaging response based on the educational materials above. Always cite your sources."""

        # Generate response with Bedrock
        response = generate_response_with_rag(
            kb_id=kb_id,
            model_id='anthropic.claude-3-5-sonnet-20241022-v2:0',
            query=augmented_prompt
        )

        # Log retrieval analytics
        log_knowledge_retrieval(
            animal_id=animal_id,
            query=user_message,
            retrieved_docs=relevant_docs,
            response_text=response['response']
        )

        return {
            'response': response['response'],
            'citations': response['citations'],
            'knowledgeUsed': True
        }
    else:
        # Fall back to standard conversation (no knowledge base)
        return handle_standard_conversation(animal_id, user_message, conversation_history)
```

---

## 6. Content Validation

### Architectural Decision: Multi-Layer Validation with AWS Comprehend

**Recommended Approach**: Automated validation pipeline with manual review triggers.

#### Validation Layers

```
Layer 1: Malware Scan (GuardDuty) → SECURITY
Layer 2: Content Safety (Comprehend Toxicity) → SAFETY
Layer 3: Educational Standards (Custom ML) → QUALITY
Layer 4: Age Appropriateness (Comprehend + Rules) → COMPLIANCE
Layer 5: Manual Review (Triggered by low scores) → OVERSIGHT
```

#### AWS Services

1. **Amazon Comprehend**
   - Toxicity Detection (harmful content)
   - Prompt Safety Classification
   - Language Detection
   - Sentiment Analysis

2. **Custom Validation Rules**
   - Educational content standards
   - Zoo-specific requirements
   - Age-appropriateness scoring

#### Implementation Pattern

**Comprehensive Content Validation**:
```python
import boto3
from typing import Dict, List, Optional

comprehend = boto3.client('comprehend', region_name='us-west-2')

def validate_educational_content(
    document_text: str,
    metadata: Dict
) -> Dict:
    """
    Multi-layer content validation for educational zoo materials.
    Returns validation score and flags for manual review.
    """
    validation_results = {
        'overall_score': 0.0,
        'passed': False,
        'layers': {},
        'flags': [],
        'requires_manual_review': False
    }

    # Layer 2: Toxicity Detection
    toxicity_result = check_toxicity(document_text)
    validation_results['layers']['toxicity'] = toxicity_result

    if toxicity_result['has_toxicity']:
        validation_results['flags'].append({
            'layer': 'toxicity',
            'severity': 'HIGH',
            'message': 'Toxic content detected',
            'details': toxicity_result['toxic_labels']
        })

    # Layer 3: Educational Standards
    educational_result = check_educational_standards(document_text, metadata)
    validation_results['layers']['educational_standards'] = educational_result

    if educational_result['score'] < 0.7:
        validation_results['flags'].append({
            'layer': 'educational_standards',
            'severity': 'MEDIUM',
            'message': 'Does not meet educational standards',
            'details': educational_result['issues']
        })

    # Layer 4: Age Appropriateness
    age_result = check_age_appropriateness(document_text, metadata)
    validation_results['layers']['age_appropriateness'] = age_result

    if not age_result['appropriate']:
        validation_results['flags'].append({
            'layer': 'age_appropriateness',
            'severity': 'HIGH',
            'message': 'Not age-appropriate',
            'details': age_result['concerns']
        })

    # Calculate overall score (weighted average)
    weights = {
        'toxicity': 0.4,
        'educational_standards': 0.3,
        'age_appropriateness': 0.3
    }

    validation_results['overall_score'] = (
        (1.0 - toxicity_result['max_toxicity_score']) * weights['toxicity'] +
        educational_result['score'] * weights['educational_standards'] +
        (1.0 if age_result['appropriate'] else 0.0) * weights['age_appropriateness']
    )

    # Determine if manual review required
    validation_results['requires_manual_review'] = (
        validation_results['overall_score'] < 0.85 or
        len([f for f in validation_results['flags'] if f['severity'] == 'HIGH']) > 0
    )

    # Pass if score >= 0.85 and no high-severity flags
    validation_results['passed'] = (
        validation_results['overall_score'] >= 0.85 and
        not validation_results['requires_manual_review']
    )

    return validation_results

def check_toxicity(text: str) -> Dict:
    """
    Use AWS Comprehend to detect toxic content.
    Important for zoo educational materials (child safety).
    """
    try:
        response = comprehend.detect_toxic_content(
            TextSegments=[
                {'Text': text[i:i+5000]}
                for i in range(0, len(text), 5000)
            ],
            LanguageCode='en'
        )

        toxic_labels = []
        max_score = 0.0

        for segment in response['ResultList']:
            for label in segment['Labels']:
                if label['Score'] > 0.5:  # Threshold for toxicity
                    toxic_labels.append({
                        'name': label['Name'],
                        'score': label['Score']
                    })
                    max_score = max(max_score, label['Score'])

        return {
            'has_toxicity': len(toxic_labels) > 0,
            'toxic_labels': toxic_labels,
            'max_toxicity_score': max_score
        }
    except Exception as e:
        return {
            'has_toxicity': False,
            'toxic_labels': [],
            'max_toxicity_score': 0.0,
            'error': str(e)
        }

def check_educational_standards(text: str, metadata: Dict) -> Dict:
    """
    Validate content meets educational standards.
    Custom rules based on zoo educational requirements.
    """
    score = 1.0
    issues = []

    # Check for educational markers
    educational_markers = [
        'fact', 'habitat', 'diet', 'conservation', 'behavior',
        'adaptation', 'ecosystem', 'species', 'endangered'
    ]

    text_lower = text.lower()
    marker_count = sum(1 for marker in educational_markers if marker in text_lower)

    if marker_count < 3:
        issues.append('Insufficient educational content markers')
        score -= 0.3

    # Check reading level (use Comprehend for complexity)
    word_count = len(text.split())
    avg_word_length = sum(len(word) for word in text.split()) / word_count

    # Target: 5th-8th grade reading level
    if avg_word_length > 7:  # Too complex
        issues.append('Reading level too advanced')
        score -= 0.2
    elif avg_word_length < 4:  # Too simple
        issues.append('Reading level too simple')
        score -= 0.1

    # Check for citations/sources
    if 'source:' not in text_lower and 'reference:' not in text_lower:
        issues.append('Missing source citations')
        score -= 0.2

    return {
        'score': max(0.0, score),
        'issues': issues,
        'educational_markers': marker_count
    }

def check_age_appropriateness(text: str, metadata: Dict) -> Dict:
    """
    Verify content is appropriate for zoo visitor age groups.
    Target: 5-12 years old (primary educational demographic).
    """
    concerns = []
    appropriate = True

    # Check for inappropriate topics
    inappropriate_keywords = [
        'death', 'kill', 'blood', 'violent', 'aggressive attack',
        'predator hunting', 'disease', 'suffering'
    ]

    text_lower = text.lower()
    for keyword in inappropriate_keywords:
        if keyword in text_lower:
            concerns.append(f"Contains potentially distressing topic: {keyword}")
            appropriate = False

    # Check sentiment (educational content should be positive/neutral)
    try:
        sentiment_response = comprehend.detect_sentiment(
            Text=text[:5000],  # Comprehend limit
            LanguageCode='en'
        )

        if sentiment_response['Sentiment'] == 'NEGATIVE':
            if sentiment_response['SentimentScore']['Negative'] > 0.7:
                concerns.append('Overly negative tone for educational content')
                appropriate = False
    except Exception:
        pass

    return {
        'appropriate': appropriate,
        'concerns': concerns,
        'target_age_range': '5-12 years'
    }
```

**Manual Review Queue**:
```python
def queue_for_manual_review(
    document_id: str,
    animal_id: str,
    validation_results: Dict
) -> Dict:
    """
    Add document to manual review queue if validation concerns exist.
    Integrates with existing CMZ admin workflow.
    """
    from openapi_server.impl.utils.dynamo import table, to_ddb, now_iso

    review_table = table('quest-dev-content-review')

    review_item = {
        'reviewId': f"review_{document_id}",
        'documentId': document_id,
        'animalId': animal_id,
        'reviewStatus': 'pending',
        'validationScore': validation_results['overall_score'],
        'flags': validation_results['flags'],
        'priority': 'high' if any(f['severity'] == 'HIGH' for f in validation_results['flags']) else 'normal',
        'assignedTo': None,
        'reviewNotes': None,
        'created': {'at': now_iso()},
        'modified': {'at': now_iso()}
    }

    review_table.put_item(Item=to_ddb(review_item))

    # Send notification to admin dashboard
    send_review_notification(review_item)

    return {
        'reviewId': review_item['reviewId'],
        'status': 'queued'
    }

def send_review_notification(review_item: Dict):
    """Send SNS notification for manual review."""
    sns = boto3.client('sns', region_name='us-west-2')

    sns.publish(
        TopicArn='arn:aws:sns:us-west-2:195275676211:cmz-content-review',
        Subject=f"Content Review Required: {review_item['documentId']}",
        Message=f"""Document requires manual review:

Document ID: {review_item['documentId']}
Animal ID: {review_item['animalId']}
Validation Score: {review_item['validationScore']:.2%}
Priority: {review_item['priority'].upper()}
Flags: {len(review_item['flags'])}

Review in admin dashboard: https://admin.cmzchatbots.org/content-review/{review_item['reviewId']}
"""
    )
```

---

## Recommended AWS Technology Stack

### Core Services (Must Have)

| Service | Purpose | Estimated Cost |
|---------|---------|---------------|
| **Amazon S3** | Document storage (quarantine + production) | ~$2-5/month |
| **AWS Lambda** | Serverless processing functions | ~$1-3/month |
| **Amazon DynamoDB** | Metadata and status tracking | ~$2-4/month |
| **AWS GuardDuty** | Malware scanning (Free Tier: 1000 scans) | $0-10/month |
| **Amazon Textract** | Text extraction (500 pages/month) | ~$2-5/month |
| **Amazon Bedrock** | Knowledge Bases + embeddings + RAG | ~$10-20/month |
| **OpenSearch Serverless** | Vector storage (included in Bedrock KB) | Included |
| **Amazon EventBridge** | Event routing | ~$1/month |
| **AWS Step Functions** | Workflow orchestration | ~$1/month |

**Total Estimated Cost**: $15-30/month for moderate usage

### Optional Services (Nice to Have)

| Service | Purpose | Estimated Cost |
|---------|---------|---------------|
| **Amazon Comprehend** | Content validation (toxicity, sentiment) | ~$5-10/month |
| **AWS CloudWatch** | Monitoring and logging | ~$2-5/month |
| **Amazon SNS** | Notifications (admin alerts) | <$1/month |
| **AWS KMS** | Encryption key management | ~$1/month |

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

1. **S3 Bucket Setup**
   - Create quarantine and production buckets
   - Configure lifecycle policies
   - Enable versioning and encryption

2. **GuardDuty Integration**
   - Enable Malware Protection for S3
   - Configure EventBridge rules
   - Test upload → scan → tag workflow

3. **DynamoDB Tables**
   - Create `quest-dev-knowledge` table
   - Create `quest-dev-content-review` table
   - Add indexes for common queries

4. **OpenAPI Specification**
   - Add `/knowledge/upload` endpoint
   - Add `/knowledge/documents` endpoints (CRUD)
   - Add `/knowledge/validate` endpoint

### Phase 2: Processing Pipeline (Week 3-4)

1. **Lambda Functions**
   - Implement upload validation
   - Implement Textract integration (sync + async)
   - Implement text extraction and structuring

2. **Step Functions**
   - Create processing state machine
   - Add error handling and retries
   - Implement progress tracking

3. **Integration Testing**
   - Test with sample PDFs, DOCs, TXT files
   - Verify 5-minute processing requirement
   - Validate error handling

### Phase 3: Knowledge Base & RAG (Week 5-6)

1. **Bedrock Knowledge Bases**
   - Create KB for each animal assistant
   - Configure OpenSearch Serverless collections
   - Set up S3 data sources

2. **Embedding Pipeline**
   - Implement chunking strategy
   - Configure semantic chunking (Bedrock)
   - Test embedding generation

3. **Conversation Integration**
   - Modify `impl/conversation.py` to use KB
   - Implement retrieve + generate pattern
   - Add citation tracking

### Phase 4: Validation & Quality (Week 7-8)

1. **Content Validation**
   - Integrate Comprehend toxicity detection
   - Implement educational standards rules
   - Add age-appropriateness checks

2. **Manual Review Workflow**
   - Create admin dashboard UI
   - Implement review queue
   - Add approval/rejection workflow

3. **Analytics & Monitoring**
   - CloudWatch dashboards
   - Knowledge base usage metrics
   - Processing time analytics

### Phase 5: Production Readiness (Week 9-10)

1. **Performance Optimization**
   - Enable binary embeddings (cost reduction)
   - Optimize Lambda memory/timeout
   - Add caching for frequently accessed docs

2. **Security Hardening**
   - IAM role least privilege
   - Bucket policies and encryption
   - Audit logging

3. **Documentation & Training**
   - Admin user guide
   - API documentation
   - Troubleshooting runbook

---

## Cost Optimization Strategies

### 1. Binary Embeddings (30-50% Cost Reduction)
- Enable binary embeddings in Bedrock Knowledge Bases
- Trade-off: ~5% accuracy reduction
- Savings: Reduced OpenSearch storage and query costs

### 2. Intelligent S3 Storage Tiering
- Use S3 Intelligent-Tiering for production bucket
- Move extracted text to Glacier after 90 days
- Delete failed uploads after 7 days

### 3. Lambda Optimization
- Right-size memory allocation (256-512MB typical)
- Use Lambda Provisioned Concurrency sparingly
- Batch operations where possible

### 4. DynamoDB Optimization
- Use Pay-Per-Request (existing CMZ pattern)
- Archive old document metadata after 1 year
- Use sparse indexes for optional attributes

### 5. GuardDuty Free Tier
- Leverage 1,000 free scans/month
- Average: 100-200 uploads/month = fully covered

### 6. Textract Optimization
- Only use AnalyzeDocument when structure needed
- Use DetectDocumentText for simple text extraction
- Cache results to avoid re-processing

---

## Security & Compliance

### Data Protection

1. **Encryption at Rest**
   - S3: SSE-KMS (AWS Key Management Service)
   - DynamoDB: Default encryption enabled
   - OpenSearch: Encryption enabled by default

2. **Encryption in Transit**
   - All API calls over HTTPS/TLS 1.2+
   - VPC endpoints for private connectivity (optional)

3. **Access Control**
   - IAM roles with least privilege
   - Bucket policies deny public access
   - Tag-based access control for scanned files

### Audit & Compliance

1. **CloudTrail Logging**
   - All API calls logged
   - 90-day retention minimum
   - Integration with CloudWatch Insights

2. **S3 Access Logging**
   - Log all bucket access
   - Monitor for unauthorized access patterns

3. **Content Audit Trail**
   - Track who uploaded each document
   - Record validation decisions
   - Log manual review actions

### COPPA Compliance (Children's Online Privacy Protection Act)

Educational content for children under 13 requires:
- No collection of personal information without parental consent
- Clear privacy policies
- Content appropriateness validation (implemented)
- Parental notification of practices

**CMZ Implementation**:
- All knowledge base content validated for age-appropriateness
- No user-generated content from children
- Educational focus only (no social features)

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Processing timeout (>5min) | User frustration | Async processing + progress notifications |
| Storage quota exceeded (500MB) | Upload rejection | Pre-upload quota check + warnings |
| Malware detected | Security breach | Two-bucket quarantine + auto-deletion |
| Low extraction confidence | Incorrect content | Manual review queue |
| Vector search low relevance | Poor responses | Relevance feedback + reranking |
| Cost overruns | Budget impact | CloudWatch billing alarms + quotas |

### Operational Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Knowledge base drift | Outdated information | Scheduled content review (quarterly) |
| Manual review backlog | Delayed content | Priority queue + admin notifications |
| Inconsistent quality | Poor user experience | Standardized validation rules |
| Admin training gaps | Misuse of system | Comprehensive documentation + training |

### Mitigation Implementation

**1. Processing Timeout Prevention**:
```python
# Lambda timeout: 15 minutes (max)
# Step Functions timeout: 30 minutes
# User notification: Progress updates every 30 seconds

def start_processing_with_notifications(document_id: str, animal_id: str):
    """Start processing and send progress updates."""
    # Start Step Functions execution
    execution_arn = start_step_functions_execution(...)

    # Send initial notification
    send_progress_update(document_id, status='started', progress=0)

    # Monitor execution and send updates
    # (Implementation in Lambda triggered by Step Functions events)
```

**2. Storage Quota Enforcement**:
```python
# In upload validation Lambda

def validate_storage_quota(animal_id: str, upload_size_mb: float) -> Tuple[bool, str]:
    """Prevent uploads that would exceed 500MB limit."""
    current_usage = check_storage_quota(animal_id)

    if current_usage['totalMB'] + upload_size_mb > 500:
        return False, f"Upload would exceed 500MB limit. Current: {current_usage['totalMB']}MB, Upload: {upload_size_mb}MB"

    if current_usage['percentUsed'] > 90:
        # Send warning notification
        send_quota_warning(animal_id, current_usage)

    return True, "Within quota"
```

---

## Integration with Existing CMZ Patterns

### DynamoDB Integration

All knowledge base operations use existing `impl/utils/dynamo.py`:
```python
from openapi_server.impl.utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)

# Example: Create document metadata
def create_document_metadata(document_data: Dict) -> Tuple[Dict, int]:
    item = model_to_json_keyed_dict(document_data)
    ensure_pk(item, "documentId")

    item.setdefault("created", {"at": now_iso()})
    item["modified"] = {"at": now_iso()}

    try:
        knowledge_table = table('quest-dev-knowledge')
        knowledge_table.put_item(Item=to_ddb(item))
        return from_ddb(item), 201
    except ClientError as e:
        return error_response(e)
```

### OpenAPI Integration

Add knowledge endpoints to `openapi_spec.yaml`:
```yaml
/knowledge/upload:
  post:
    summary: Upload document to animal knowledge base
    operationId: knowledge_upload_post
    tags: [Knowledge]
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            properties:
              animalId:
                type: string
              file:
                type: string
                format: binary
    responses:
      '201':
        description: Upload successful
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DocumentUploadResponse'

/knowledge/{animalId}/documents:
  get:
    summary: List documents for an animal
    operationId: knowledge_documents_get
    tags: [Knowledge]
    parameters:
      - name: animalId
        in: path
        required: true
        schema:
          type: string
    responses:
      '200':
        description: Document list
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/DocumentMetadata'
```

### Controller Implementation

Follow existing CMZ controller → handler pattern:
```python
# In controllers/knowledge_controller.py (generated)
from openapi_server.impl import knowledge

def knowledge_upload_post(body):
    """Upload document to knowledge base."""
    return knowledge.handle_upload(body)

# In impl/knowledge.py (custom implementation)
def handle_upload(body: Dict) -> Tuple[Dict, int]:
    """
    Handle document upload with validation and processing.
    Integrates with existing CMZ patterns.
    """
    from .utils.dynamo import table, to_ddb, now_iso, error_response

    animal_id = body.get('animalId')
    file_data = body.get('file')

    # Validate animal exists
    animals_table = table('quest-dev-animals')
    try:
        animal = animals_table.get_item(Key=to_ddb({'animalId': animal_id}))
        if 'Item' not in animal:
            return not_found(f"Animal {animal_id} not found")
    except ClientError as e:
        return error_response(e)

    # Upload to S3 quarantine bucket
    # Trigger processing pipeline
    # Return upload status

    return {
        'documentId': document_id,
        'status': 'processing',
        'message': 'Document uploaded successfully and queued for processing'
    }, 201
```

---

## Next Steps

### Immediate Actions (This Week)

1. **Review Architecture**: Team review of this document, identify concerns
2. **Cost Approval**: Verify $15-30/month budget allocation
3. **AWS Permissions**: Ensure IAM roles have necessary Bedrock/Textract permissions
4. **Prototype**: Build minimal upload → scan → Textract flow

### Short-Term (Next 2 Weeks)

1. **Phase 1 Implementation**: S3 buckets, GuardDuty, DynamoDB tables
2. **OpenAPI Updates**: Add knowledge base endpoints to spec
3. **Testing Strategy**: Define test documents and success criteria

### Medium-Term (Month 1-2)

1. **Complete Pipeline**: All processing steps functional
2. **Bedrock Integration**: Knowledge Bases configured for 3-5 animals
3. **Admin Dashboard**: Basic UI for document management

### Long-Term (Month 3+)

1. **Production Deployment**: All 24 animal assistants with knowledge bases
2. **Usage Analytics**: Track query patterns, refine chunking
3. **Continuous Improvement**: Quarterly content review, quality optimization

---

## Appendix A: AWS Service Limits

### Relevant Service Limits (us-west-2)

| Service | Limit | CMZ Usage | Notes |
|---------|-------|-----------|-------|
| Lambda Concurrent Executions | 1,000 | <10 | Well within limit |
| Textract Pages/Second | 5 | <1 | Async avoids limit |
| Bedrock Knowledge Bases | 100 | 24 | One per animal |
| OpenSearch Collections | 50 | 24 | One per animal |
| DynamoDB Tables | 2,500 | 12 | 2 new tables |
| S3 Buckets | 1,000 | 2 | Quarantine + production |
| Step Functions Executions | Unlimited | 100-200/month | Pay per execution |

### Request Increases (If Needed)

- Textract async jobs: Default 100 concurrent, increase to 200 if needed
- Bedrock invocations: Default 50,000/min, sufficient for CMZ

---

## Appendix B: Sample Documents for Testing

### Test Document Set

1. **red_panda_diet.pdf** (15 pages, 3,500 words)
   - Tables: 2 (feeding schedule, nutritional requirements)
   - Structure: Title, 5 sections, citations
   - Purpose: Test table extraction, section chunking

2. **lion_conservation.docx** (8 pages, 2,000 words)
   - Complex formatting: Headings, bullet lists, images
   - Purpose: Test DOCX parsing, structure preservation

3. **elephant_behavior.txt** (5 pages, 1,200 words)
   - Plain text with minimal formatting
   - Purpose: Test basic text extraction, fast processing

4. **malicious_test.pdf** (1 page)
   - Contains EICAR test file signature
   - Purpose: Verify GuardDuty malware detection

5. **low_quality_scan.pdf** (10 pages, 50 DPI)
   - Poor quality scanned document
   - Purpose: Test confidence thresholds, manual review trigger

---

## Appendix C: Monitoring & Alerting

### CloudWatch Alarms

```python
# Processing Time Alarm
{
    "AlarmName": "CMZ-KB-Processing-Slow",
    "MetricName": "Duration",
    "Namespace": "AWS/Lambda",
    "Statistic": "Average",
    "Period": 300,
    "EvaluationPeriods": 2,
    "Threshold": 300000,  # 5 minutes in ms
    "ComparisonOperator": "GreaterThanThreshold",
    "Dimensions": [
        {"Name": "FunctionName", "Value": "cmz-kb-process-textract"}
    ]
}

# Storage Quota Alarm
{
    "AlarmName": "CMZ-KB-Storage-80-Percent",
    "MetricName": "BucketSizeBytes",
    "Namespace": "AWS/S3",
    "Statistic": "Average",
    "Period": 86400,  # Daily
    "Threshold": 10737418240,  # 80% of 500MB * 24 animals
    "ComparisonOperator": "GreaterThanThreshold"
}

# Cost Alarm
{
    "AlarmName": "CMZ-KB-Monthly-Cost-High",
    "MetricName": "EstimatedCharges",
    "Namespace": "AWS/Billing",
    "Statistic": "Maximum",
    "Period": 21600,  # 6 hours
    "Threshold": 50,  # $50 (above expected $15-30)
    "ComparisonOperator": "GreaterThanThreshold"
}
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-23 | Claude Code Research | Initial comprehensive research document |

---

**End of Document**
