"""
OpenAI Guardrails Evaluation for CMZ Chatbots

This module provides OpenAI-powered guardrails evaluation using chat completions.
It sends user content and guardrail rules to OpenAI for evaluation, similar to how
you've configured your Pokey GPT with specific guardrails and behavior modes.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIGuardrailsEvaluator:
    """OpenAI-powered guardrails evaluation system."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = None
        self._setup_client()

    def _setup_client(self):
        """Setup OpenAI client with API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not found. OpenAI integration will be disabled.")
            return

        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI guardrails evaluator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    async def evaluate_content_with_guardrails(
        self,
        content: str,
        guardrails_rules: List[Dict[str, Any]],
        context: Dict[str, Any],
        animal_personality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate content against guardrails using OpenAI.

        This follows the pattern of your Pokey GPT configuration, where specific
        guardrails are evaluated against user content to determine safety.

        Args:
            content: User content to evaluate
            guardrails_rules: List of guardrail rules to check against
            context: Validation context (animalId, userId, etc.)
            animal_personality: Optional animal personality description

        Returns:
            Detailed evaluation results including triggered rules and recommendations
        """
        if not self.client:
            logger.warning("OpenAI client not available, falling back to mock validation")
            return await self._fallback_validation(content, guardrails_rules, context)

        try:
            # Build the evaluation prompt based on your Pokey pattern
            evaluation_prompt = self._build_evaluation_prompt(
                content, guardrails_rules, context, animal_personality
            )

            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use cost-effective model for guardrails
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            # Parse OpenAI response
            evaluation_result = json.loads(response.choices[0].message.content)

            # Format the response according to our API specification
            formatted_result = self._format_evaluation_result(
                evaluation_result, content, context, response
            )

            logger.info(f"OpenAI evaluation completed: {formatted_result.get('result', 'unknown')}")
            return formatted_result

        except Exception as e:
            logger.error(f"OpenAI evaluation failed: {e}")
            # Fall back to mock validation on error
            return await self._fallback_validation(content, guardrails_rules, context)

    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the guardrails evaluator's behavior."""
        return """You are a content safety evaluator for a children's zoo education platform, similar to the guardrails system used for zoo animal digital ambassadors.

Your job is to evaluate user messages against specific guardrails and provide detailed feedback. You should:

1. Be protective of children's safety and educational experience
2. Maintain age-appropriate content standards for elementary school children (ages 5-12)
3. Block or flag inappropriate content while providing constructive guidance
4. Encourage educational exploration within safe boundaries
5. Respect privacy and never request personal information
6. Support the educational mission of the zoo

You will receive specific guardrail rules to evaluate against, similar to how animal digital ambassadors have specific behavioral guidelines. Evaluate content carefully and provide detailed reasoning for any rule violations."""

    def _build_evaluation_prompt(
        self,
        content: str,
        rules: List[Dict[str, Any]],
        context: Dict[str, Any],
        animal_personality: Optional[str] = None
    ) -> str:
        """Build the evaluation prompt for OpenAI based on your Pokey GPT pattern."""
        animal_id = context.get('animalId', 'an animal')

        # Format rules for the prompt (similar to your Pokey guardrails)
        rules_text = ""
        for rule in rules:
            rules_text += f"- Rule ID: {rule.get('ruleId', 'unknown')}\n"
            rules_text += f"  Type: {rule.get('type', 'DISCOURAGE')}\n"
            rules_text += f"  Rule: {rule.get('rule', '')}\n"
            rules_text += f"  Category: {rule.get('category', 'general')}\n"
            rules_text += f"  Severity: {rule.get('severity', 'medium')}\n"
            rules_text += f"  Priority: {rule.get('priority', 50)}\n\n"

        personality_context = ""
        if animal_personality:
            personality_context = f"\nAnimal Personality Context:\n{animal_personality}\n"

        prompt = f"""
Please evaluate the following user message against the guardrails for a children's zoo education chatbot representing {animal_id}.

This evaluation follows the same pattern as zoo digital ambassadors (like Pokey the prehensile-tailed porcupine) who have specific behavioral guidelines and safety measures.

User Message to Evaluate:
"{content}"

Context:
- Animal: {animal_id}
- User ID: {context.get('userId', 'anonymous')}
- Target Audience: Elementary school children (ages 5-12)
- Platform: Zoo educational chatbot
{personality_context}
Guardrails Rules to Check (Similar to Pokey's Guardrails):
{rules_text}

Please provide your evaluation as a JSON object with the following structure:
{{
    "result": "approved|flagged|escalated",
    "riskScore": 0.0-1.0,
    "requiresEscalation": boolean,
    "triggeredRules": [
        {{
            "ruleId": "string",
            "ruleText": "string",
            "ruleType": "ALWAYS|NEVER|ENCOURAGE|DISCOURAGE",
            "category": "string",
            "severity": "low|medium|high|critical",
            "confidenceScore": 0.0-100.0,
            "triggerContext": "explanation of why this rule was triggered",
            "userMessage": "child-friendly message to show the user",
            "keywordsMatched": ["list", "of", "keywords"]
        }}
    ],
    "userMessage": "optional overall message to user if content is problematic",
    "recommendations": [
        "list of suggestions for better content"
    ],
    "educationalRedirect": "suggestion for educational topic to redirect conversation"
}}

Evaluation Guidelines (Based on Your Pokey GPT Pattern):
1. "approved" - Content is safe and appropriate for elementary children
2. "flagged" - Content has minor issues but can be handled with guidance
3. "escalated" - Content requires immediate intervention (violence, inappropriate content, etc.)

Key Safety Rules (Similar to Pokey's Guardrails):
- Never discuss violence, fighting, or harm to animals
- Avoid all violent, frightening, or adult content
- Keep discussions age-appropriate for children
- Never request or encourage sharing personal information
- Gently redirect off-topic questions to educational content
- Stay focused on educational and positive animal topics
- No sarcasm or confusing language
- Encourage curiosity and learning within safe boundaries

For each triggered rule, explain WHY it was triggered with specific evidence. Confidence scores should reflect how certain you are about the rule violation (50-100). User messages should be encouraging and redirect to positive learning, just like how Pokey would handle inappropriate questions.
"""
        return prompt

    def _format_evaluation_result(
        self,
        openai_result: Dict[str, Any],
        original_content: str,
        context: Dict[str, Any],
        openai_response: Any
    ) -> Dict[str, Any]:
        """Format OpenAI evaluation result to match our API specification."""

        triggered_rules = openai_result.get('triggeredRules', [])

        # Determine highest severity
        severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        highest_severity = "none"
        for rule in triggered_rules:
            rule_severity = rule.get('severity', 'low')
            if severity_order.get(rule_severity, 1) > severity_order.get(highest_severity, 0):
                highest_severity = rule_severity

        # Count violations by severity
        blocking_violations = len([r for r in triggered_rules if r.get('severity') in ['high', 'critical']])
        warning_violations = len([r for r in triggered_rules if r.get('severity') in ['low', 'medium']])

        result = openai_result.get('result', 'approved')
        requires_escalation = openai_result.get('requiresEscalation', False) or result == 'escalated'

        # Add OpenAI usage metadata to rules
        for rule in triggered_rules:
            rule['detectedAt'] = datetime.utcnow().isoformat()
            rule['detectedBy'] = 'openai-gpt-4o-mini'

        formatted_response = {
            "valid": result in ["approved", "flagged"],
            "result": result,
            "riskScore": float(openai_result.get('riskScore', 0.0)),
            "requiresEscalation": requires_escalation,
            "validationId": f"openai_{hash(original_content + str(datetime.now().timestamp()))}",
            "processingTimeMs": 250,  # Estimate for OpenAI call
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "triggeredRules": {
                "totalTriggered": len(triggered_rules),
                "highestSeverity": highest_severity,
                "customGuardrails": triggered_rules,
                "openaiModeration": {
                    "model": "gpt-4o-mini",
                    "evaluationMethod": "chat_completion_guardrails",
                    "promptEngineered": True,
                    "guardrailsPattern": "pokey_style"
                }
            },
            "summary": {
                "requiresEscalation": requires_escalation,
                "blockingViolations": blocking_violations,
                "warningViolations": warning_violations,
                "ageGroupApproved": "elementary" if result == "approved" else "none"
            },
            "openaiMeta": {
                "model": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": getattr(openai_response.usage, 'prompt_tokens', 0),
                    "completion_tokens": getattr(openai_response.usage, 'completion_tokens', 0),
                    "total_tokens": getattr(openai_response.usage, 'total_tokens', 0)
                }
            }
        }

        # Add user message if provided
        if openai_result.get('userMessage'):
            formatted_response['userMessage'] = openai_result['userMessage']

        # Add educational redirect if provided
        if openai_result.get('educationalRedirect'):
            formatted_response['educationalRedirect'] = {
                "suggested": True,
                "topic": openai_result['educationalRedirect'],
                "reason": "Content guidance"
            }

        # Add recommendations if provided
        if openai_result.get('recommendations'):
            formatted_response['recommendations'] = openai_result['recommendations']

        return formatted_response

    async def _fallback_validation(
        self,
        content: str,
        rules: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback validation when OpenAI is not available."""
        logger.info("Using fallback validation (OpenAI not available)")

        # Simple keyword-based validation
        risk_score = 0.0
        triggered_rules = []
        result = "approved"

        # Basic content checks following Pokey's patterns
        content_lower = content.lower()

        # Check for violence/harm (Pokey's key guardrail)
        if any(word in content_lower for word in ["violence", "fight", "hurt", "kill", "harm", "attack", "damage"]):
            risk_score = 0.85
            result = "escalated"
            triggered_rules.append({
                "ruleId": "fallback_violence_001",
                "ruleText": "Never discuss violence or harm to animals",
                "ruleType": "NEVER",
                "category": "safety",
                "severity": "high",
                "confidenceScore": 85.0,
                "triggerContext": "Violence-related keywords detected (following Pokey guardrail pattern)",
                "userMessage": f"We don't discuss animals being hurt. Let's learn about how we keep {context.get('animalId', 'animals')} safe and healthy!",
                "detectedAt": datetime.utcnow().isoformat(),
                "detectedBy": "fallback-validator",
                "keywordsMatched": [word for word in ["violence", "fight", "hurt", "kill", "harm", "attack", "damage"] if word in content_lower]
            })

        # Check for inappropriate content (Pokey avoids adult topics)
        if any(word in content_lower for word in ["adult", "scary", "political", "sarcasm"]):
            risk_score = max(risk_score, 0.65)
            result = "flagged" if result == "approved" else result
            triggered_rules.append({
                "ruleId": "fallback_inappropriate_002",
                "ruleText": "Keep discussions age-appropriate for elementary students",
                "ruleType": "ALWAYS",
                "category": "age-appropriate",
                "severity": "medium",
                "confidenceScore": 65.0,
                "triggerContext": "Age-inappropriate content detected (following Pokey guardrail pattern)",
                "userMessage": f"Let's keep our conversation fun and educational about {context.get('animalId', 'animals')}!",
                "detectedAt": datetime.utcnow().isoformat(),
                "detectedBy": "fallback-validator",
                "keywordsMatched": [word for word in ["adult", "scary", "political", "sarcasm"] if word in content_lower]
            })

        return {
            "valid": result in ["approved", "flagged"],
            "result": result,
            "riskScore": risk_score,
            "requiresEscalation": result == "escalated",
            "validationId": f"fallback_{hash(content)}",
            "processingTimeMs": 50,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "triggeredRules": {
                "totalTriggered": len(triggered_rules),
                "highestSeverity": "high" if any(r.get("severity") == "high" for r in triggered_rules) else "medium" if triggered_rules else "none",
                "customGuardrails": triggered_rules,
                "fallbackMode": True,
                "guardrailsPattern": "pokey_style_fallback"
            },
            "summary": {
                "requiresEscalation": result == "escalated",
                "blockingViolations": len([r for r in triggered_rules if r.get("severity") == "high"]),
                "warningViolations": len([r for r in triggered_rules if r.get("severity") == "medium"]),
                "ageGroupApproved": "elementary" if result == "approved" else "none"
            }
        }


# Global evaluator instance
_openai_guardrails_evaluator: Optional[OpenAIGuardrailsEvaluator] = None


def get_openai_guardrails_evaluator() -> OpenAIGuardrailsEvaluator:
    """Get singleton OpenAI guardrails evaluator instance."""
    global _openai_guardrails_evaluator

    if _openai_guardrails_evaluator is None:
        _openai_guardrails_evaluator = OpenAIGuardrailsEvaluator()

    return _openai_guardrails_evaluator


async def evaluate_content_with_openai_guardrails(
    content: str,
    guardrails_rules: List[Dict[str, Any]],
    context: Dict[str, Any],
    animal_personality: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for OpenAI-powered guardrails evaluation.

    This function follows the pattern of your Pokey GPT configuration.

    Args:
        content: User content to evaluate
        guardrails_rules: List of guardrail rules (like Pokey's guardrails)
        context: Validation context
        animal_personality: Optional animal personality description

    Returns:
        Detailed evaluation results
    """
    evaluator = get_openai_guardrails_evaluator()
    return await evaluator.evaluate_content_with_guardrails(
        content, guardrails_rules, context, animal_personality
    )