/**
 * CollapsibleRuleCard Component
 *
 * Individual rule card that displays triggered guardrail rule information
 * with expandable details, severity indicators, and accessibility features.
 * Supports WCAG 2.1 AA compliance with proper focus management and screen reader support.
 */

import React, { useRef, useEffect } from 'react';
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import {
  TriggeredRule,
  CollapsibleRuleCardProps,
  SEVERITY_COLORS,
  CATEGORY_ICONS,
  RULE_TYPE_LABELS
} from '../../types/GuardrailTypes';

const CollapsibleRuleCard: React.FC<CollapsibleRuleCardProps> = ({
  rule,
  isExpanded,
  onToggle,
  showDetails = true,
  showContext = true
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const toggleButtonRef = useRef<HTMLButtonElement>(null);

  // Format timestamp for display
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch (error) {
      return timestamp; // Fallback to raw timestamp
    }
  };

  // Get severity color for visual indicators
  const getSeverityColor = (severity: string) => {
    return SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || SEVERITY_COLORS.none;
  };

  // Get category icon
  const getCategoryIcon = (category: string) => {
    return CATEGORY_ICONS[category as keyof typeof CATEGORY_ICONS] || '⚠️';
  };

  // Get confidence level description
  const getConfidenceLevel = (score: number) => {
    if (score >= 90) return 'Very High';
    if (score >= 75) return 'High';
    if (score >= 60) return 'Medium';
    if (score >= 50) return 'Low';
    return 'Very Low';
  };

  // Get confidence color based on score
  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'text-green-700 bg-green-100';
    if (score >= 75) return 'text-blue-700 bg-blue-100';
    if (score >= 60) return 'text-yellow-700 bg-yellow-100';
    if (score >= 50) return 'text-orange-700 bg-orange-100';
    return 'text-red-700 bg-red-100';
  };

  // Handle keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onToggle();
    }
  };

  // Focus management for accessibility
  useEffect(() => {
    if (isExpanded && cardRef.current) {
      // Announce expansion to screen readers
      const announcement = `Rule details expanded: ${rule.ruleText}`;
      const liveRegion = document.createElement('div');
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      liveRegion.textContent = announcement;
      document.body.appendChild(liveRegion);

      // Clean up after announcement
      setTimeout(() => {
        document.body.removeChild(liveRegion);
      }, 1000);
    }
  }, [isExpanded, rule.ruleText]);

  const severityColor = getSeverityColor(rule.severity);
  const categoryIcon = getCategoryIcon(rule.category);
  const confidenceLevel = getConfidenceLevel(rule.confidenceScore);
  const confidenceColorClass = getConfidenceColor(rule.confidenceScore);

  return (
    <div
      ref={cardRef}
      className={`border rounded-lg transition-all duration-200 ${
        isExpanded
          ? 'border-blue-300 shadow-md bg-blue-50'
          : 'border-gray-200 hover:border-gray-300 hover:shadow-sm bg-white'
      }`}
      role="region"
      aria-labelledby={`rule-${rule.ruleId}-title`}
    >
      {/* Header - Always Visible */}
      <button
        ref={toggleButtonRef}
        onClick={onToggle}
        onKeyDown={handleKeyDown}
        className={`w-full p-4 text-left focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset rounded-lg transition-colors ${
          isExpanded ? 'bg-blue-50' : 'bg-white hover:bg-gray-50'
        }`}
        aria-expanded={isExpanded}
        aria-controls={`rule-${rule.ruleId}-details`}
        aria-describedby={`rule-${rule.ruleId}-summary`}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            {/* Rule Header */}
            <div className="flex items-center space-x-3 mb-2">
              {/* Category Icon */}
              <span className="text-lg" aria-hidden="true">
                {categoryIcon}
              </span>

              {/* Rule Type */}
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                {RULE_TYPE_LABELS[rule.ruleType] || rule.ruleType}
              </span>

              {/* Severity Badge */}
              <span
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                style={{ backgroundColor: severityColor }}
                aria-label={`Severity: ${rule.severity}`}
              >
                {rule.severity.charAt(0).toUpperCase() + rule.severity.slice(1)}
              </span>

              {/* Confidence Score */}
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${confidenceColorClass}`}
                aria-label={`Confidence: ${rule.confidenceScore}% (${confidenceLevel})`}
              >
                {rule.confidenceScore.toFixed(1)}% {confidenceLevel}
              </span>
            </div>

            {/* Rule Text */}
            <h4
              id={`rule-${rule.ruleId}-title`}
              className="text-sm font-medium text-gray-900 mb-1"
            >
              {rule.ruleText}
            </h4>

            {/* Summary Info */}
            <div
              id={`rule-${rule.ruleId}-summary`}
              className="text-sm text-gray-600"
            >
              <span className="capitalize">{rule.category}</span> rule
              {rule.priority && (
                <span> • Priority {rule.priority}</span>
              )}
              <span> • Detected {formatTimestamp(rule.detectedAt)}</span>
            </div>
          </div>

          {/* Expand/Collapse Icon */}
          <div className="flex-shrink-0 ml-4">
            {isExpanded ? (
              <ChevronDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            ) : (
              <ChevronRightIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            )}
          </div>
        </div>
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div
          id={`rule-${rule.ruleId}-details`}
          className="px-4 pb-4 border-t border-blue-200 bg-white"
          role="region"
          aria-labelledby={`rule-${rule.ruleId}-title`}
        >
          <div className="space-y-4 pt-4">
            {/* Rule Details */}
            {showDetails && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h5 className="text-xs font-medium text-gray-700 uppercase tracking-wide mb-2">
                    Rule Information
                  </h5>
                  <dl className="space-y-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Rule ID</dt>
                      <dd className="text-sm text-gray-900 font-mono">{rule.ruleId}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Category</dt>
                      <dd className="text-sm text-gray-900 capitalize">
                        {categoryIcon} {rule.category}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Type</dt>
                      <dd className="text-sm text-gray-900">
                        {RULE_TYPE_LABELS[rule.ruleType] || rule.ruleType}
                      </dd>
                    </div>
                    {rule.priority && (
                      <div>
                        <dt className="text-sm font-medium text-gray-600">Priority</dt>
                        <dd className="text-sm text-gray-900">{rule.priority}</dd>
                      </div>
                    )}
                  </dl>
                </div>

                <div>
                  <h5 className="text-xs font-medium text-gray-700 uppercase tracking-wide mb-2">
                    Detection Details
                  </h5>
                  <dl className="space-y-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Confidence Score</dt>
                      <dd className="text-sm text-gray-900">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="h-2 rounded-full transition-all duration-300"
                              style={{
                                width: `${rule.confidenceScore}%`,
                                backgroundColor: severityColor
                              }}
                              aria-hidden="true"
                            />
                          </div>
                          <span className="font-medium">
                            {rule.confidenceScore.toFixed(1)}%
                          </span>
                        </div>
                        <span className="text-xs text-gray-500">{confidenceLevel} confidence</span>
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Severity Level</dt>
                      <dd className="text-sm text-gray-900">
                        <span
                          className="inline-flex items-center px-2 py-1 rounded text-xs font-medium text-white"
                          style={{ backgroundColor: severityColor }}
                        >
                          {rule.severity.charAt(0).toUpperCase() + rule.severity.slice(1)}
                        </span>
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-600">Detected At</dt>
                      <dd className="text-sm text-gray-900 font-mono">
                        {formatTimestamp(rule.detectedAt)}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            )}

            {/* Context Information */}
            {showContext && rule.triggerContext && (
              <div>
                <h5 className="text-xs font-medium text-gray-700 uppercase tracking-wide mb-2">
                  Trigger Context
                </h5>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm text-gray-700">{rule.triggerContext}</p>
                </div>
              </div>
            )}

            {/* User Message */}
            {rule.userMessage && (
              <div>
                <h5 className="text-xs font-medium text-gray-700 uppercase tracking-wide mb-2">
                  User Guidance
                </h5>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-800">{rule.userMessage}</p>
                </div>
              </div>
            )}

            {/* Educational Note for Content Creators */}
            {rule.ruleType === 'DISCOURAGE' && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <div className="flex items-start">
                  <svg className="h-5 w-5 text-yellow-400 mt-0.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <div className="ml-3">
                    <h6 className="text-sm font-medium text-yellow-800">
                      Content Guidance
                    </h6>
                    <p className="text-sm text-yellow-700 mt-1">
                      Consider revising this content to better align with educational goals and age-appropriate guidelines.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CollapsibleRuleCard;