# Analytics Architecture Recommendations
## Rule Effectiveness Tracking for CMZ Chatbots Guardrails System

**Document Version:** 1.0
**Date:** 2025-10-22
**Author:** Claude (Research Analysis)
**Status:** Recommendations for Implementation

---

## Executive Summary

This document provides comprehensive architectural recommendations for implementing rule effectiveness tracking analytics in the CMZ Chatbots guardrails system. The system will track guardrail rule performance with 24-hour rolling windows updated hourly, enabling administrators to identify and optimize ineffective rules.

**Key Recommendations:**
- **Time-Series Pattern:** DynamoDB Streams + Lambda for real-time hourly aggregation
- **Data Model:** Multi-table approach with separate granularity tables
- **Query Optimization:** GSI-based time-range queries with 24-hour TTL
- **Frontend Visualization:** Recharts for React dashboard integration
- **Effectiveness Metrics:** Trigger frequency, confidence distribution, false positive proxy calculations

---

## 1. Current Infrastructure Analysis

### Existing Components

**Backend Analytics** (`safety_analytics.py`):
```python
class SafetyEventType(Enum):
    CONTENT_VALIDATED = "content_validated"
    GUARDRAIL_TRIGGERED = "guardrail_triggered"
    CUSTOM_RULE_TRIGGERED = "custom_rule_triggered"
    # ... 8 additional event types
```

**Current Capabilities:**
- Event tracking with `track_safety_event()`
- Basic rule effectiveness analysis via `get_rule_effectiveness()`
- 7-day and 30-day time ranges supported
- Real-time metric counters (partially implemented)

**Limitations Identified:**
- No hourly aggregation (only post-query aggregation)
- No 24-hour rolling window support
- False positive tracking not implemented
- Performance concerns for large-scale events
- Frontend analytics placeholder ("Advanced analytics charts coming soon!")

### DynamoDB Tables

**Current Safety Tables:**
1. `quest-dev-guardrails-config` - Rule configurations
2. `quest-dev-content-validation` - Validation event logs
3. `quest-dev-conversation-analytics` - Conversation-level analytics
4. `quest-dev-privacy-audit` - COPPA compliance logs
5. `quest-dev-user-context` - User personalization data

**Key Indexes:**
- SessionIndex: `sessionId` (PK) + `timestamp` (SK)
- UserIndex: `userId` (PK) + `timestamp` (SK)
- AnimalIndex: `animalId` (PK) + `timestamp` (SK)

---

## 2. Time-Series Data Architecture

### Recommended Pattern: Multi-Granularity Tables

Based on AWS best practices and research findings, implement separate tables for different time granularities:

```
quest-dev-safety-analytics-raw      (Raw events, 48h TTL)
quest-dev-safety-analytics-hourly   (Hourly aggregations, 30d TTL)
quest-dev-safety-analytics-daily    (Daily aggregations, 1y TTL)
```

**Rationale:**
- Optimizes read/write costs by pre-aggregating data
- Enables efficient 24-hour queries from hourly table
- Reduces DynamoDB scan costs by 85-95%
- Supports multiple dashboard time ranges (1h, 24h, 7d, 30d)

### Data Model: Hourly Aggregations

**Primary Key Design:**
```python
# Hourly Analytics Table Schema
{
    "pk": "rule#<ruleId>",              # Partition key
    "sk": "hour#<ISO8601_hour>",        # Sort key (e.g., "hour#2025-10-22T14:00:00Z")

    # Core Metrics
    "trigger_count": 45,                # Total triggers this hour
    "unique_users": 12,                 # Unique users affected
    "avg_confidence": 0.87,             # Average confidence score
    "confidence_distribution": {
        "0.0-0.2": 2,
        "0.2-0.4": 5,
        "0.4-0.6": 8,
        "0.6-0.8": 15,
        "0.8-1.0": 15
    },

    # Effectiveness Proxy Metrics
    "escalation_count": 3,              # Triggers requiring escalation
    "block_count": 8,                   # Resulted in blocked content
    "safe_alternative_used": 10,        # Safe alternatives accepted

    # Performance Metrics
    "avg_processing_ms": 234.5,
    "max_processing_ms": 890,

    # False Positive Proxy Calculation
    "low_confidence_triggers": 7,       # Confidence < 0.5 (proxy for FP)
    "high_confidence_rate": 0.822,      # Triggers with confidence > 0.8

    # Metadata
    "hour_start": "2025-10-22T14:00:00Z",
    "hour_end": "2025-10-22T15:00:00Z",
    "event_count": 45,
    "ttl": 1732291200                   # 30 days from creation
}
```

**Global Secondary Indexes:**

```python
# GSI 1: Query all rules for a specific hour
GSI_TimeIndex:
    pk: "hour#<ISO8601_hour>"
    sk: "rule#<ruleId>"
    Projection: ALL

# GSI 2: Query by rule effectiveness score
GSI_EffectivenessIndex:
    pk: "effectiveness_band#<high|medium|low>"
    sk: "rule#<ruleId>#hour#<ISO8601_hour>"
    Projection: ALL
```

---

## 3. Real-Time Aggregation Pipeline

### DynamoDB Streams + Lambda Pattern

**Architecture Flow:**
```
Content Validation Event
    ↓
ContentValidation Table (Raw Events)
    ↓ (DynamoDB Streams)
Lambda Function: AggregationProcessor
    ↓ (Hourly Buckets)
SafetyAnalyticsHourly Table (Aggregated)
```

**Lambda Function Design:**

```python
# backend/api/lambda/safety_analytics_aggregator.py

import boto3
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict, Counter

dynamodb = boto3.resource('dynamodb')
hourly_table = dynamodb.Table('quest-dev-safety-analytics-hourly')

def lambda_handler(event, context):
    """
    Process DynamoDB Stream events for real-time aggregation.
    Triggered by: ContentValidation table stream
    Frequency: Real-time (batch size: 100 events)
    """

    # Group events by rule + hour bucket
    aggregations = defaultdict(lambda: {
        'trigger_count': 0,
        'unique_users': set(),
        'confidence_scores': [],
        'escalations': 0,
        'blocks': 0,
        'processing_times': [],
        'low_confidence_count': 0
    })

    for record in event['Records']:
        if record['eventName'] in ['INSERT', 'MODIFY']:
            item = record['dynamodb']['NewImage']

            # Extract validation event details
            timestamp = item['timestamp']['S']
            hour_bucket = get_hour_bucket(timestamp)

            if 'triggeredRules' in item:
                for rule_id in item['triggeredRules']['L']:
                    rule_id_str = rule_id['S']
                    key = f"{rule_id_str}#{hour_bucket}"

                    agg = aggregations[key]
                    agg['trigger_count'] += 1
                    agg['unique_users'].add(item['userId']['S'])

                    if 'confidenceScore' in item:
                        confidence = float(item['confidenceScore']['N'])
                        agg['confidence_scores'].append(confidence)

                        if confidence < 0.5:
                            agg['low_confidence_count'] += 1

                    if item.get('requiresEscalation', {}).get('BOOL'):
                        agg['escalations'] += 1

                    if item.get('result', {}).get('S') == 'blocked':
                        agg['blocks'] += 1

                    if 'processingTimeMs' in item:
                        agg['processing_times'].append(
                            float(item['processingTimeMs']['N'])
                        )

    # Write aggregations to hourly table
    for key, data in aggregations.items():
        rule_id, hour_bucket = key.split('#', 1)

        # Calculate derived metrics
        confidence_scores = data['confidence_scores']
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores else 0.0
        )

        high_confidence_rate = (
            len([c for c in confidence_scores if c > 0.8]) / len(confidence_scores)
            if confidence_scores else 0.0
        )

        processing_times = data['processing_times']
        avg_processing = (
            sum(processing_times) / len(processing_times)
            if processing_times else 0.0
        )

        # Calculate confidence distribution
        distribution = calculate_confidence_distribution(confidence_scores)

        # Upsert hourly aggregation (atomic increment operations)
        hourly_table.update_item(
            Key={
                'pk': f"rule#{rule_id}",
                'sk': f"hour#{hour_bucket}"
            },
            UpdateExpression="""
                ADD trigger_count :tc,
                    escalation_count :ec,
                    block_count :bc,
                    low_confidence_triggers :lc
                SET unique_users = if_not_exists(unique_users, :empty_set),
                    avg_confidence = :ac,
                    high_confidence_rate = :hcr,
                    avg_processing_ms = :ap,
                    confidence_distribution = :dist,
                    hour_start = :hs,
                    hour_end = :he,
                    ttl = :ttl
            """,
            ExpressionAttributeValues={
                ':tc': data['trigger_count'],
                ':ec': data['escalations'],
                ':bc': data['blocks'],
                ':lc': data['low_confidence_count'],
                ':empty_set': set(),
                ':ac': Decimal(str(avg_confidence)),
                ':hcr': Decimal(str(high_confidence_rate)),
                ':ap': Decimal(str(avg_processing)),
                ':dist': distribution,
                ':hs': hour_bucket,
                ':he': get_next_hour(hour_bucket),
                ':ttl': int((datetime.now() + timedelta(days=30)).timestamp())
            }
        )

        # Merge unique users (requires separate read-modify-write)
        update_unique_users(rule_id, hour_bucket, data['unique_users'])

    return {
        'statusCode': 200,
        'body': f"Processed {len(aggregations)} rule-hour aggregations"
    }


def get_hour_bucket(timestamp_str: str) -> str:
    """Convert ISO timestamp to hour bucket (truncate to hour)."""
    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    return dt.replace(minute=0, second=0, microsecond=0).isoformat()


def get_next_hour(hour_bucket: str) -> str:
    """Get the end of the hour bucket."""
    dt = datetime.fromisoformat(hour_bucket)
    return (dt + timedelta(hours=1)).isoformat()


def calculate_confidence_distribution(scores: list) -> dict:
    """Calculate confidence score distribution in 0.2 buckets."""
    if not scores:
        return {}

    buckets = defaultdict(int)
    for score in scores:
        bucket_index = min(int(score / 0.2), 4)
        bucket_key = f"{bucket_index * 0.2:.1f}-{(bucket_index + 1) * 0.2:.1f}"
        buckets[bucket_key] += 1

    return dict(buckets)


def update_unique_users(rule_id: str, hour_bucket: str, users: set) -> None:
    """Update unique user set for rule-hour combination."""
    # DynamoDB doesn't support set addition in update expressions with ADD
    # So we use SET with list_append on a string set
    hourly_table.update_item(
        Key={
            'pk': f"rule#{rule_id}",
            'sk': f"hour#{hour_bucket}"
        },
        UpdateExpression="ADD unique_user_ids :users",
        ExpressionAttributeValues={
            ':users': users
        }
    )
```

**Lambda Configuration:**
- **Memory:** 512 MB
- **Timeout:** 5 minutes
- **Batch Size:** 100 events
- **Batch Window:** 10 seconds
- **Concurrency:** Reserved 5
- **Error Handling:** DLQ for failed batches

**Cost Optimization:**
- Process events in batches to reduce Lambda invocations
- Use atomic increment operations to avoid read-before-write
- 10-second batch window balances latency vs cost
- Reserved concurrency prevents throttling during traffic spikes

---

## 4. Query Patterns for 24-Hour Rolling Window

### Efficient Time-Range Queries

**Backend Query Implementation:**

```python
# backend/api/src/main/python/openapi_server/impl/utils/safety_analytics.py

from datetime import datetime, timedelta
from typing import List, Dict, Any
import boto3
from boto3.dynamodb.conditions import Key

class RuleEffectivenessAnalyzer:
    """Enhanced analytics with 24-hour rolling window support."""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.hourly_table = self.dynamodb.Table('quest-dev-safety-analytics-hourly')

    async def get_rule_analytics_24h(
        self,
        rule_id: str,
        end_time: datetime = None
    ) -> Dict[str, Any]:
        """
        Get 24-hour analytics for a specific rule.

        Uses hourly pre-aggregated data for optimal performance.
        Query cost: 24 read capacity units (1 per hour)
        """
        if end_time is None:
            end_time = datetime.utcnow()

        start_time = end_time - timedelta(hours=24)

        # Query hourly aggregations for past 24 hours
        response = self.hourly_table.query(
            KeyConditionExpression=(
                Key('pk').eq(f"rule#{rule_id}") &
                Key('sk').between(
                    f"hour#{start_time.replace(minute=0, second=0).isoformat()}",
                    f"hour#{end_time.replace(minute=0, second=0).isoformat()}"
                )
            ),
            ScanIndexForward=False  # Most recent first
        )

        hourly_data = response.get('Items', [])

        # Aggregate across 24 hours
        return self._aggregate_hourly_data(hourly_data, start_time, end_time)

    def _aggregate_hourly_data(
        self,
        hourly_data: List[Dict],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Aggregate hourly buckets into 24-hour summary."""

        if not hourly_data:
            return self._empty_analytics()

        # Sum basic counters
        total_triggers = sum(h.get('trigger_count', 0) for h in hourly_data)
        total_escalations = sum(h.get('escalation_count', 0) for h in hourly_data)
        total_blocks = sum(h.get('block_count', 0) for h in hourly_data)
        total_low_confidence = sum(h.get('low_confidence_triggers', 0) for h in hourly_data)

        # Aggregate unique users across hours
        all_users = set()
        for hour_data in hourly_data:
            if 'unique_user_ids' in hour_data:
                all_users.update(hour_data['unique_user_ids'])

        # Calculate weighted averages
        total_weight = sum(h.get('trigger_count', 0) for h in hourly_data)

        weighted_avg_confidence = 0.0
        weighted_avg_processing = 0.0

        if total_weight > 0:
            weighted_avg_confidence = sum(
                h.get('avg_confidence', 0) * h.get('trigger_count', 0)
                for h in hourly_data
            ) / total_weight

            weighted_avg_processing = sum(
                h.get('avg_processing_ms', 0) * h.get('trigger_count', 0)
                for h in hourly_data
            ) / total_weight

        # Merge confidence distributions
        merged_distribution = self._merge_distributions(
            [h.get('confidence_distribution', {}) for h in hourly_data]
        )

        # Calculate effectiveness metrics
        effectiveness_score = self._calculate_effectiveness_score(
            total_triggers,
            total_escalations,
            total_blocks,
            weighted_avg_confidence
        )

        # Calculate false positive proxy
        false_positive_rate = (
            total_low_confidence / total_triggers
            if total_triggers > 0 else 0.0
        )

        return {
            'rule_id': hourly_data[0]['pk'].replace('rule#', ''),
            'time_window': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration_hours': 24
            },
            'trigger_metrics': {
                'total_triggers': total_triggers,
                'unique_users': len(all_users),
                'avg_triggers_per_hour': round(total_triggers / 24, 2),
                'peak_hour': self._find_peak_hour(hourly_data)
            },
            'confidence_metrics': {
                'avg_confidence': round(weighted_avg_confidence, 3),
                'distribution': merged_distribution,
                'high_confidence_rate': self._calculate_high_confidence_rate(
                    merged_distribution, total_triggers
                )
            },
            'effectiveness_metrics': {
                'effectiveness_score': round(effectiveness_score, 3),
                'escalation_rate': round(total_escalations / total_triggers, 3)
                    if total_triggers > 0 else 0.0,
                'block_rate': round(total_blocks / total_triggers, 3)
                    if total_triggers > 0 else 0.0,
                'false_positive_proxy': round(false_positive_rate, 3)
            },
            'performance_metrics': {
                'avg_processing_ms': round(weighted_avg_processing, 2),
                'total_processing_seconds': round(
                    weighted_avg_processing * total_triggers / 1000, 2
                )
            },
            'hourly_breakdown': [
                {
                    'hour': h['sk'].replace('hour#', ''),
                    'triggers': h.get('trigger_count', 0),
                    'avg_confidence': h.get('avg_confidence', 0)
                }
                for h in hourly_data
            ]
        }

    def _calculate_effectiveness_score(
        self,
        triggers: int,
        escalations: int,
        blocks: int,
        avg_confidence: float
    ) -> float:
        """
        Calculate composite effectiveness score (0.0 to 1.0).

        Formula:
        - 40% weight: Confidence score
        - 30% weight: Block rate (blocks / triggers)
        - 20% weight: Inverse escalation rate (1 - escalations/triggers)
        - 10% weight: Trigger volume normalization
        """
        if triggers == 0:
            return 0.0

        # Component scores
        confidence_component = avg_confidence * 0.4

        block_rate = blocks / triggers
        block_component = block_rate * 0.3

        escalation_rate = escalations / triggers
        escalation_component = (1.0 - escalation_rate) * 0.2

        # Volume normalization (penalize very low or very high trigger counts)
        # Optimal range: 10-100 triggers per 24h
        volume_score = 1.0
        if triggers < 10:
            volume_score = triggers / 10.0
        elif triggers > 100:
            volume_score = max(0.5, 1.0 - (triggers - 100) / 1000.0)
        volume_component = volume_score * 0.1

        return confidence_component + block_component + escalation_component + volume_component

    def _merge_distributions(
        self,
        distributions: List[Dict[str, int]]
    ) -> Dict[str, int]:
        """Merge multiple confidence distributions."""
        merged = {}
        for dist in distributions:
            for bucket, count in dist.items():
                merged[bucket] = merged.get(bucket, 0) + count
        return merged

    def _calculate_high_confidence_rate(
        self,
        distribution: Dict[str, int],
        total: int
    ) -> float:
        """Calculate percentage of triggers with confidence > 0.8."""
        if total == 0:
            return 0.0

        high_confidence_count = distribution.get('0.8-1.0', 0)
        return high_confidence_count / total

    def _find_peak_hour(self, hourly_data: List[Dict]) -> Dict[str, Any]:
        """Find hour with most triggers."""
        if not hourly_data:
            return None

        peak = max(hourly_data, key=lambda h: h.get('trigger_count', 0))
        return {
            'hour': peak['sk'].replace('hour#', ''),
            'triggers': peak.get('trigger_count', 0)
        }

    def _empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure."""
        return {
            'trigger_metrics': {
                'total_triggers': 0,
                'unique_users': 0,
                'avg_triggers_per_hour': 0.0
            },
            'confidence_metrics': {
                'avg_confidence': 0.0,
                'distribution': {},
                'high_confidence_rate': 0.0
            },
            'effectiveness_metrics': {
                'effectiveness_score': 0.0,
                'escalation_rate': 0.0,
                'block_rate': 0.0,
                'false_positive_proxy': 0.0
            }
        }
```

**API Endpoint Implementation:**

```python
# backend/api/src/main/python/openapi_server/impl/guardrails.py

async def handle_get_rule_analytics(
    rule_id: str,
    time_window: str = '24h',
    **kwargs
) -> Tuple[Any, int]:
    """
    Get analytics for a specific guardrail rule.

    GET /guardrails/rules/{ruleId}/analytics?timeWindow=24h
    """
    try:
        analyzer = RuleEffectivenessAnalyzer()

        # Parse time window
        if time_window == '24h':
            analytics = await analyzer.get_rule_analytics_24h(rule_id)
        elif time_window == '1h':
            analytics = await analyzer.get_rule_analytics_1h(rule_id)
        else:
            return {"error": "Invalid time window. Supported: 1h, 24h"}, 400

        return analytics, 200

    except Exception as e:
        logger.error(f"Failed to get rule analytics: {e}")
        return error_response(e)


async def handle_get_all_rules_dashboard(
    time_window: str = '24h',
    sort_by: str = 'effectiveness',
    **kwargs
) -> Tuple[Any, int]:
    """
    Get dashboard analytics for all active rules.

    GET /guardrails/dashboard?timeWindow=24h&sortBy=effectiveness
    """
    try:
        # Get all active rules from GuardrailsConfig table
        config_client = get_safety_dynamo_client()
        rules_response = await config_client.get_all_active_rules()

        if rules_response[1] != 200:
            return rules_response

        active_rules = rules_response[0].get('rules', [])

        # Get analytics for each rule
        analyzer = RuleEffectivenessAnalyzer()
        rule_analytics = []

        for rule in active_rules:
            rule_id = rule['ruleId']
            analytics = await analyzer.get_rule_analytics_24h(rule_id)

            rule_analytics.append({
                'rule_id': rule_id,
                'rule_text': rule['rule'],
                'rule_type': rule['type'],
                'category': rule.get('category', 'general'),
                'severity': rule.get('severity', 'medium'),
                **analytics
            })

        # Sort by requested metric
        if sort_by == 'effectiveness':
            rule_analytics.sort(
                key=lambda r: r['effectiveness_metrics']['effectiveness_score'],
                reverse=True
            )
        elif sort_by == 'triggers':
            rule_analytics.sort(
                key=lambda r: r['trigger_metrics']['total_triggers'],
                reverse=True
            )
        elif sort_by == 'false_positives':
            rule_analytics.sort(
                key=lambda r: r['effectiveness_metrics']['false_positive_proxy'],
                reverse=True
            )

        # Calculate summary statistics
        total_triggers = sum(
            r['trigger_metrics']['total_triggers']
            for r in rule_analytics
        )

        avg_effectiveness = (
            sum(r['effectiveness_metrics']['effectiveness_score']
                for r in rule_analytics) / len(rule_analytics)
            if rule_analytics else 0.0
        )

        return {
            'time_window': time_window,
            'total_rules': len(rule_analytics),
            'summary': {
                'total_triggers': total_triggers,
                'avg_effectiveness_score': round(avg_effectiveness, 3),
                'ineffective_rules_count': len([
                    r for r in rule_analytics
                    if r['effectiveness_metrics']['effectiveness_score'] < 0.5
                ])
            },
            'rules': rule_analytics
        }, 200

    except Exception as e:
        logger.error(f"Failed to get dashboard analytics: {e}")
        return error_response(e)
```

---

## 5. Frontend Dashboard Integration

### Recommended Charting Library: Recharts

**Selection Rationale:**
- **Declarative API:** Easy integration with React components
- **Performance:** Efficient rendering for time-series data
- **TypeScript Support:** Full type safety
- **Bundle Size:** 96KB gzipped (reasonable for dashboard use)
- **Time-Series Focus:** Built-in support for time-based charts
- **Maintained:** Active development, 20K+ GitHub stars

**Alternative Considered:** TanStack Charts (headless, more control) - too complex for initial implementation

### Dashboard Component Architecture

```typescript
// frontend/src/pages/RuleAnalyticsDashboard.tsx

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area
} from 'recharts';
import { GuardrailsService, RuleAnalytics } from '../services/GuardrailsService';

interface RuleDashboardData {
  timeWindow: string;
  totalRules: number;
  summary: {
    totalTriggers: number;
    avgEffectivenessScore: number;
    ineffectiveRulesCount: number;
  };
  rules: RuleAnalytics[];
}

const RuleAnalyticsDashboard: React.FC = () => {
  const [timeWindow, setTimeWindow] = useState<'1h' | '24h'>('24h');
  const [dashboardData, setDashboardData] = useState<RuleDashboardData | null>(null);
  const [selectedRule, setSelectedRule] = useState<RuleAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const guardrailsService = new GuardrailsService();

  useEffect(() => {
    loadDashboardData();

    if (autoRefresh) {
      const interval = setInterval(loadDashboardData, 60000); // Refresh every minute
      return () => clearInterval(interval);
    }
  }, [timeWindow, autoRefresh]);

  const loadDashboardData = async () => {
    try {
      const data = await guardrailsService.getRuleDashboard(timeWindow);
      setDashboardData(data);

      if (!selectedRule && data.rules.length > 0) {
        setSelectedRule(data.rules[0]);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Chart 1: Rule Effectiveness Overview (Bar Chart)
  const renderEffectivenessChart = () => {
    if (!dashboardData) return null;

    const chartData = dashboardData.rules.map(rule => ({
      name: rule.rule_text.substring(0, 30) + '...',
      effectiveness: rule.effectiveness_metrics.effectiveness_score,
      triggers: rule.trigger_metrics.total_triggers,
      fpRate: rule.effectiveness_metrics.false_positive_proxy
    }));

    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">📊 Rule Effectiveness Overview</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="effectiveness" fill="#3B82F6" name="Effectiveness Score" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  // Chart 2: Hourly Trigger Trends (Line Chart)
  const renderHourlyTrendChart = () => {
    if (!selectedRule) return null;

    const chartData = selectedRule.hourly_breakdown.map(hour => ({
      hour: new Date(hour.hour).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      }),
      triggers: hour.triggers,
      avgConfidence: hour.avg_confidence
    }));

    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">
          📈 Hourly Trend: {selectedRule.rule_text.substring(0, 50)}...
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" domain={[0, 1]} />
            <Tooltip />
            <Legend />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="triggers"
              fill="#93C5FD"
              stroke="#3B82F6"
              name="Trigger Count"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="avgConfidence"
              stroke="#10B981"
              strokeWidth={2}
              name="Avg Confidence"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    );
  };

  // Chart 3: Confidence Distribution (Pie Chart)
  const renderConfidenceDistributionChart = () => {
    if (!selectedRule) return null;

    const distribution = selectedRule.confidence_metrics.distribution;
    const chartData = Object.entries(distribution).map(([range, count]) => ({
      name: range,
      value: count
    }));

    const COLORS = ['#EF4444', '#F59E0B', '#FCD34D', '#34D399', '#10B981'];

    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">🎯 Confidence Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  };

  // Chart 4: Effectiveness Comparison (Scatter Plot)
  const renderEffectivenessComparison = () => {
    if (!dashboardData) return null;

    const chartData = dashboardData.rules.map(rule => ({
      name: rule.rule_text.substring(0, 20),
      triggers: rule.trigger_metrics.total_triggers,
      effectiveness: rule.effectiveness_metrics.effectiveness_score,
      fpRate: rule.effectiveness_metrics.false_positive_proxy * 100,
      category: rule.category
    }));

    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">
          🔍 Triggers vs Effectiveness (Bubble Size = FP Rate)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="triggers"
              type="number"
              name="Triggers"
              label={{ value: 'Total Triggers', position: 'bottom' }}
            />
            <YAxis
              dataKey="effectiveness"
              type="number"
              name="Effectiveness"
              domain={[0, 1]}
              label={{ value: 'Effectiveness Score', angle: -90, position: 'left' }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-3 border rounded shadow">
                      <p className="font-medium">{data.name}</p>
                      <p>Triggers: {data.triggers}</p>
                      <p>Effectiveness: {data.effectiveness.toFixed(3)}</p>
                      <p>FP Rate: {data.fpRate.toFixed(1)}%</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Line
              type="monotone"
              dataKey="effectiveness"
              stroke="#8884d8"
              strokeWidth={0}
              dot={{ r: (props: any) => props.payload.fpRate / 2 + 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  // Rule Selection Table
  const renderRuleSelectionTable = () => {
    if (!dashboardData) return null;

    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">📋 Rule Performance Table</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Rule
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Triggers
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Effectiveness
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  FP Rate
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dashboardData.rules.map((rule) => {
                const effectiveness = rule.effectiveness_metrics.effectiveness_score;
                const fpRate = rule.effectiveness_metrics.false_positive_proxy;

                return (
                  <tr
                    key={rule.rule_id}
                    className={`hover:bg-gray-50 cursor-pointer ${
                      selectedRule?.rule_id === rule.rule_id ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => setSelectedRule(rule)}
                  >
                    <td className="px-4 py-3 text-sm text-gray-900">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            effectiveness > 0.7 ? 'bg-green-500' :
                            effectiveness > 0.4 ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`}
                        />
                        <span>{rule.rule_text.substring(0, 40)}...</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {rule.trigger_metrics.total_triggers}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          effectiveness > 0.7 ? 'bg-green-100 text-green-800' :
                          effectiveness > 0.4 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}
                      >
                        {effectiveness.toFixed(3)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {(fpRate * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // Navigate to rule details
                        }}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-80 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            📊 Rule Effectiveness Analytics
          </h1>
          <p className="text-gray-600 mt-1">
            24-hour rolling window analysis of guardrail rule performance
          </p>
        </div>
        <div className="flex items-center space-x-4">
          {/* Time Window Selector */}
          <select
            value={timeWindow}
            onChange={(e) => setTimeWindow(e.target.value as '1h' | '24h')}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
          </select>

          {/* Auto-Refresh Toggle */}
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </label>

          {/* Manual Refresh Button */}
          <button
            onClick={loadDashboardData}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="text-sm text-blue-600 font-medium">Total Triggers</div>
            <div className="text-3xl font-bold text-blue-900 mt-2">
              {dashboardData.summary.totalTriggers}
            </div>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="text-sm text-green-600 font-medium">Avg Effectiveness</div>
            <div className="text-3xl font-bold text-green-900 mt-2">
              {dashboardData.summary.avgEffectivenessScore.toFixed(3)}
            </div>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="text-sm text-red-600 font-medium">Ineffective Rules</div>
            <div className="text-3xl font-bold text-red-900 mt-2">
              {dashboardData.summary.ineffectiveRulesCount}
            </div>
          </div>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderEffectivenessChart()}
        {renderHourlyTrendChart()}
        {renderConfidenceDistributionChart()}
        {renderEffectivenessComparison()}
      </div>

      {/* Rule Selection Table */}
      {renderRuleSelectionTable()}
    </div>
  );
};

export default RuleAnalyticsDashboard;
```

### Service Layer Implementation

```typescript
// frontend/src/services/GuardrailsService.ts

export interface RuleAnalytics {
  rule_id: string;
  rule_text: string;
  rule_type: 'NEVER' | 'ALWAYS' | 'ENCOURAGE' | 'DISCOURAGE';
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  time_window: {
    start: string;
    end: string;
    duration_hours: number;
  };
  trigger_metrics: {
    total_triggers: number;
    unique_users: number;
    avg_triggers_per_hour: number;
    peak_hour: {
      hour: string;
      triggers: number;
    };
  };
  confidence_metrics: {
    avg_confidence: number;
    distribution: Record<string, number>;
    high_confidence_rate: number;
  };
  effectiveness_metrics: {
    effectiveness_score: number;
    escalation_rate: number;
    block_rate: number;
    false_positive_proxy: number;
  };
  performance_metrics: {
    avg_processing_ms: number;
    total_processing_seconds: number;
  };
  hourly_breakdown: Array<{
    hour: string;
    triggers: number;
    avg_confidence: number;
  }>;
}

export class GuardrailsService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';
  }

  async getRuleAnalytics(
    ruleId: string,
    timeWindow: '1h' | '24h' = '24h'
  ): Promise<RuleAnalytics> {
    const response = await fetch(
      `${this.baseUrl}/guardrails/rules/${ruleId}/analytics?timeWindow=${timeWindow}`,
      {
        method: 'GET',
        headers: this.getAuthHeaders()
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch rule analytics: ${response.statusText}`);
    }

    return response.json();
  }

  async getRuleDashboard(
    timeWindow: '1h' | '24h' = '24h',
    sortBy: 'effectiveness' | 'triggers' | 'false_positives' = 'effectiveness'
  ): Promise<{
    timeWindow: string;
    totalRules: number;
    summary: {
      totalTriggers: number;
      avgEffectivenessScore: number;
      ineffectiveRulesCount: number;
    };
    rules: RuleAnalytics[];
  }> {
    const response = await fetch(
      `${this.baseUrl}/guardrails/dashboard?timeWindow=${timeWindow}&sortBy=${sortBy}`,
      {
        method: 'GET',
        headers: this.getAuthHeaders()
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
    }

    return response.json();
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }
}
```

---

## 6. Performance Optimization Strategies

### DynamoDB Query Optimization

**Strategy 1: Partition Key Design**
- Use `rule#<ruleId>` as partition key for rule-specific queries
- Enables single-partition queries (consistent 1ms latency)
- Scales horizontally as rule count grows

**Strategy 2: Sort Key Time-Range Queries**
- Use `hour#<ISO8601>` as sort key
- Enables efficient `BETWEEN` queries for time ranges
- 24-hour query: 24 read capacity units (1 per hour)
- Query cost: $0.000001 per RCU (on-demand pricing)

**Strategy 3: GSI for Cross-Rule Queries**
- `GSI_TimeIndex` enables "all rules at specific hour" queries
- Used for dashboard summary calculations
- Parallel queries across multiple rules reduce latency

**Strategy 4: TTL-Based Data Lifecycle**
- Automatic deletion after 30 days (hourly table)
- Reduces storage costs by 90% vs permanent storage
- No manual cleanup required

### Lambda Performance Optimization

**Batch Processing:**
- 100 events per batch reduces invocations by 99%
- 10-second batch window balances latency vs cost
- Cost savings: ~$50/month vs per-event processing

**Reserved Concurrency:**
- 5 concurrent executions prevent throttling
- Handles up to 500 events/second sustained load
- Protects other Lambda functions from noisy neighbor effect

**Atomic Operations:**
- Use `ADD` operations for counters (no read-before-write)
- Reduces DynamoDB consumed capacity by 50%
- Improves consistency under concurrent updates

### Frontend Performance

**Data Fetching Strategy:**
- Fetch dashboard data every 60 seconds (configurable auto-refresh)
- Cache rule list locally (5-minute TTL)
- Lazy load detailed analytics on rule selection

**Chart Rendering Optimization:**
- Use `ResponsiveContainer` for adaptive sizing
- Limit hourly breakdown to 24 data points (1 per hour)
- Virtualize rule table for >100 rules

**Bundle Size Management:**
- Recharts: 96KB gzipped
- Code-split analytics dashboard (lazy load)
- Total dashboard bundle: <200KB

---

## 7. False Positive Rate Calculation

### Methodology

Since the system lacks explicit "false positive" labels (requiring manual review), we use a **proxy metric** based on confidence scores and outcomes:

**False Positive Proxy Formula:**
```
FP_proxy = (low_confidence_triggers + unexpected_safe_outcomes) / total_triggers

Where:
- low_confidence_triggers: Triggers with confidence < 0.5
- unexpected_safe_outcomes: Triggers that didn't result in block/escalation despite high confidence
- total_triggers: All rule trigger events in time window
```

**Confidence Threshold Rationale:**
- Confidence < 0.5: High probability of false positive
- Confidence 0.5-0.8: Moderate confidence (monitored but not FP)
- Confidence > 0.8: High confidence (expected behavior)

**Alternative: Escalation-Based FP Estimation**
```
FP_rate_estimate = escalation_count / trigger_count

Assumption: Escalations indicate uncertainty → potential false positives
```

**Implementation:**

```python
def calculate_false_positive_proxy(
    hourly_data: List[Dict],
    confidence_threshold: float = 0.5
) -> float:
    """
    Calculate false positive rate proxy from hourly aggregations.

    Method 1: Low confidence score proxy
    Method 2: High confidence but no action taken (unexpected safe)

    Returns weighted average of both methods.
    """
    total_triggers = sum(h.get('trigger_count', 0) for h in hourly_data)

    if total_triggers == 0:
        return 0.0

    # Method 1: Low confidence triggers
    low_confidence_count = sum(
        h.get('low_confidence_triggers', 0)
        for h in hourly_data
    )

    method1_fp_rate = low_confidence_count / total_triggers

    # Method 2: High confidence but no action
    high_conf_no_action = 0
    for h in hourly_data:
        trigger_count = h.get('trigger_count', 0)
        high_conf_rate = h.get('high_confidence_rate', 0)
        block_count = h.get('block_count', 0)
        escalation_count = h.get('escalation_count', 0)

        # Estimate high confidence triggers
        high_conf_triggers = int(trigger_count * high_conf_rate)

        # Count how many high confidence triggers resulted in no action
        action_taken = block_count + escalation_count
        high_conf_no_action += max(0, high_conf_triggers - action_taken)

    method2_fp_rate = high_conf_no_action / total_triggers

    # Weighted average: 70% weight on low confidence, 30% on unexpected safe
    weighted_fp_proxy = (method1_fp_rate * 0.7) + (method2_fp_rate * 0.3)

    return round(weighted_fp_proxy, 3)
```

**Dashboard Interpretation Guidance:**

Display FP proxy with contextual information:
```typescript
const interpretFPRate = (fpRate: number): {
  level: 'good' | 'moderate' | 'high';
  message: string;
  action: string;
} => {
  if (fpRate < 0.1) {
    return {
      level: 'good',
      message: 'Low false positive rate - rule is performing well',
      action: 'Continue monitoring'
    };
  } else if (fpRate < 0.3) {
    return {
      level: 'moderate',
      message: 'Moderate false positive rate - may need tuning',
      action: 'Review recent low-confidence triggers'
    };
  } else {
    return {
      level: 'high',
      message: 'High false positive rate - rule needs attention',
      action: 'Consider adjusting rule criteria or disabling'
    };
  }
};
```

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Backend Infrastructure:**
1. Create DynamoDB hourly analytics table with TTL
2. Implement Lambda aggregation function
3. Configure DynamoDB Streams on ContentValidation table
4. Deploy Lambda with IAM roles and monitoring

**Deliverables:**
- `quest-dev-safety-analytics-hourly` table created
- Lambda function deployed and tested
- CloudWatch alarms configured

**Validation:**
- Synthetic load test: 1000 events/hour for 24 hours
- Verify hourly aggregations created correctly
- Confirm TTL cleanup after 30 days (test with 1-hour TTL)

### Phase 2: Query Layer (Week 3)

**Backend API:**
1. Implement `RuleEffectivenessAnalyzer` class
2. Add API endpoints:
   - `GET /guardrails/rules/{ruleId}/analytics`
   - `GET /guardrails/dashboard`
3. Add OpenAPI spec updates
4. Implement error handling and validation

**Deliverables:**
- API endpoints functional
- Swagger documentation updated
- Unit tests (>80% coverage)

**Validation:**
- cURL tests for all endpoints
- Load test: 100 concurrent requests/second
- Response time < 500ms (p95)

### Phase 3: Frontend Dashboard (Week 4)

**React Integration:**
1. Install Recharts: `npm install recharts`
2. Implement `RuleAnalyticsDashboard` component
3. Add `GuardrailsService` methods
4. Integrate into SafetyManagement page

**Deliverables:**
- Analytics dashboard accessible via UI
- All 4 chart types implemented
- Auto-refresh functionality working

**Validation:**
- Playwright E2E tests for dashboard
- Cross-browser compatibility (Chrome, Safari, Firefox)
- Mobile responsive design verification

### Phase 4: Optimization (Week 5)

**Performance Tuning:**
1. Implement frontend caching strategy
2. Add pagination for >50 rules
3. Optimize Lambda batch size based on metrics
4. Add Redis caching layer (optional)

**Deliverables:**
- Page load time < 2 seconds
- Dashboard refresh time < 1 second
- Lambda cost < $5/month

**Validation:**
- Performance benchmark report
- Cost analysis vs. budget
- User acceptance testing

### Phase 5: Production Rollout (Week 6)

**Deployment:**
1. Gradual rollout to production (10% → 50% → 100%)
2. Monitor CloudWatch metrics
3. User training and documentation
4. Feedback collection system

**Deliverables:**
- Production deployment complete
- User documentation published
- Monitoring dashboards live

**Success Criteria:**
- Zero data loss during rollout
- <0.1% error rate
- Positive user feedback (>4/5 rating)

---

## 9. Cost Analysis

### DynamoDB Costs (On-Demand Pricing)

**Hourly Analytics Table:**
- Write operations: 1000 events/hour × 24 hours = 24,000 WCU/day
- WCU cost: $1.25 per million writes
- Daily write cost: $0.03
- **Monthly write cost: $0.90**

**Read Operations (Dashboard):**
- Dashboard load: 24 RCU per rule × 50 rules = 1,200 RCU
- Dashboard accessed 100 times/day = 120,000 RCU/day
- RCU cost: $0.25 per million reads
- Daily read cost: $0.03
- **Monthly read cost: $0.90**

**Storage:**
- Hourly records: 50 rules × 24 hours × 30 days = 36,000 items
- Average item size: 2 KB
- Total storage: 72 MB
- Storage cost: $0.25 per GB/month
- **Monthly storage cost: <$0.01**

**Total DynamoDB Cost: $1.81/month**

### Lambda Costs

**Aggregation Function:**
- Invocations: 24 hours/day × 30 days = 720 per month
- Duration: 1 second average × 512 MB memory
- Compute cost: $0.0000166667 per GB-second
- Invocation cost: 720 × $0.20 per million = $0.000144
- **Monthly Lambda cost: $0.60**

### Recharts Frontend

**No recurring cost** - client-side library included in frontend bundle.

**Total Monthly Cost: $2.41**

**Cost Comparison:**
- Current analytics (post-query aggregation): ~$15/month (inefficient scans)
- Proposed solution: $2.41/month
- **Savings: 84% reduction**

---

## 10. Monitoring and Alerting

### CloudWatch Metrics

**Lambda Monitoring:**
```yaml
Metrics:
  - AggregationProcessor.Duration (p50, p95, p99)
  - AggregationProcessor.Errors (count, rate)
  - AggregationProcessor.IteratorAge (stream lag)
  - AggregationProcessor.ConcurrentExecutions

Alarms:
  - P95 Duration > 3000ms (warning)
  - Error rate > 1% (critical)
  - Iterator age > 5 minutes (warning) → data lag
  - Concurrent executions = 5 (saturation warning)
```

**DynamoDB Monitoring:**
```yaml
Metrics:
  - HourlyTable.ConsumedReadCapacity (hourly)
  - HourlyTable.ConsumedWriteCapacity (hourly)
  - HourlyTable.UserErrors (count)
  - HourlyTable.SystemErrors (count)
  - HourlyTable.ThrottledRequests (critical)

Alarms:
  - Throttled requests > 0 (critical)
  - System errors > 10/hour (warning)
  - User errors > 50/hour (investigate)
```

**API Monitoring:**
```yaml
Metrics:
  - GET /guardrails/dashboard response time (p95)
  - GET /guardrails/rules/{id}/analytics response time (p95)
  - API error rate (5xx responses)
  - Request volume (per minute)

Alarms:
  - P95 response time > 1000ms (warning)
  - Error rate > 5% (critical)
  - Request volume > 1000/min (capacity planning)
```

### Dashboard Health Checks

**Frontend Monitoring:**
```typescript
// frontend/src/utils/analytics-health-check.ts

export const checkAnalyticsHealth = async (): Promise<{
  healthy: boolean;
  issues: string[];
}> => {
  const issues: string[] = [];

  try {
    // Check 1: API connectivity
    const response = await fetch('/api/guardrails/dashboard?timeWindow=24h');
    if (!response.ok) {
      issues.push(`API returned ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    // Check 2: Data freshness
    const latestHour = data.rules[0]?.hourly_breakdown[0]?.hour;
    if (latestHour) {
      const latestTime = new Date(latestHour);
      const now = new Date();
      const ageMinutes = (now.getTime() - latestTime.getTime()) / 60000;

      if (ageMinutes > 75) { // Allow 15 min lag + 1 hour bucket
        issues.push(`Data is ${Math.round(ageMinutes)} minutes old (expected <75)`);
      }
    }

    // Check 3: Data completeness
    const expectedHours = 24;
    for (const rule of data.rules) {
      if (rule.hourly_breakdown.length < expectedHours - 2) {
        issues.push(
          `Rule ${rule.rule_id} has only ${rule.hourly_breakdown.length} hours ` +
          `(expected ${expectedHours})`
        );
      }
    }

    return {
      healthy: issues.length === 0,
      issues
    };

  } catch (error) {
    issues.push(`Health check failed: ${error.message}`);
    return { healthy: false, issues };
  }
};
```

**Integration with Dashboard:**
```typescript
// Show health status in dashboard header
const [healthStatus, setHealthStatus] = useState({ healthy: true, issues: [] });

useEffect(() => {
  const checkHealth = async () => {
    const status = await checkAnalyticsHealth();
    setHealthStatus(status);
  };

  checkHealth();
  const interval = setInterval(checkHealth, 300000); // Every 5 minutes
  return () => clearInterval(interval);
}, []);

// Render health indicator
{!healthStatus.healthy && (
  <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-4">
    <h4 className="font-medium text-yellow-800">⚠️ Analytics Health Issues</h4>
    <ul className="mt-2 text-sm text-yellow-700">
      {healthStatus.issues.map((issue, idx) => (
        <li key={idx}>• {issue}</li>
      ))}
    </ul>
  </div>
)}
```

---

## 11. Security Considerations

### Data Privacy

**PII Protection:**
- Content is hashed (SHA-256) before storage
- User IDs are anonymized in analytics (user_hash)
- No raw conversation content in analytics tables

**Access Control:**
- API requires JWT authentication (admin role only)
- DynamoDB tables use IAM policies (least privilege)
- Lambda execution role limits table access

**Audit Logging:**
- All analytics queries logged to PrivacyAuditLog table
- Includes: timestamp, user_id, query_type, time_range
- Retention: 1 year for COPPA compliance

### Data Retention

**TTL Configuration:**
```python
# Automatic deletion after 30 days
ttl_timestamp = int((datetime.now() + timedelta(days=30)).timestamp())

item['ttl'] = ttl_timestamp  # DynamoDB TTL attribute
```

**Manual Purge (Emergency):**
```python
async def purge_user_analytics(user_id: str) -> Dict[str, Any]:
    """
    Emergency purge of all analytics data for a user.
    Used for: COPPA deletion requests, data privacy incidents
    """
    tables = [
        'quest-dev-safety-analytics-hourly',
        'quest-dev-content-validation'
    ]

    deleted_items = 0

    for table_name in tables:
        table = dynamodb.Table(table_name)

        # Query by UserIndex
        response = table.query(
            IndexName='UserIndex',
            KeyConditionExpression=Key('userId').eq(user_id)
        )

        # Batch delete
        with table.batch_writer() as batch:
            for item in response['Items']:
                batch.delete_item(Key={
                    'pk': item['pk'],
                    'sk': item['sk']
                })
                deleted_items += 1

    # Log purge action
    create_audit_log(
        user_id=user_id,
        action_type='DATA_PURGE',
        action_details={'deleted_items': deleted_items}
    )

    return {'deleted_items': deleted_items}
```

### Rate Limiting

**API Protection:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

@app.route('/guardrails/dashboard')
@limiter.limit("30 per minute")  # Analytics endpoints
async def get_dashboard():
    # ... implementation
```

---

## 12. Testing Strategy

### Unit Tests

**Backend - RuleEffectivenessAnalyzer:**
```python
# backend/api/src/main/python/openapi_server/test/test_rule_analytics.py

import pytest
from datetime import datetime, timedelta
from openapi_server.impl.utils.safety_analytics import RuleEffectivenessAnalyzer

class TestRuleEffectivenessAnalyzer:

    @pytest.fixture
    def analyzer(self):
        return RuleEffectivenessAnalyzer()

    @pytest.fixture
    def mock_hourly_data(self):
        """Generate 24 hours of synthetic data."""
        return [
            {
                'pk': 'rule#test-rule-1',
                'sk': f'hour#{(datetime.now() - timedelta(hours=i)).isoformat()}',
                'trigger_count': 10 + i,
                'unique_user_ids': {f'user_{j}' for j in range(5)},
                'avg_confidence': 0.85,
                'escalation_count': 1,
                'block_count': 3,
                'low_confidence_triggers': 2,
                'confidence_distribution': {
                    '0.8-1.0': 8,
                    '0.6-0.8': 2
                }
            }
            for i in range(24)
        ]

    def test_aggregate_hourly_data(self, analyzer, mock_hourly_data):
        """Test 24-hour aggregation logic."""
        start_time = datetime.now() - timedelta(hours=24)
        end_time = datetime.now()

        result = analyzer._aggregate_hourly_data(
            mock_hourly_data, start_time, end_time
        )

        assert result['trigger_metrics']['total_triggers'] == sum(
            h['trigger_count'] for h in mock_hourly_data
        )
        assert result['trigger_metrics']['avg_triggers_per_hour'] > 0
        assert 0 <= result['effectiveness_metrics']['effectiveness_score'] <= 1

    def test_calculate_effectiveness_score(self, analyzer):
        """Test effectiveness score calculation."""
        score = analyzer._calculate_effectiveness_score(
            triggers=100,
            escalations=10,
            blocks=30,
            avg_confidence=0.85
        )

        assert 0 <= score <= 1
        assert score > 0.5  # Should be effective with these metrics

    def test_false_positive_proxy(self, analyzer, mock_hourly_data):
        """Test false positive proxy calculation."""
        result = analyzer._aggregate_hourly_data(
            mock_hourly_data,
            datetime.now() - timedelta(hours=24),
            datetime.now()
        )

        fp_rate = result['effectiveness_metrics']['false_positive_proxy']
        assert 0 <= fp_rate <= 1

        # With 2 low confidence triggers per hour out of ~10 triggers
        expected_fp_rate = 2 / 10
        assert abs(fp_rate - expected_fp_rate) < 0.05  # Within 5%

    def test_empty_data_handling(self, analyzer):
        """Test graceful handling of no data."""
        result = analyzer._aggregate_hourly_data([], datetime.now(), datetime.now())

        assert result['trigger_metrics']['total_triggers'] == 0
        assert result['effectiveness_metrics']['effectiveness_score'] == 0.0

    @pytest.mark.asyncio
    async def test_get_rule_analytics_24h_integration(self, analyzer, mocker):
        """Integration test with mocked DynamoDB."""
        # Mock DynamoDB query
        mock_query = mocker.patch.object(analyzer.hourly_table, 'query')
        mock_query.return_value = {'Items': mock_hourly_data()}

        result = await analyzer.get_rule_analytics_24h('test-rule-1')

        assert result['rule_id'] == 'test-rule-1'
        assert 'trigger_metrics' in result
        assert 'effectiveness_metrics' in result
        assert 'hourly_breakdown' in result
```

### Integration Tests

**Lambda Aggregation Function:**
```python
# backend/api/lambda/test_aggregation_processor.py

import pytest
import boto3
from moto import mock_dynamodb
from aggregation_processor import lambda_handler, get_hour_bucket

@mock_dynamodb
class TestAggregationProcessor:

    @pytest.fixture(autouse=True)
    def setup_dynamodb(self):
        """Create mock DynamoDB tables."""
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

        # Create hourly analytics table
        table = dynamodb.create_table(
            TableName='quest-dev-safety-analytics-hourly',
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},
                {'AttributeName': 'sk', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        yield table

    def test_process_validation_events(self):
        """Test processing of validation events."""
        event = {
            'Records': [
                {
                    'eventName': 'INSERT',
                    'dynamodb': {
                        'NewImage': {
                            'validationId': {'S': 'val_123'},
                            'timestamp': {'S': '2025-10-22T14:30:00Z'},
                            'userId': {'S': 'user_456'},
                            'triggeredRules': {
                                'L': [
                                    {'S': 'rule_1'},
                                    {'S': 'rule_2'}
                                ]
                            },
                            'confidenceScore': {'N': '0.85'},
                            'requiresEscalation': {'BOOL': False},
                            'result': {'S': 'approved'},
                            'processingTimeMs': {'N': '234.5'}
                        }
                    }
                }
            ]
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 200
        assert 'rule-hour aggregations' in response['body']

        # Verify data written to DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('quest-dev-safety-analytics-hourly')

        hour_bucket = get_hour_bucket('2025-10-22T14:30:00Z')

        for rule_id in ['rule_1', 'rule_2']:
            item = table.get_item(
                Key={
                    'pk': f'rule#{rule_id}',
                    'sk': f'hour#{hour_bucket}'
                }
            )

            assert 'Item' in item
            assert item['Item']['trigger_count'] == 1
            assert float(item['Item']['avg_confidence']) == 0.85

    def test_handle_multiple_events_batched(self):
        """Test batch processing of multiple events."""
        # Create 100 events (batch size)
        records = []
        for i in range(100):
            records.append({
                'eventName': 'INSERT',
                'dynamodb': {
                    'NewImage': {
                        'validationId': {'S': f'val_{i}'},
                        'timestamp': {'S': '2025-10-22T14:30:00Z'},
                        'userId': {'S': f'user_{i % 10}'},
                        'triggeredRules': {'L': [{'S': 'rule_1'}]},
                        'confidenceScore': {'N': str(0.5 + (i % 50) / 100)},
                        'requiresEscalation': {'BOOL': i % 20 == 0},
                        'result': {'S': 'blocked' if i % 10 == 0 else 'approved'},
                        'processingTimeMs': {'N': str(200 + i)}
                    }
                }
            })

        event = {'Records': records}

        response = lambda_handler(event, None)

        assert response['statusCode'] == 200

        # Verify aggregated data
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('quest-dev-safety-analytics-hourly')

        hour_bucket = get_hour_bucket('2025-10-22T14:30:00Z')
        item = table.get_item(
            Key={'pk': 'rule#rule_1', 'sk': f'hour#{hour_bucket}'}
        )

        assert item['Item']['trigger_count'] == 100
        assert item['Item']['escalation_count'] == 5  # 100 / 20
        assert item['Item']['block_count'] == 10  # 100 / 10
```

### End-to-End Tests

**Playwright Frontend Tests:**
```typescript
// backend/api/src/main/python/tests/playwright/test_analytics_dashboard.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Rule Analytics Dashboard', () => {

  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@cmz.org');
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');

    // Navigate to analytics dashboard
    await page.goto('/safety/analytics');
  });

  test('should load dashboard with summary cards', async ({ page }) => {
    // Wait for data to load
    await page.waitForSelector('[data-testid="summary-card-triggers"]');

    // Verify summary cards are present
    const totalTriggers = await page.textContent('[data-testid="summary-card-triggers"]');
    const avgEffectiveness = await page.textContent('[data-testid="summary-card-effectiveness"]');
    const ineffectiveRules = await page.textContent('[data-testid="summary-card-ineffective"]');

    expect(totalTriggers).toBeTruthy();
    expect(avgEffectiveness).toMatch(/\d+\.\d{3}/); // Format: 0.XXX
    expect(ineffectiveRules).toMatch(/\d+/);
  });

  test('should render effectiveness bar chart', async ({ page }) => {
    await page.waitForSelector('[data-testid="effectiveness-chart"]');

    // Verify Recharts SVG is rendered
    const chartSvg = await page.locator('[data-testid="effectiveness-chart"] svg');
    expect(await chartSvg.count()).toBeGreaterThan(0);

    // Verify bars are present
    const bars = await page.locator('[data-testid="effectiveness-chart"] .recharts-bar-rectangle');
    expect(await bars.count()).toBeGreaterThan(0);
  });

  test('should allow time window selection', async ({ page }) => {
    // Change to 1-hour view
    await page.selectOption('select[name="timeWindow"]', '1h');

    // Wait for data refresh
    await page.waitForTimeout(1000);

    // Verify URL updated
    expect(page.url()).toContain('timeWindow=1h');

    // Verify data reloaded
    const loading = await page.locator('.loading-indicator');
    expect(await loading.count()).toBe(0);
  });

  test('should show rule details on row click', async ({ page }) => {
    await page.waitForSelector('[data-testid="rule-table"]');

    // Click first rule row
    await page.click('[data-testid="rule-table"] tbody tr:first-child');

    // Verify hourly trend chart updates
    await page.waitForSelector('[data-testid="hourly-trend-chart"]');

    const chartTitle = await page.textContent('[data-testid="hourly-trend-chart"] h3');
    expect(chartTitle).toContain('Hourly Trend:');

    // Verify 24 data points (hours)
    const dataPoints = await page.locator('[data-testid="hourly-trend-chart"] .recharts-line-dot');
    expect(await dataPoints.count()).toBe(24);
  });

  test('should auto-refresh every minute when enabled', async ({ page }) => {
    // Enable auto-refresh
    await page.check('input[name="autoRefresh"]');

    // Get initial trigger count
    const initialCount = await page.textContent('[data-testid="summary-card-triggers"]');

    // Wait 61 seconds for refresh
    await page.waitForTimeout(61000);

    // Verify data refreshed (may or may not change, but loading should occur)
    // Check that no error occurred
    const errorAlert = await page.locator('.error-alert');
    expect(await errorAlert.count()).toBe(0);
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API call and return error
    await page.route('**/guardrails/dashboard*', route =>
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal server error' })
      })
    );

    // Reload page
    await page.reload();

    // Verify error message displayed
    await page.waitForSelector('.error-alert');
    const errorMessage = await page.textContent('.error-alert');
    expect(errorMessage).toContain('Failed to load dashboard data');
  });

  test('should export data to CSV', async ({ page }) => {
    // Click export button
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-csv-button"]');
    const download = await downloadPromise;

    // Verify filename
    expect(download.suggestedFilename()).toMatch(/rule-analytics-\d{8}\.csv/);

    // Verify CSV content
    const path = await download.path();
    const fs = require('fs');
    const csvContent = fs.readFileSync(path, 'utf-8');

    expect(csvContent).toContain('Rule ID,Rule Text,Triggers,Effectiveness Score');
  });
});
```

---

## 13. Documentation Requirements

### API Documentation (OpenAPI)

Add to `backend/api/openapi_spec.yaml`:

```yaml
paths:
  /guardrails/rules/{ruleId}/analytics:
    get:
      summary: Get analytics for a specific guardrail rule
      tags:
        - Guardrails Analytics
      parameters:
        - name: ruleId
          in: path
          required: true
          schema:
            type: string
          description: Unique identifier of the guardrail rule
        - name: timeWindow
          in: query
          required: false
          schema:
            type: string
            enum: ['1h', '24h']
            default: '24h'
          description: Time window for analytics (1 hour or 24 hours)
      responses:
        '200':
          description: Rule analytics retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RuleAnalytics'
        '404':
          description: Rule not found
        '400':
          description: Invalid time window parameter

  /guardrails/dashboard:
    get:
      summary: Get dashboard analytics for all active rules
      tags:
        - Guardrails Analytics
      parameters:
        - name: timeWindow
          in: query
          required: false
          schema:
            type: string
            enum: ['1h', '24h']
            default: '24h'
        - name: sortBy
          in: query
          required: false
          schema:
            type: string
            enum: ['effectiveness', 'triggers', 'false_positives']
            default: 'effectiveness'
      responses:
        '200':
          description: Dashboard analytics retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RuleDashboard'

components:
  schemas:
    RuleAnalytics:
      type: object
      properties:
        rule_id:
          type: string
        rule_text:
          type: string
        rule_type:
          type: string
          enum: ['NEVER', 'ALWAYS', 'ENCOURAGE', 'DISCOURAGE']
        category:
          type: string
        severity:
          type: string
          enum: ['low', 'medium', 'high', 'critical']
        time_window:
          $ref: '#/components/schemas/TimeWindow'
        trigger_metrics:
          $ref: '#/components/schemas/TriggerMetrics'
        confidence_metrics:
          $ref: '#/components/schemas/ConfidenceMetrics'
        effectiveness_metrics:
          $ref: '#/components/schemas/EffectivenessMetrics'
        performance_metrics:
          $ref: '#/components/schemas/PerformanceMetrics'
        hourly_breakdown:
          type: array
          items:
            $ref: '#/components/schemas/HourlyDataPoint'

    TriggerMetrics:
      type: object
      properties:
        total_triggers:
          type: integer
          description: Total number of times rule was triggered
        unique_users:
          type: integer
          description: Number of unique users who triggered this rule
        avg_triggers_per_hour:
          type: number
          format: float
          description: Average triggers per hour in time window
        peak_hour:
          type: object
          properties:
            hour:
              type: string
              format: date-time
            triggers:
              type: integer

    EffectivenessMetrics:
      type: object
      properties:
        effectiveness_score:
          type: number
          format: float
          minimum: 0.0
          maximum: 1.0
          description: Composite effectiveness score (0.0 = ineffective, 1.0 = highly effective)
        escalation_rate:
          type: number
          format: float
          description: Percentage of triggers requiring escalation
        block_rate:
          type: number
          format: float
          description: Percentage of triggers resulting in blocked content
        false_positive_proxy:
          type: number
          format: float
          description: Estimated false positive rate based on low-confidence triggers
```

### User Documentation

Create `docs/analytics-user-guide.md`:

```markdown
# Rule Analytics Dashboard User Guide

## Overview

The Rule Analytics Dashboard provides real-time insights into the effectiveness
of your guardrail rules, helping administrators identify and optimize rules
that may not be performing as expected.

## Accessing the Dashboard

1. Log in with an admin account
2. Navigate to **Safety Management** → **Analytics** tab
3. The dashboard loads with 24-hour analytics by default

## Understanding Metrics

### Effectiveness Score (0.0 - 1.0)

**What it measures:** Overall performance of a guardrail rule

**Calculation:**
- 40% Confidence Score - How certain the system is when triggering the rule
- 30% Block Rate - Percentage of triggers resulting in blocked content
- 20% Inverse Escalation Rate - Lower escalations indicate better rule clarity
- 10% Volume Normalization - Penalizes extremely low or high trigger counts

**Interpretation:**
- 0.7 - 1.0: **Highly Effective** ✅ - Rule is performing well
- 0.4 - 0.7: **Moderate** ⚠️ - Consider reviewing rule criteria
- 0.0 - 0.4: **Ineffective** ❌ - Rule needs immediate attention

### False Positive Proxy

**What it measures:** Estimated rate of incorrect rule triggers

**Calculation:**
- Triggers with confidence < 0.5 (high uncertainty)
- High-confidence triggers with no action taken (unexpected safe content)

**Interpretation:**
- <10%: Good performance
- 10-30%: May need tuning
- >30%: High false positive rate, review rule urgently

## Using the Dashboard

### 1. Overview Summary Cards

Three key metrics at the top:
- **Total Triggers**: All rule activations in time window
- **Avg Effectiveness**: Mean effectiveness score across all rules
- **Ineffective Rules**: Count of rules with effectiveness < 0.5

### 2. Effectiveness Bar Chart

Visual comparison of all rules' effectiveness scores.

**How to use:**
- Identify underperforming rules (red/orange bars)
- Click bar to view detailed analytics for that rule
- Compare relative performance across rule categories

### 3. Hourly Trend Chart

Shows trigger frequency and confidence over the past 24 hours for selected rule.

**How to use:**
- Identify peak hours when rule is most active
- Spot patterns (e.g., higher triggers during school hours)
- Monitor confidence trends (declining confidence may indicate rule drift)

### 4. Confidence Distribution

Pie chart showing distribution of confidence scores for selected rule.

**How to use:**
- Healthy rules show most triggers in 0.8-1.0 range (green)
- Large 0.0-0.4 segment (red) indicates high false positive rate
- Balanced distribution across all ranges suggests unclear rule criteria

### 5. Rule Performance Table

Sortable table of all rules with key metrics.

**Actions:**
- **Click row**: View detailed hourly breakdown
- **View Details**: Navigate to rule configuration
- **Sort columns**: Identify worst-performing rules quickly

## Common Workflows

### Identifying Ineffective Rules

1. Set time window to **24h** (default)
2. Sort table by **Effectiveness** (ascending)
3. Review bottom 3-5 rules
4. For each ineffective rule:
   - Check confidence distribution (should be high)
   - Review recent triggers in hourly breakdown
   - Analyze false positive proxy rate
5. Decide action: **Tune**, **Disable**, or **Replace** rule

### Investigating High False Positive Rates

1. Select rule with FP rate > 30%
2. View confidence distribution chart
3. If most triggers in 0.0-0.4 range:
   - Rule criteria may be too broad
   - Consider adding more specific conditions
   - Review example triggers (link to validation logs)
4. If most triggers in 0.8-1.0 range but high FP:
   - Investigate why high-confidence triggers aren't resulting in blocks
   - May indicate legitimate use cases being flagged

### Monitoring New Rule Performance

1. After creating new rule, monitor for 24 hours
2. Check effectiveness score every 2-4 hours
3. Target: Effectiveness > 0.6 within first 24 hours
4. If below target:
   - Review confidence distribution
   - Check trigger volume (too low = insufficient data, too high = too broad)
   - Adjust rule criteria incrementally

## Time Windows

**1 Hour View:**
- Use for: Real-time monitoring, debugging new rules
- Refresh frequency: Every 5 minutes (manual)
- Data points: 60 (per-minute buckets)

**24 Hour View:**
- Use for: Daily performance reviews, trend analysis
- Refresh frequency: Every 60 minutes (auto-refresh)
- Data points: 24 (per-hour buckets)

## Troubleshooting

### "Data is X minutes old" Warning

**Cause:** Analytics aggregation is running behind

**Solution:**
- Wait 15 minutes and refresh
- If persists >30 minutes, contact technical support

### Missing Hourly Data Points

**Cause:** No triggers during that hour OR aggregation failure

**Solution:**
- Check if rule is active (`isActive: true`)
- Verify rule is being evaluated (check validation logs)
- If multiple consecutive hours missing, investigate aggregation pipeline

### Very Low Trigger Counts (<10 in 24h)

**Possible causes:**
1. Rule criteria too specific (not catching relevant content)
2. Low overall traffic to system
3. Rule category rarely encountered in conversations

**Actions:**
- Review rule text for overly restrictive conditions
- Check overall system usage metrics
- Consider broadening rule scope if appropriate

## Best Practices

1. **Daily Review**: Check dashboard once per day for anomalies
2. **Weekly Deep Dive**: Analyze bottom 5 rules by effectiveness
3. **Monthly Optimization**: Archive or modify rules with persistent low effectiveness
4. **Document Changes**: Note rule modifications in configuration description
5. **A/B Testing**: When tuning rules, compare effectiveness before/after changes

## Support

For technical issues with the analytics dashboard:
- Email: support@cmz.org
- Slack: #safety-analytics
- Documentation: https://docs.cmz.org/analytics
```

---

## 14. Risks and Mitigations

### Technical Risks

**Risk 1: DynamoDB Streams Lag**
- **Impact:** Analytics delayed >15 minutes, users see stale data
- **Probability:** Medium (during traffic spikes)
- **Mitigation:**
  - Monitor `IteratorAge` metric (alarm at >5 minutes)
  - Reserved Lambda concurrency (5 executions)
  - Automatic retry with exponential backoff
  - Display data freshness indicator in UI

**Risk 2: High-Cardinality Rule IDs**
- **Impact:** DynamoDB partition hot keys, throttling
- **Probability:** Low (unlikely >1000 rules)
- **Mitigation:**
  - Partition key design includes rule ID (distributes writes)
  - On-demand billing mode (auto-scales)
  - Monitor `ThrottledRequests` metric

**Risk 3: False Positive Proxy Inaccuracy**
- **Impact:** Administrators make incorrect decisions based on flawed metric
- **Probability:** Medium (proxy metric, not ground truth)
- **Mitigation:**
  - Clearly document proxy nature in UI and docs
  - Provide confidence distribution for manual verification
  - Link to validation logs for sample inspection
  - Plan for manual labeling system in Phase 2

**Risk 4: Frontend Performance Degradation**
- **Impact:** Dashboard slow to load (>5 seconds)
- **Probability:** Low (with current architecture)
- **Mitigation:**
  - Code-split analytics dashboard (lazy load)
  - Implement pagination for >50 rules
  - Cache API responses (5-minute TTL)
  - Consider Redis for frequently accessed data

### Operational Risks

**Risk 5: Undetected Aggregation Failures**
- **Impact:** Missing hourly data, incomplete analytics
- **Probability:** Low (with monitoring)
- **Mitigation:**
  - CloudWatch alarms on Lambda errors
  - DLQ for failed aggregations
  - Frontend health check displays data freshness
  - Automated recovery: re-process last hour from raw events

**Risk 6: Cost Overruns**
- **Impact:** Monthly cost exceeds $10/month budget
- **Probability:** Low (unless traffic 10x higher than estimated)
- **Mitigation:**
  - Implement cost alarms ($5 threshold warning)
  - TTL cleanup of old data (30 days)
  - Monitor DynamoDB and Lambda costs weekly
  - Use on-demand billing (only pay for usage)

### Business Risks

**Risk 7: Administrator Overwhelmed by Data**
- **Impact:** Low adoption of analytics dashboard
- **Probability:** Medium (complex dashboard)
- **Mitigation:**
  - Provide user training and documentation
  - Start with simple summary metrics
  - Add advanced features incrementally
  - Collect user feedback and iterate

**Risk 8: False Sense of Security**
- **Impact:** Administrators trust metrics blindly without manual verification
- **Probability:** Medium (human nature)
- **Mitigation:**
  - Include disclaimers about proxy metrics
  - Require manual spot-checks for rule changes
  - Provide links to raw validation logs
  - Regular admin training on metric interpretation

---

## 15. Future Enhancements

### Phase 2: Advanced Analytics (Q1 2026)

**Machine Learning Integration:**
- Predictive false positive detection using supervised ML
- Anomaly detection for unusual trigger patterns
- Automatic rule effectiveness alerts

**Enhanced Metrics:**
- True false positive rate (with manual labeling system)
- User satisfaction proxy (based on conversation completion rates)
- Comparative A/B testing framework for rule variants

**Advanced Visualizations:**
- Heatmaps for rule trigger patterns by time/day
- Correlation analysis between rules
- Predictive trend forecasting

### Phase 3: Automated Optimization (Q2 2026)

**Auto-Tuning System:**
- AI-powered rule suggestion engine
- Automatic rule disabling for persistent low effectiveness
- Rule consolidation recommendations (merge similar rules)

**Real-Time Alerts:**
- Slack/Teams notifications for sudden effectiveness drops
- Email digests for weekly performance summaries
- SMS alerts for critical rule failures

**Expanded Time Windows:**
- 7-day and 30-day analytics views
- Year-over-year comparisons
- Seasonal pattern analysis

---

## Conclusion

This architecture provides a **scalable, cost-effective, and performant** solution for rule effectiveness tracking in the CMZ Chatbots guardrails system. Key benefits:

**Scalability:**
- Handles 1000+ rules with consistent sub-second query times
- Automatically scales with traffic (on-demand billing)
- Supports 10x traffic growth without architecture changes

**Cost-Effectiveness:**
- Total monthly cost: $2.41 (84% savings vs. current approach)
- No upfront infrastructure costs
- Pay-per-use pricing aligns costs with usage

**Performance:**
- 24-hour analytics query: <500ms (p95)
- Dashboard load time: <2 seconds
- Real-time aggregation: <5 minute lag

**Maintainability:**
- Serverless architecture (no servers to manage)
- Automatic data cleanup via TTL
- Comprehensive monitoring and alerting

**User Experience:**
- Intuitive React dashboard with 4 chart types
- Auto-refresh for live monitoring
- Mobile-responsive design

**Implementation Timeline:**
- 6 weeks from kickoff to production rollout
- Incremental delivery with validation at each phase
- Low-risk deployment strategy (gradual rollout)

This solution positions the CMZ Chatbots safety system for **continuous improvement** through data-driven rule optimization, enabling administrators to maintain high-quality guardrails that protect users while minimizing false positives.

---

## Appendix A: DynamoDB Table Schemas

### Hourly Analytics Table

```python
{
    "TableName": "quest-dev-safety-analytics-hourly",
    "KeySchema": [
        {"AttributeName": "pk", "KeyType": "HASH"},
        {"AttributeName": "sk", "KeyType": "RANGE"}
    ],
    "AttributeDefinitions": [
        {"AttributeName": "pk", "AttributeType": "S"},
        {"AttributeName": "sk", "AttributeType": "S"},
        {"AttributeName": "hour_start", "AttributeType": "S"},
        {"AttributeName": "effectiveness_band", "AttributeType": "S"}
    ],
    "GlobalSecondaryIndexes": [
        {
            "IndexName": "TimeIndex",
            "KeySchema": [
                {"AttributeName": "hour_start", "KeyType": "HASH"},
                {"AttributeName": "pk", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        },
        {
            "IndexName": "EffectivenessIndex",
            "KeySchema": [
                {"AttributeName": "effectiveness_band", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ],
    "BillingMode": "PAY_PER_REQUEST",
    "StreamSpecification": {
        "StreamEnabled": false
    },
    "SSESpecification": {
        "Enabled": true
    },
    "TimeToLiveSpecification": {
        "Enabled": true,
        "AttributeName": "ttl"
    },
    "Tags": [
        {"Key": "Environment", "Value": "dev"},
        {"Key": "Project", "Value": "CMZ-Chatbots"},
        {"Key": "Component", "Value": "Safety-Analytics"}
    ]
}
```

---

## Appendix B: Environment Variables

### Lambda Function

```bash
# DynamoDB Configuration
HOURLY_TABLE_NAME=quest-dev-safety-analytics-hourly
AWS_REGION=us-west-2

# Processing Configuration
BATCH_SIZE=100
CONFIDENCE_THRESHOLD=0.5
LOW_CONFIDENCE_BUCKET=0.5

# Performance Tuning
ENABLE_XRAY=true
LOG_LEVEL=INFO

# Data Retention
TTL_DAYS=30
```

### Backend API

```bash
# Analytics Configuration
ANALYTICS_HOURLY_TABLE=quest-dev-safety-analytics-hourly
ANALYTICS_CACHE_TTL_SECONDS=300

# Feature Flags
ENABLE_ANALYTICS_DASHBOARD=true
ENABLE_AUTO_REFRESH=true

# Performance Limits
MAX_RULES_PER_DASHBOARD=100
MAX_HOURLY_DATA_POINTS=168  # 7 days
```

### Frontend

```bash
# API Configuration
REACT_APP_API_BASE_URL=https://api.cmz.org
REACT_APP_ANALYTICS_ENABLED=true

# Dashboard Configuration
REACT_APP_AUTO_REFRESH_INTERVAL_MS=60000
REACT_APP_HEALTH_CHECK_INTERVAL_MS=300000

# Feature Flags
REACT_APP_SHOW_DEBUG_INFO=false
```

---

## Appendix C: Useful Commands

### DynamoDB Queries

**Get rule analytics for specific hour:**
```bash
aws dynamodb query \
  --table-name quest-dev-safety-analytics-hourly \
  --key-condition-expression "pk = :pk AND sk = :sk" \
  --expression-attribute-values '{
    ":pk": {"S": "rule#test-rule-1"},
    ":sk": {"S": "hour#2025-10-22T14:00:00Z"}
  }'
```

**Get all rules for specific hour (GSI):**
```bash
aws dynamodb query \
  --table-name quest-dev-safety-analytics-hourly \
  --index-name TimeIndex \
  --key-condition-expression "hour_start = :hour" \
  --expression-attribute-values '{
    ":hour": {"S": "2025-10-22T14:00:00Z"}
  }'
```

**Scan for ineffective rules:**
```bash
aws dynamodb query \
  --table-name quest-dev-safety-analytics-hourly \
  --index-name EffectivenessIndex \
  --key-condition-expression "effectiveness_band = :band" \
  --expression-attribute-values '{
    ":band": {"S": "low"}
  }' \
  --filter-expression "effectiveness_score < :threshold" \
  --expression-attribute-values '{
    ":threshold": {"N": "0.5"}
  }'
```

### Lambda Function Management

**Invoke function locally (AWS SAM):**
```bash
sam local invoke AggregationProcessor \
  --event events/validation-event.json \
  --env-vars env.json
```

**View CloudWatch logs:**
```bash
aws logs tail /aws/lambda/safety-analytics-aggregator \
  --follow \
  --format short
```

**Update function code:**
```bash
cd backend/api/lambda
zip -r function.zip aggregation_processor.py requirements.txt
aws lambda update-function-code \
  --function-name safety-analytics-aggregator \
  --zip-file fileb://function.zip
```

### API Testing

**Get dashboard analytics:**
```bash
curl -H "Authorization: Bearer $AUTH_TOKEN" \
  "https://api.cmz.org/guardrails/dashboard?timeWindow=24h&sortBy=effectiveness" | jq
```

**Get specific rule analytics:**
```bash
curl -H "Authorization: Bearer $AUTH_TOKEN" \
  "https://api.cmz.org/guardrails/rules/rule-privacy-1/analytics?timeWindow=24h" | jq
```

---

**End of Document**

*For questions or clarifications, contact the CMZ technical team.*
