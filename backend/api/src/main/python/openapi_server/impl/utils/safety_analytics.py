"""
Safety Analytics and Monitoring for CMZ Chatbots safety system.

This module provides comprehensive analytics, monitoring, and reporting
capabilities for the content safety and guardrails systems.

Key Features:
- Safety event tracking and aggregation
- Risk score analytics and trending
- Guardrails rule effectiveness monitoring
- Content violation pattern analysis
- Performance metrics for safety systems
- Escalation tracking and response monitoring
- Educational content effectiveness analytics
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum

from .dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)
from .safety_dynamo import get_safety_dynamo_client
from .safety_errors import get_safety_error_handler

# Configure logging
logger = logging.getLogger(__name__)


class SafetyEventType(Enum):
    """Safety event types for analytics tracking."""
    CONTENT_VALIDATED = "content_validated"
    CONTENT_FLAGGED = "content_flagged"
    CONTENT_BLOCKED = "content_blocked"
    GUARDRAIL_TRIGGERED = "guardrail_triggered"
    ESCALATION_REQUIRED = "escalation_required"
    SAFE_ALTERNATIVE_PROVIDED = "safe_alternative_provided"
    OPENAI_MODERATION_TRIGGERED = "openai_moderation_triggered"
    CUSTOM_RULE_TRIGGERED = "custom_rule_triggered"
    CONFIGURATION_CREATED = "configuration_created"
    CONFIGURATION_UPDATED = "configuration_updated"
    PERFORMANCE_METRIC = "performance_metric"


class SafetyMetricType(Enum):
    """Safety metric types for monitoring."""
    VALIDATION_LATENCY = "validation_latency"
    OPENAI_API_LATENCY = "openai_api_latency"
    GUARDRAILS_PROCESSING_TIME = "guardrails_processing_time"
    TOTAL_CONTENT_VALIDATED = "total_content_validated"
    FLAGGED_CONTENT_RATE = "flagged_content_rate"
    BLOCKED_CONTENT_RATE = "blocked_content_rate"
    ESCALATION_RATE = "escalation_rate"
    RULE_EFFECTIVENESS = "rule_effectiveness"
    USER_ENGAGEMENT_SAFETY = "user_engagement_safety"


@dataclass
class SafetyAnalyticsEvent:
    """Safety analytics event data structure."""
    event_id: str
    event_type: SafetyEventType
    timestamp: str
    user_id: str
    conversation_id: str
    animal_id: Optional[str]
    content_hash: Optional[str]
    risk_score: Optional[float]
    triggered_rules: List[str]
    moderation_result: Optional[Dict[str, Any]]
    processing_time_ms: Optional[float]
    escalation_required: bool
    safe_alternative_provided: bool
    additional_data: Dict[str, Any]


class SafetyAnalytics:
    """Comprehensive safety analytics and monitoring service."""

    def __init__(self):
        """Initialize safety analytics manager."""
        self.safety_client = get_safety_dynamo_client()

        # Event aggregation cache
        self._event_cache: Dict[str, List[SafetyAnalyticsEvent]] = defaultdict(list)
        self._metric_cache: Dict[str, float] = {}
        self._cache_timestamp = datetime.now()
        self._cache_ttl_minutes = 15

    async def track_safety_event(
        self,
        event_type: SafetyEventType,
        user_id: str,
        conversation_id: str,
        animal_id: Optional[str] = None,
        content: Optional[str] = None,
        risk_score: Optional[float] = None,
        triggered_rules: Optional[List[str]] = None,
        moderation_result: Optional[Dict[str, Any]] = None,
        processing_time_ms: Optional[float] = None,
        escalation_required: bool = False,
        safe_alternative_provided: bool = False,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Track a safety event for analytics.

        Args:
            event_type: Type of safety event
            user_id: User ID associated with the event
            conversation_id: Conversation ID
            animal_id: Animal ID (if applicable)
            content: Content that triggered the event (will be hashed)
            risk_score: Risk score assigned to the content
            triggered_rules: List of rule IDs that were triggered
            moderation_result: OpenAI moderation API result
            processing_time_ms: Processing time in milliseconds
            escalation_required: Whether escalation was required
            safe_alternative_provided: Whether a safe alternative was provided
            additional_data: Additional event-specific data

        Returns:
            Event ID for tracking
        """
        try:
            # Generate event ID
            event_id = f"safety_event_{int(datetime.now().timestamp() * 1000)}_{user_id[:8]}"

            # Hash content for privacy
            content_hash = None
            if content:
                content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

            # Create event
            event = SafetyAnalyticsEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=now_iso(),
                user_id=user_id,
                conversation_id=conversation_id,
                animal_id=animal_id,
                content_hash=content_hash,
                risk_score=risk_score,
                triggered_rules=triggered_rules or [],
                moderation_result=moderation_result,
                processing_time_ms=processing_time_ms,
                escalation_required=escalation_required,
                safe_alternative_provided=safe_alternative_provided,
                additional_data=additional_data or {}
            )

            # Store event
            await self._store_analytics_event(event)

            # Update real-time metrics
            await self._update_real_time_metrics(event)

            logger.info(f"Tracked safety event: {event_type.value} for user {user_id}")
            return event_id

        except Exception as e:
            logger.error(f"Failed to track safety event: {e}")
            return ""

    async def get_safety_metrics(
        self,
        time_range: str = "24h",
        animal_id: Optional[str] = None,
        metric_types: Optional[List[SafetyMetricType]] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get safety metrics for specified time range.

        Args:
            time_range: Time range (1h, 24h, 7d, 30d)
            animal_id: Filter by specific animal
            metric_types: Specific metrics to retrieve

        Returns:
            Tuple of (metrics_data, status_code)
        """
        try:
            logger.info(f"Getting safety metrics for range: {time_range}")

            # Parse time range
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                return {"error": "Invalid time range"}, 400

            # Get events from time range
            events = await self._get_events_in_range(start_time, end_time, animal_id)

            # Calculate metrics
            metrics = await self._calculate_metrics(events, metric_types)

            # Add metadata
            metrics["metadata"] = {
                "time_range": time_range,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "animal_id": animal_id,
                "total_events": len(events),
                "generated_at": now_iso()
            }

            return metrics, 200

        except Exception as e:
            logger.error(f"Failed to get safety metrics: {e}")
            return error_response(e)

    async def get_safety_trends(
        self,
        metric_type: SafetyMetricType,
        time_range: str = "7d",
        granularity: str = "1h",
        animal_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get trending data for a specific safety metric.

        Args:
            metric_type: Type of metric to trend
            time_range: Overall time range
            granularity: Data point granularity (15m, 1h, 1d)
            animal_id: Filter by specific animal

        Returns:
            Tuple of (trend_data, status_code)
        """
        try:
            logger.info(f"Getting safety trends for {metric_type.value}")

            # Parse time range and granularity
            end_time = datetime.now()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                return {"error": "Invalid time range"}, 400

            # Calculate time buckets
            if granularity == "15m":
                bucket_size = timedelta(minutes=15)
            elif granularity == "1h":
                bucket_size = timedelta(hours=1)
            elif granularity == "1d":
                bucket_size = timedelta(days=1)
            else:
                return {"error": "Invalid granularity"}, 400

            # Get events and bucket them
            events = await self._get_events_in_range(start_time, end_time, animal_id)
            trend_data = await self._calculate_trend_buckets(
                events, metric_type, start_time, end_time, bucket_size
            )

            return {
                "metric_type": metric_type.value,
                "time_range": time_range,
                "granularity": granularity,
                "animal_id": animal_id,
                "data_points": trend_data,
                "metadata": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_count": len(trend_data),
                    "generated_at": now_iso()
                }
            }, 200

        except Exception as e:
            logger.error(f"Failed to get safety trends: {e}")
            return error_response(e)

    async def get_rule_effectiveness(
        self,
        time_range: str = "7d",
        animal_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Analyze guardrails rule effectiveness.

        Args:
            time_range: Time range for analysis
            animal_id: Filter by specific animal

        Returns:
            Tuple of (effectiveness_data, status_code)
        """
        try:
            logger.info(f"Analyzing rule effectiveness for range: {time_range}")

            # Get events
            end_time = datetime.now()
            if time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=7)

            events = await self._get_events_in_range(start_time, end_time, animal_id)

            # Analyze rule triggers
            rule_stats = defaultdict(lambda: {
                "trigger_count": 0,
                "escalation_count": 0,
                "effectiveness_score": 0.0,
                "average_risk_score": 0.0,
                "unique_users": set(),
                "recent_triggers": []
            })

            total_risk_scores = defaultdict(list)

            for event in events:
                if event.event_type == SafetyEventType.GUARDRAIL_TRIGGERED:
                    for rule_id in event.triggered_rules:
                        rule_stats[rule_id]["trigger_count"] += 1
                        rule_stats[rule_id]["unique_users"].add(event.user_id)

                        if event.escalation_required:
                            rule_stats[rule_id]["escalation_count"] += 1

                        if event.risk_score:
                            total_risk_scores[rule_id].append(event.risk_score)

                        rule_stats[rule_id]["recent_triggers"].append({
                            "timestamp": event.timestamp,
                            "risk_score": event.risk_score,
                            "escalation_required": event.escalation_required
                        })

            # Calculate effectiveness scores
            effectiveness_data = {}
            for rule_id, stats in rule_stats.items():
                if stats["trigger_count"] > 0:
                    # Effectiveness = (triggers - escalations) / triggers
                    effectiveness_score = max(0.0,
                        (stats["trigger_count"] - stats["escalation_count"]) / stats["trigger_count"]
                    )

                    avg_risk = (
                        sum(total_risk_scores[rule_id]) / len(total_risk_scores[rule_id])
                        if total_risk_scores[rule_id] else 0.0
                    )

                    effectiveness_data[rule_id] = {
                        "trigger_count": stats["trigger_count"],
                        "escalation_count": stats["escalation_count"],
                        "effectiveness_score": round(effectiveness_score, 3),
                        "average_risk_score": round(avg_risk, 3),
                        "unique_user_count": len(stats["unique_users"]),
                        "recent_triggers": stats["recent_triggers"][-5:]  # Last 5 triggers
                    }

            return {
                "time_range": time_range,
                "animal_id": animal_id,
                "rule_effectiveness": effectiveness_data,
                "summary": {
                    "total_rules_analyzed": len(effectiveness_data),
                    "total_triggers": sum(r["trigger_count"] for r in effectiveness_data.values()),
                    "total_escalations": sum(r["escalation_count"] for r in effectiveness_data.values()),
                    "overall_effectiveness": round(
                        sum(r["effectiveness_score"] for r in effectiveness_data.values()) /
                        len(effectiveness_data) if effectiveness_data else 0.0, 3
                    )
                },
                "generated_at": now_iso()
            }, 200

        except Exception as e:
            logger.error(f"Failed to analyze rule effectiveness: {e}")
            return error_response(e)

    async def _store_analytics_event(self, event: SafetyAnalyticsEvent) -> None:
        """Store analytics event in DynamoDB."""
        try:
            # Convert to DynamoDB format
            item = asdict(event)
            item["event_type"] = event.event_type.value
            item["pk"] = f"safety_event#{event.event_id}"
            item["sk"] = f"timestamp#{event.timestamp}"
            item["gsi1_pk"] = f"user#{event.user_id}"
            item["gsi1_sk"] = f"timestamp#{event.timestamp}"

            if event.animal_id:
                item["gsi2_pk"] = f"animal#{event.animal_id}"
                item["gsi2_sk"] = f"timestamp#{event.timestamp}"

            # Store in safety analytics table
            await self.safety_client.store_analytics_event(to_ddb(item))

        except Exception as e:
            logger.error(f"Failed to store analytics event: {e}")
            raise

    async def _update_real_time_metrics(self, event: SafetyAnalyticsEvent) -> None:
        """Update real-time metric counters."""
        try:
            # Update relevant counters based on event type
            if event.event_type == SafetyEventType.CONTENT_VALIDATED:
                await self._increment_metric("total_content_validated")
            elif event.event_type == SafetyEventType.CONTENT_FLAGGED:
                await self._increment_metric("flagged_content_count")
            elif event.event_type == SafetyEventType.CONTENT_BLOCKED:
                await self._increment_metric("blocked_content_count")
            elif event.event_type == SafetyEventType.ESCALATION_REQUIRED:
                await self._increment_metric("escalation_count")

            # Update performance metrics
            if event.processing_time_ms:
                await self._update_avg_metric("avg_processing_time", event.processing_time_ms)

        except Exception as e:
            logger.error(f"Failed to update real-time metrics: {e}")

    async def _get_events_in_range(
        self,
        start_time: datetime,
        end_time: datetime,
        animal_id: Optional[str] = None
    ) -> List[SafetyAnalyticsEvent]:
        """Get safety events within time range."""
        try:
            # Query DynamoDB for events in range
            # This is a simplified version - would need proper GSI queries
            events = await self.safety_client.query_analytics_events(
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                animal_id=animal_id
            )

            # Convert to SafetyAnalyticsEvent objects
            return [
                SafetyAnalyticsEvent(**from_ddb(event))
                for event in events
            ]

        except Exception as e:
            logger.error(f"Failed to get events in range: {e}")
            return []

    async def _calculate_metrics(
        self,
        events: List[SafetyAnalyticsEvent],
        metric_types: Optional[List[SafetyMetricType]] = None
    ) -> Dict[str, Any]:
        """Calculate safety metrics from events."""
        metrics = {}

        if not events:
            return metrics

        # Count events by type
        event_counts = Counter(event.event_type for event in events)

        # Basic counts
        total_validations = event_counts.get(SafetyEventType.CONTENT_VALIDATED, 0)
        total_flagged = event_counts.get(SafetyEventType.CONTENT_FLAGGED, 0)
        total_blocked = event_counts.get(SafetyEventType.CONTENT_BLOCKED, 0)
        total_escalations = event_counts.get(SafetyEventType.ESCALATION_REQUIRED, 0)

        # Calculate rates
        if total_validations > 0:
            metrics["flagged_content_rate"] = round(total_flagged / total_validations, 4)
            metrics["blocked_content_rate"] = round(total_blocked / total_validations, 4)
            metrics["escalation_rate"] = round(total_escalations / total_validations, 4)

        # Performance metrics
        processing_times = [
            event.processing_time_ms for event in events
            if event.processing_time_ms
        ]
        if processing_times:
            metrics["avg_processing_time_ms"] = round(sum(processing_times) / len(processing_times), 2)
            metrics["max_processing_time_ms"] = round(max(processing_times), 2)
            metrics["min_processing_time_ms"] = round(min(processing_times), 2)

        # Risk score analytics
        risk_scores = [event.risk_score for event in events if event.risk_score]
        if risk_scores:
            metrics["avg_risk_score"] = round(sum(risk_scores) / len(risk_scores), 3)
            metrics["max_risk_score"] = round(max(risk_scores), 3)
            metrics["high_risk_content_count"] = len([r for r in risk_scores if r > 0.7])

        # User engagement
        unique_users = len(set(event.user_id for event in events))
        unique_conversations = len(set(event.conversation_id for event in events))

        metrics.update({
            "total_events": len(events),
            "total_validations": total_validations,
            "total_flagged": total_flagged,
            "total_blocked": total_blocked,
            "total_escalations": total_escalations,
            "unique_users": unique_users,
            "unique_conversations": unique_conversations,
            "event_type_breakdown": dict(event_counts)
        })

        return metrics

    async def _calculate_trend_buckets(
        self,
        events: List[SafetyAnalyticsEvent],
        metric_type: SafetyMetricType,
        start_time: datetime,
        end_time: datetime,
        bucket_size: timedelta
    ) -> List[Dict[str, Any]]:
        """Calculate trend data in time buckets."""
        buckets = []
        current_time = start_time

        while current_time < end_time:
            bucket_end = min(current_time + bucket_size, end_time)

            # Filter events to this bucket
            bucket_events = [
                event for event in events
                if current_time <= datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')) < bucket_end
            ]

            # Calculate metric value for this bucket
            value = self._calculate_bucket_metric_value(bucket_events, metric_type)

            buckets.append({
                "timestamp": current_time.isoformat(),
                "value": value,
                "event_count": len(bucket_events)
            })

            current_time = bucket_end

        return buckets

    def _calculate_bucket_metric_value(
        self,
        events: List[SafetyAnalyticsEvent],
        metric_type: SafetyMetricType
    ) -> float:
        """Calculate metric value for a time bucket."""
        if not events:
            return 0.0

        if metric_type == SafetyMetricType.TOTAL_CONTENT_VALIDATED:
            return len([e for e in events if e.event_type == SafetyEventType.CONTENT_VALIDATED])
        elif metric_type == SafetyMetricType.FLAGGED_CONTENT_RATE:
            validated = len([e for e in events if e.event_type == SafetyEventType.CONTENT_VALIDATED])
            flagged = len([e for e in events if e.event_type == SafetyEventType.CONTENT_FLAGGED])
            return round(flagged / validated if validated > 0 else 0.0, 4)
        elif metric_type == SafetyMetricType.VALIDATION_LATENCY:
            times = [e.processing_time_ms for e in events if e.processing_time_ms]
            return round(sum(times) / len(times) if times else 0.0, 2)
        else:
            return 0.0

    async def _increment_metric(self, metric_name: str) -> None:
        """Increment a real-time metric counter."""
        # This would increment counters in DynamoDB or Redis
        pass

    async def _update_avg_metric(self, metric_name: str, value: float) -> None:
        """Update a real-time average metric."""
        # This would update rolling averages in DynamoDB or Redis
        pass


# Global analytics instance
_safety_analytics: Optional[SafetyAnalytics] = None


def get_safety_analytics() -> SafetyAnalytics:
    """Get singleton SafetyAnalytics instance."""
    global _safety_analytics

    if _safety_analytics is None:
        _safety_analytics = SafetyAnalytics()

    return _safety_analytics


# Handler functions for controllers
async def handle_get_safety_metrics(
    time_range: str = "24h",
    animal_id: Optional[str] = None,
    metric_types: Optional[str] = None
) -> Tuple[Any, int]:
    """Handle safety metrics retrieval."""
    analytics = get_safety_analytics()

    # Parse metric types if provided
    parsed_metric_types = None
    if metric_types:
        try:
            parsed_metric_types = [
                SafetyMetricType(t.strip())
                for t in metric_types.split(',')
            ]
        except ValueError as e:
            return {"error": f"Invalid metric type: {e}"}, 400

    return await analytics.get_safety_metrics(time_range, animal_id, parsed_metric_types)


async def handle_get_safety_trends(
    metric_type: str,
    time_range: str = "7d",
    granularity: str = "1h",
    animal_id: Optional[str] = None
) -> Tuple[Any, int]:
    """Handle safety trends retrieval."""
    analytics = get_safety_analytics()

    try:
        parsed_metric_type = SafetyMetricType(metric_type)
    except ValueError:
        return {"error": f"Invalid metric type: {metric_type}"}, 400

    return await analytics.get_safety_trends(
        parsed_metric_type, time_range, granularity, animal_id
    )


async def handle_get_rule_effectiveness(
    time_range: str = "7d",
    animal_id: Optional[str] = None
) -> Tuple[Any, int]:
    """Handle rule effectiveness analysis."""
    analytics = get_safety_analytics()
    return await analytics.get_rule_effectiveness(time_range, animal_id)