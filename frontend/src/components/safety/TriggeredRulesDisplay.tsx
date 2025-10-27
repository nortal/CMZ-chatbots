/**
 * TriggeredRulesDisplay Component
 *
 * Displays detailed information about triggered guardrail rules including
 * categories, severity levels, and confidence scores for content administrators.
 * Supports sorting, grouping, and interactive rule exploration.
 */

import React, { useState, useMemo } from 'react';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import {
  DetailedValidationResponse,
  TriggeredRule,
  TriggeredRulesDisplayProps,
  RuleSortOptions,
  RuleFilterOptions,
  SEVERITY_COLORS,
  CATEGORY_ICONS,
  RULE_TYPE_LABELS
} from '../../types/GuardrailTypes';
import CollapsibleRuleCard from './CollapsibleRuleCard';

const TriggeredRulesDisplay: React.FC<TriggeredRulesDisplayProps> = ({
  validationResult,
  sortBy = 'severity',
  groupBy = 'none',
  showAnalytics = false,
  onRuleClick
}) => {
  const [expandedRules, setExpandedRules] = useState<Set<string>>(new Set());
  const [sortOptions, setSortOptions] = useState<RuleSortOptions>({
    field: sortBy,
    direction: 'desc'
  });
  const [filterOptions, setFilterOptions] = useState<RuleFilterOptions>({
    severities: [],
    categories: [],
    types: [],
    minConfidence: 0,
    maxConfidence: 100
  });

  // Extract triggered rules from validation result
  const triggeredRules = useMemo(() => {
    if (!validationResult?.triggeredRules?.customGuardrails) {
      return [];
    }
    return validationResult.triggeredRules.customGuardrails;
  }, [validationResult]);

  // Apply filters to rules
  const filteredRules = useMemo(() => {
    return triggeredRules.filter(rule => {
      // Severity filter
      if (filterOptions.severities && filterOptions.severities.length > 0) {
        if (!filterOptions.severities.includes(rule.severity)) {
          return false;
        }
      }

      // Category filter
      if (filterOptions.categories && filterOptions.categories.length > 0) {
        if (!filterOptions.categories.includes(rule.category)) {
          return false;
        }
      }

      // Type filter
      if (filterOptions.types && filterOptions.types.length > 0) {
        if (!filterOptions.types.includes(rule.ruleType)) {
          return false;
        }
      }

      // Confidence range filter
      if (rule.confidenceScore < (filterOptions.minConfidence || 0) ||
          rule.confidenceScore > (filterOptions.maxConfidence || 100)) {
        return false;
      }

      return true;
    });
  }, [triggeredRules, filterOptions]);

  // Sort rules based on current sort options
  const sortedRules = useMemo(() => {
    const sorted = [...filteredRules];

    sorted.sort((a, b) => {
      let comparison = 0;

      switch (sortOptions.field) {
        case 'severity':
          const severityOrder = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1 };
          comparison = (severityOrder[a.severity as keyof typeof severityOrder] || 0) -
                      (severityOrder[b.severity as keyof typeof severityOrder] || 0);
          break;
        case 'confidence':
          comparison = a.confidenceScore - b.confidenceScore;
          break;
        case 'timestamp':
          comparison = new Date(a.detectedAt).getTime() - new Date(b.detectedAt).getTime();
          break;
        case 'category':
          comparison = a.category.localeCompare(b.category);
          break;
        default:
          comparison = 0;
      }

      return sortOptions.direction === 'desc' ? -comparison : comparison;
    });

    return sorted;
  }, [filteredRules, sortOptions]);

  // Group rules if grouping is enabled
  const groupedRules = useMemo(() => {
    if (groupBy === 'none') {
      return { 'All Rules': sortedRules };
    }

    const groups: Record<string, TriggeredRule[]> = {};

    sortedRules.forEach(rule => {
      let groupKey = '';

      switch (groupBy) {
        case 'severity':
          groupKey = rule.severity.charAt(0).toUpperCase() + rule.severity.slice(1);
          break;
        case 'type':
          groupKey = RULE_TYPE_LABELS[rule.ruleType] || rule.ruleType;
          break;
        case 'category':
          groupKey = rule.category.charAt(0).toUpperCase() + rule.category.slice(1);
          break;
        default:
          groupKey = 'All Rules';
      }

      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(rule);
    });

    return groups;
  }, [sortedRules, groupBy]);

  const handleRuleToggle = (ruleId: string) => {
    const newExpanded = new Set(expandedRules);
    if (newExpanded.has(ruleId)) {
      newExpanded.delete(ruleId);
    } else {
      newExpanded.add(ruleId);
    }
    setExpandedRules(newExpanded);
  };

  const handleSortChange = (field: RuleSortOptions['field']) => {
    setSortOptions(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const getSeverityBadgeColor = (severity: string) => {
    return SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || SEVERITY_COLORS.none;
  };

  const getOverallSummary = () => {
    const total = triggeredRules.length;
    const highestSeverity = validationResult.triggeredRules.highestSeverity;
    const openaiTriggered = validationResult.triggeredRules.openaiModeration?.flagged || false;

    return {
      total,
      highestSeverity,
      openaiTriggered,
      requiresEscalation: validationResult.summary.requiresEscalation,
      blockingViolations: validationResult.summary.blockingViolations,
      warningViolations: validationResult.summary.warningViolations
    };
  };

  const summary = getOverallSummary();

  if (triggeredRules.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800">
              No Guardrail Rules Triggered
            </h3>
            <p className="text-sm text-green-700 mt-1">
              Content passed all safety checks without triggering any custom guardrail rules.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-3">
          Triggered Rules Summary
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm font-medium text-gray-500">Total Rules</div>
            <div className="text-2xl font-bold text-gray-900">{summary.total}</div>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm font-medium text-gray-500">Highest Severity</div>
            <div className="flex items-center mt-1">
              <span
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                style={{ backgroundColor: getSeverityBadgeColor(summary.highestSeverity) }}
              >
                {summary.highestSeverity.charAt(0).toUpperCase() + summary.highestSeverity.slice(1)}
              </span>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm font-medium text-gray-500">OpenAI Moderation</div>
            <div className="text-lg font-semibold">
              {summary.openaiTriggered ? (
                <span className="text-orange-600">Flagged</span>
              ) : (
                <span className="text-green-600">Clear</span>
              )}
            </div>
          </div>
        </div>

        {summary.requiresEscalation && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="ml-2 text-sm font-medium text-red-800">
                Requires Escalation: {summary.blockingViolations} blocking, {summary.warningViolations} warning violations
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Controls Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
          {/* Sort Controls */}
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Sort by:</span>
            {(['severity', 'confidence', 'timestamp', 'category'] as const).map((field) => (
              <button
                key={field}
                onClick={() => handleSortChange(field)}
                className={`text-sm px-3 py-1 rounded-md border ${
                  sortOptions.field === field
                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                    : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {field.charAt(0).toUpperCase() + field.slice(1)}
                {sortOptions.field === field && (
                  sortOptions.direction === 'desc' ?
                    <ChevronDownIcon className="w-4 h-4 ml-1 inline" /> :
                    <ChevronUpIcon className="w-4 h-4 ml-1 inline" />
                )}
              </button>
            ))}
          </div>

          {/* Rule Count */}
          <div className="text-sm text-gray-500">
            Showing {filteredRules.length} of {triggeredRules.length} rules
          </div>
        </div>
      </div>

      {/* Rules Display */}
      <div className="space-y-3">
        {Object.entries(groupedRules).map(([groupName, rules]) => (
          <div key={groupName} className="space-y-2">
            {groupBy !== 'none' && (
              <h4 className="text-sm font-medium text-gray-700 px-1">
                {groupName} ({rules.length})
              </h4>
            )}

            {rules.map((rule) => (
              <CollapsibleRuleCard
                key={rule.ruleId}
                rule={rule}
                isExpanded={expandedRules.has(rule.ruleId)}
                onToggle={() => handleRuleToggle(rule.ruleId)}
                showDetails={true}
                showContext={true}
              />
            ))}
          </div>
        ))}
      </div>

      {/* Analytics Section (if enabled) */}
      {showAnalytics && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-lg font-medium text-gray-900 mb-3">
            Rule Analytics
          </h4>
          <div className="text-sm text-gray-500">
            Rule effectiveness analytics would be displayed here based on User Story 3 implementation.
          </div>
        </div>
      )}
    </div>
  );
};

export default TriggeredRulesDisplay;