/**
 * Safety Management Page for CMZ Chatbots admin interface.
 *
 * This page provides a comprehensive safety management dashboard including:
 * - Real-time safety system status monitoring
 * - Safety analytics and metrics visualization
 * - Content validation testing interface
 * - Guardrails configuration management
 * - Live safety feed with recent validations
 */

import React, { useState, useEffect } from 'react';
import { GuardrailsService, SafetyMetrics, SafetyTrends, RuleEffectivenessAnalysis } from '../services/GuardrailsService';
import SafetyStatusComponent from '../components/safety/SafetyStatus';
import ContentFilterIndicator, { useContentFilter } from '../components/safety/ContentFilter';
import TriggeredRulesDisplay from '../components/safety/TriggeredRulesDisplay';
import { DetailedValidationResponse } from '../types/GuardrailTypes';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'stable';
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'gray';
}

const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  color = 'blue'
}) => {
  const getColorClasses = (color: string) => {
    switch (color) {
      case 'green': return 'bg-green-50 border-green-200 text-green-800';
      case 'yellow': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'red': return 'bg-red-50 border-red-200 text-red-800';
      case 'gray': return 'bg-gray-50 border-gray-200 text-gray-800';
      default: return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      case 'stable': return '➡️';
      default: return '';
    }
  };

  return (
    <div className={`p-4 rounded-lg border ${getColorClasses(color)}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">{title}</h3>
        {trend && <span className="text-lg">{getTrendIcon(trend)}</span>}
      </div>
      <div className="mt-2">
        <p className="text-2xl font-bold">{value}</p>
        {subtitle && (
          <p className="text-sm opacity-80 mt-1">{subtitle}</p>
        )}
      </div>
    </div>
  );
};

const SafetyManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'testing' | 'config'>('overview');
  const [safetyMetrics, setSafetyMetrics] = useState<SafetyMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Animal selection for testing interface
  const [selectedAnimalId, setSelectedAnimalId] = useState<string>('lion_leo');

  // Test animals for validation context
  const testAnimals = [
    { id: 'lion_leo', name: 'Leo the Lion', emoji: '🦁', description: 'Apex predator safety rules' },
    { id: 'elephant_ella', name: 'Ella the Elephant', emoji: '🐘', description: 'Large mammal safety guidelines' },
    { id: 'penguin_penny', name: 'Penny the Penguin', emoji: '🐧', description: 'Arctic animal education focus' },
    { id: 'butterfly_bella', name: 'Bella the Butterfly', emoji: '🦋', description: 'Gentle creature, age-appropriate content' },
    { id: 'tiger_tony', name: 'Tony the Tiger', emoji: '🐅', description: 'Endangered species conservation focus' },
    { id: 'monkey_max', name: 'Max the Monkey', emoji: '🐒', description: 'Primate behavior and feeding safety' }
  ];

  // Configuration tab state - moved outside render function to fix React Hooks error
  const [guardrails, setGuardrails] = useState([
    {
      id: 'rule-1',
      rule: 'Never provide personal information about zoo staff or visitors',
      type: 'NEVER' as const,
      priority: 1,
      isActive: true,
      category: 'Privacy',
      severity: 'critical' as const,
      description: 'Protects privacy of zoo personnel and visitors',
      examples: ['Staff home addresses', 'Visitor contact information']
    },
    {
      id: 'rule-2',
      rule: 'Always encourage learning about animal conservation',
      type: 'ALWAYS' as const,
      priority: 2,
      isActive: true,
      category: 'Education',
      severity: 'high' as const,
      description: 'Promotes educational mission',
      examples: ['Conservation success stories', 'How to help endangered species']
    },
    {
      id: 'rule-3',
      rule: 'Discourage feeding animals inappropriate foods',
      type: 'DISCOURAGE' as const,
      priority: 3,
      isActive: true,
      category: 'Safety',
      severity: 'high' as const,
      description: 'Prevents animal health issues',
      examples: ['Human food to animals', 'Chocolate to any animal']
    },
    {
      id: 'rule-4',
      rule: 'Encourage respectful questions about animal behavior',
      type: 'ENCOURAGE' as const,
      priority: 4,
      isActive: false,
      category: 'Education',
      severity: 'medium' as const,
      description: 'Fosters curiosity about animal behavior',
      examples: ['Why do animals sleep patterns differ?', 'How do animals communicate?']
    }
  ]);

  const [showAddForm, setShowAddForm] = useState(false);
  const [newRule, setNewRule] = useState({
    rule: '',
    type: 'NEVER' as const,
    category: 'General',
    severity: 'medium' as const,
    description: '',
    examples: ['']
  });

  // Editing state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingRule, setEditingRule] = useState({
    rule: '',
    type: 'NEVER' as const,
    category: 'General',
    severity: 'medium' as const
  });

  // Manual content testing state (no auto-debouncing)
  const [testContent, setTestContent] = useState('');
  const [validationResult, setValidationResult] = useState<any>(null);
  const [isValidating, setIsValidating] = useState(false);

  const guardrailsService = new GuardrailsService();

  // Manual validation function
  const handleValidateContent = async () => {
    if (!testContent.trim()) {
      alert('Please enter some content to test');
      return;
    }

    setIsValidating(true);
    setValidationResult(null);

    try {
      const result = await guardrailsService.validateContent({
        content: testContent,
        context: {
          userId: 'admin_test',
          conversationId: 'safety_test',
          animalId: selectedAnimalId
        }
      });

      setValidationResult(result);
    } catch (error) {
      console.error('Validation failed:', error);
      alert('Failed to validate content. Please check the backend is running.');
    } finally {
      setIsValidating(false);
    }
  };

  useEffect(() => {
    const loadSafetyData = async () => {
      try {
        setError(null);
        const metrics = await guardrailsService.getSafetyMetrics('24h');
        setSafetyMetrics(metrics);
      } catch (err) {
        console.error('Failed to load safety data:', err);
        setError('Unable to load safety metrics');
      } finally {
        setLoading(false);
      }
    };

    loadSafetyData();
  }, []);

  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Safety System Status */}
      <SafetyStatusComponent
        className="mb-6"
        showDetailedMetrics={true}
        refreshInterval={60000}
      />

      {/* Key Metrics Grid */}
      {safetyMetrics && (
        <div>
          <h3 className="text-lg font-semibold mb-4">📊 24-Hour Safety Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricsCard
              title="Content Validations"
              value={formatNumber(safetyMetrics.totalValidations)}
              subtitle="Total processed"
              color="blue"
              trend="up"
            />
            <MetricsCard
              title="Flagged Content"
              value={formatPercentage(safetyMetrics.flaggedContentRate)}
              subtitle={`${safetyMetrics.totalFlagged} total`}
              color={safetyMetrics.flaggedContentRate > 0.1 ? 'yellow' : 'green'}
              trend={safetyMetrics.flaggedContentRate > 0.05 ? 'up' : 'stable'}
            />
            <MetricsCard
              title="Blocked Content"
              value={formatPercentage(safetyMetrics.blockedContentRate)}
              subtitle={`${safetyMetrics.totalBlocked} total`}
              color={safetyMetrics.blockedContentRate > 0.05 ? 'red' : 'green'}
              trend={safetyMetrics.blockedContentRate > 0.02 ? 'up' : 'stable'}
            />
            <MetricsCard
              title="Average Response"
              value={`${safetyMetrics.avgProcessingTimeMs}ms`}
              subtitle="Processing time"
              color={safetyMetrics.avgProcessingTimeMs > 2000 ? 'yellow' : 'green'}
              trend={safetyMetrics.avgProcessingTimeMs > 1500 ? 'up' : 'stable'}
            />
          </div>
        </div>
      )}

      {/* User Activity Summary */}
      {safetyMetrics && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">👥 User Activity</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{formatNumber(safetyMetrics.uniqueUsers)}</div>
              <div className="text-sm text-gray-600">Unique Users</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{formatNumber(safetyMetrics.uniqueConversations)}</div>
              <div className="text-sm text-gray-600">Conversations</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{safetyMetrics.totalEscalations}</div>
              <div className="text-sm text-gray-600">Escalations</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">📈 Safety Analytics</h3>
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">🚧</div>
          <p>Advanced analytics charts coming soon!</p>
          <p className="text-sm mt-2">
            This will include trend analysis, rule effectiveness charts, and safety pattern recognition.
          </p>
        </div>
      </div>
    </div>
  );

  const renderTestingTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">🧪 Content Safety Testing</h3>
        <p className="text-gray-600 mb-4">
          Test content against the safety system to see how it would be processed.
        </p>

        <div className="space-y-4">
          {/* Animal Selection */}
          <div>
            <label htmlFor="animalSelect" className="block text-sm font-medium text-gray-700 mb-2">
              Select Animal Context:
            </label>
            <select
              id="animalSelect"
              value={selectedAnimalId}
              onChange={(e) => setSelectedAnimalId(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              {testAnimals.map((animal) => (
                <option key={animal.id} value={animal.id}>
                  {animal.emoji} {animal.name} - {animal.description}
                </option>
              ))}
            </select>
            <p className="text-sm text-gray-600 mt-1">
              Different animals have different safety rules and educational contexts.
              This simulates how content validation adapts to specific animal personalities.
            </p>
          </div>

          {/* Test Input */}
          <div>
            <label htmlFor="testContent" className="block text-sm font-medium text-gray-700 mb-2">
              Test Content:
            </label>
            <textarea
              id="testContent"
              value={testContent}
              onChange={(e) => setTestContent(e.target.value)}
              placeholder="Enter content to test against safety filters..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
            <button
              onClick={handleValidateContent}
              disabled={isValidating || !testContent.trim()}
              className="mt-3 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isValidating ? 'Validating...' : 'Test Content'}
            </button>
          </div>

          {/* Validation Results */}
          {validationResult && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Validation Results:</h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <span className="font-medium">Result:</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    validationResult.result === 'approved' ? 'bg-green-100 text-green-800' :
                    validationResult.result === 'flagged' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {validationResult.result?.toUpperCase()}
                  </span>
                </div>
                {validationResult.riskScore !== undefined && (
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">Risk Score:</span>
                    <span>{(validationResult.riskScore * 100).toFixed(1)}%</span>
                  </div>
                )}
                {validationResult.userMessage && (
                  <div className="flex items-start space-x-2">
                    <span className="font-medium">Message:</span>
                    <span className="text-gray-700">{validationResult.userMessage}</span>
                  </div>
                )}
                {validationResult.processingTimeMs && (
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">Processing Time:</span>
                    <span className="text-gray-600">{validationResult.processingTimeMs}ms</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Enhanced Validation Details */}
          {validationResult && (
            <div className="space-y-6">
              {/* Animal Context Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium mb-2 text-blue-800">
                  🐾 Validation Context: {testAnimals.find(a => a.id === selectedAnimalId)?.emoji} {testAnimals.find(a => a.id === selectedAnimalId)?.name}
                </h4>
                <p className="text-sm text-blue-700">
                  Testing with {testAnimals.find(a => a.id === selectedAnimalId)?.description.toLowerCase()}
                </p>
              </div>

              {/* Basic Validation Summary */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium mb-2">🔍 Validation Summary:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <strong>Result:</strong> <span className={`px-2 py-1 rounded text-xs ${
                      validationResult.result === 'approved' ? 'bg-green-100 text-green-800' :
                      validationResult.result === 'flagged' ? 'bg-yellow-100 text-yellow-800' :
                      validationResult.result === 'blocked' ? 'bg-red-100 text-red-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>{validationResult.result.toUpperCase()}</span>
                  </div>
                  <div><strong>Risk Score:</strong> {validationResult.riskScore.toFixed(3)}</div>
                  <div><strong>Processing Time:</strong> {validationResult.processingTimeMs}ms</div>
                  <div><strong>Validation ID:</strong> {validationResult.validationId}</div>
                </div>
                {validationResult.userMessage && (
                  <div className="mt-3">
                    <strong>User Message:</strong>
                    <div className="bg-blue-50 p-2 rounded mt-1 text-blue-800">
                      {validationResult.userMessage}
                    </div>
                  </div>
                )}
                {validationResult.safeAlternative && (
                  <div className="mt-3">
                    <strong>Safe Alternative:</strong>
                    <div className="bg-green-50 p-2 rounded mt-1 text-green-800">
                      {validationResult.safeAlternative}
                    </div>
                  </div>
                )}
              </div>

              {/* Enhanced Triggered Rules Display */}
              {validationResult.triggeredRules && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    🛡️ Detailed Rule Analysis
                    <span className="ml-2 text-sm font-normal text-gray-500">
                      (New Feature - User Story 1)
                    </span>
                  </h4>
                  <TriggeredRulesDisplay
                    validationResult={validationResult as DetailedValidationResponse}
                    sortBy="severity"
                    groupBy="none"
                    showAnalytics={false}
                    onRuleClick={(rule) => {
                      console.log('Rule clicked:', rule);
                      // Future: Could implement rule details modal or navigation
                    }}
                  />
                </div>
              )}
            </div>
          )}

          {/* Quick Test Examples */}
          <div className="border-t pt-4">
            <h4 className="font-medium mb-2">🎯 Quick Test Examples:</h4>
            <p className="text-sm text-gray-600 mb-3">
              Try these examples to see the enhanced detailed rule feedback in action:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <button
                onClick={() => setTestContent("I love lions because they're the king of the jungle!")}
                className="p-3 text-sm bg-green-100 text-green-800 rounded hover:bg-green-200 transition-colors text-left"
              >
                <div className="font-medium">✅ Safe Educational Content</div>
                <div className="text-xs mt-1 opacity-80">Should pass all guardrails cleanly</div>
              </button>
              <button
                onClick={() => setTestContent("Can you tell me about violence and fighting?")}
                className="p-3 text-sm bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200 transition-colors text-left"
              >
                <div className="font-medium">⚠️ Rule-Triggering Content</div>
                <div className="text-xs mt-1 opacity-80">Should trigger violence rules</div>
              </button>
              <button
                onClick={() => setTestContent("How do I hurt animals or cause them harm?")}
                className="p-3 text-sm bg-red-100 text-red-800 rounded hover:bg-red-200 transition-colors text-left"
              >
                <div className="font-medium">🚫 Blocked Content</div>
                <div className="text-xs mt-1 opacity-80">Should trigger high-severity rules</div>
              </button>
              <button
                onClick={() => setTestContent("I want to learn about animal conservation efforts")}
                className="p-3 text-sm bg-blue-100 text-blue-800 rounded hover:bg-blue-200 transition-colors text-left"
              >
                <div className="font-medium">🌟 Encouraged Content</div>
                <div className="text-xs mt-1 opacity-80">Should trigger ENCOURAGE rules</div>
              </button>
              <button
                onClick={() => setTestContent("Can I feed chocolate to the monkeys?")}
                className="p-3 text-sm bg-orange-100 text-orange-800 rounded hover:bg-orange-200 transition-colors text-left"
              >
                <div className="font-medium">🍫 Safety Warning</div>
                <div className="text-xs mt-1 opacity-80">Should trigger animal feeding rules</div>
              </button>
              <button
                onClick={() => setTestContent("What's the personal information of the zookeepers?")}
                className="p-3 text-sm bg-purple-100 text-purple-800 rounded hover:bg-purple-200 transition-colors text-left"
              >
                <div className="font-medium">🔒 Privacy Violation</div>
                <div className="text-xs mt-1 opacity-80">Should trigger privacy rules</div>
              </button>
            </div>

            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <div className="text-blue-500 mr-2">💡</div>
                <div className="text-sm">
                  <div className="font-medium text-blue-800">Enhanced Rule Feedback</div>
                  <div className="text-blue-700 mt-1">
                    Each test now shows detailed information about triggered rules including severity levels,
                    confidence scores, categories, and specific guidance. This helps content administrators
                    understand exactly why content was flagged and how to improve it.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderConfigTab = () => {
    const toggleGuardrail = (id: string) => {
      setGuardrails(prev =>
        prev.map(rule =>
          rule.id === id ? { ...rule, isActive: !rule.isActive } : rule
        )
      );
    };

    const deleteGuardrail = (id: string) => {
      setGuardrails(prev => prev.filter(rule => rule.id !== id));
    };

    const addGuardrail = () => {
      if (!newRule.rule.trim()) return;

      const newId = `rule-${Date.now()}`;
      const rule = {
        id: newId,
        rule: newRule.rule,
        type: newRule.type,
        priority: guardrails.length + 1,
        isActive: true,
        category: newRule.category,
        severity: newRule.severity,
        description: '',
        examples: []
      };

      setGuardrails(prev => [...prev, rule]);
      setNewRule({
        rule: '',
        type: 'NEVER',
        category: 'Safety',
        severity: 'medium'
      });
      setShowAddForm(false);
    };

    const startEditing = (rule: any) => {
      setEditingId(rule.id);
      setEditingRule({
        rule: rule.rule,
        type: rule.type,
        category: rule.category,
        severity: rule.severity
      });
    };

    const saveEdit = () => {
      if (!editingRule.rule.trim()) return;

      setGuardrails(prev =>
        prev.map(rule =>
          rule.id === editingId ? {
            ...rule,
            rule: editingRule.rule,
            type: editingRule.type,
            category: editingRule.category,
            severity: editingRule.severity
          } : rule
        )
      );

      setEditingId(null);
      setEditingRule({
        rule: '',
        type: 'NEVER',
        category: 'General',
        severity: 'medium'
      });
    };

    const cancelEdit = () => {
      setEditingId(null);
      setEditingRule({
        rule: '',
        type: 'NEVER',
        category: 'General',
        severity: 'medium'
      });
    };

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">⚙️ Guardrails Configuration</h3>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center space-x-2"
            >
              <span>➕</span>
              <span>Add New Rule</span>
            </button>
          </div>

          {/* Add New Rule Form */}
          {showAddForm && (
            <div className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
              <h4 className="font-medium mb-3">Create New Guardrail Rule</h4>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rule Text:
                  </label>
                  <textarea
                    value={newRule.rule}
                    onChange={(e) => setNewRule(prev => ({ ...prev, rule: e.target.value }))}
                    placeholder="Enter the guardrail rule (e.g., 'Never discuss inappropriate topics')"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Rule Type:
                    </label>
                    <select
                      value={newRule.type}
                      onChange={(e) => setNewRule(prev => ({ ...prev, type: e.target.value as 'NEVER' | 'ALWAYS' | 'ENCOURAGE' | 'DISCOURAGE' }))}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="NEVER">NEVER - Strictly forbidden</option>
                      <option value="ALWAYS">ALWAYS - Must include</option>
                      <option value="DISCOURAGE">DISCOURAGE - Avoid if possible</option>
                      <option value="ENCOURAGE">ENCOURAGE - Promote this</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Category:
                    </label>
                    <select
                      value={newRule.category}
                      onChange={(e) => setNewRule(prev => ({ ...prev, category: e.target.value }))}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="Safety">Safety</option>
                      <option value="Privacy">Privacy</option>
                      <option value="Education">Education</option>
                      <option value="Content">Content</option>
                      <option value="Behavior">Behavior</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Severity:
                    </label>
                    <select
                      value={newRule.severity}
                      onChange={(e) => setNewRule(prev => ({ ...prev, severity: e.target.value as 'low' | 'medium' | 'high' | 'critical' }))}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={addGuardrail}
                    disabled={!newRule.rule.trim()}
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    ✅ Create Rule
                  </button>
                  <button
                    onClick={() => setShowAddForm(false)}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    ❌ Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Guardrails List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Active Guardrail Rules ({guardrails.filter(r => r.isActive).length}/{guardrails.length})</h4>
              <div className="text-sm text-gray-500">
                Priority determines rule evaluation order
              </div>
            </div>

            {guardrails.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">📝</div>
                <p>No guardrail rules configured yet.</p>
                <p className="text-sm mt-1">Click "Add New Rule" to create your first guardrail.</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                {guardrails.map((rule, index) => (
                  editingId === rule.id ? (
                    // Edit Mode
                    <div key={rule.id} className="p-4 border-2 border-blue-200 rounded-lg bg-blue-50">
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Rule Text:
                          </label>
                          <textarea
                            value={editingRule.rule}
                            onChange={(e) => setEditingRule(prev => ({ ...prev, rule: e.target.value }))}
                            className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            rows={2}
                            placeholder="Enter the guardrail rule..."
                          />
                        </div>
                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Type:
                            </label>
                            <select
                              value={editingRule.type}
                              onChange={(e) => setEditingRule(prev => ({ ...prev, type: e.target.value as any }))}
                              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="NEVER">NEVER - Strictly forbidden</option>
                              <option value="ALWAYS">ALWAYS - Must include</option>
                              <option value="DISCOURAGE">DISCOURAGE - Avoid if possible</option>
                              <option value="ENCOURAGE">ENCOURAGE - Promote this</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Category:
                            </label>
                            <select
                              value={editingRule.category}
                              onChange={(e) => setEditingRule(prev => ({ ...prev, category: e.target.value }))}
                              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="Safety">Safety</option>
                              <option value="Privacy">Privacy</option>
                              <option value="Education">Education</option>
                              <option value="Content">Content</option>
                              <option value="Behavior">Behavior</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Severity:
                            </label>
                            <select
                              value={editingRule.severity}
                              onChange={(e) => setEditingRule(prev => ({ ...prev, severity: e.target.value as any }))}
                              className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="critical">Critical</option>
                              <option value="high">High</option>
                              <option value="medium">Medium</option>
                              <option value="low">Low</option>
                            </select>
                          </div>
                        </div>
                        <div className="flex space-x-3">
                          <button
                            onClick={saveEdit}
                            disabled={!editingRule.rule.trim()}
                            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                          >
                            ✅ Save Changes
                          </button>
                          <button
                            onClick={cancelEdit}
                            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                          >
                            ❌ Cancel
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    // Display Mode
                    <div
                      key={rule.id}
                      className={`p-4 border rounded-lg transition-all ${
                        rule.isActive
                          ? 'border-gray-200 bg-white'
                          : 'border-gray-100 bg-gray-50 opacity-60'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className="text-sm font-medium text-gray-500">#{rule.priority}</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold border ${
                              rule.type === 'NEVER' ? 'bg-red-100 text-red-800' :
                              rule.type === 'ALWAYS' ? 'bg-green-100 text-green-800' :
                              rule.type === 'ENCOURAGE' ? 'bg-blue-100 text-blue-800' :
                              rule.type === 'DISCOURAGE' ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-800'
                            }`}>
                              {rule.type}
                            </span>
                            <span className="text-xs text-gray-500">{rule.category}</span>
                            <div className={`w-3 h-3 rounded-full ${
                              rule.severity === 'critical' ? 'bg-red-500' :
                              rule.severity === 'high' ? 'bg-orange-500' :
                              rule.severity === 'medium' ? 'bg-yellow-500' :
                              rule.severity === 'low' ? 'bg-green-500' : 'bg-gray-500'
                            }`} title={`${rule.severity} severity`}></div>
                          </div>
                          <p className={`text-sm ${rule.isActive ? 'text-gray-900' : 'text-gray-500'}`}>
                            {rule.rule}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <label className="flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={rule.isActive}
                              onChange={() => toggleGuardrail(rule.id)}
                              className="sr-only"
                            />
                            <div className={`relative w-11 h-6 rounded-full transition-colors ${
                              rule.isActive ? 'bg-green-500' : 'bg-gray-300'
                            }`}>
                              <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                                rule.isActive ? 'translate-x-5' : 'translate-x-0'
                              }`}></div>
                            </div>
                            <span className="ml-2 text-sm text-gray-600">
                              {rule.isActive ? 'Enabled' : 'Disabled'}
                            </span>
                          </label>
                          <button
                            onClick={() => startEditing(rule)}
                            className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Edit this rule"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => deleteGuardrail(rule.id)}
                            className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete this rule"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    </div>
                  )
                ))}
              </div>
            )}
          </div>

          {/* Summary Stats */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">{guardrails.length}</div>
                <div className="text-sm text-gray-600">Total Rules</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{guardrails.filter(r => r.isActive).length}</div>
                <div className="text-sm text-gray-600">Active Rules</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">{guardrails.filter(r => r.severity === 'critical').length}</div>
                <div className="text-sm text-gray-600">Critical Rules</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">{new Set(guardrails.map(r => r.category)).size}</div>
                <div className="text-sm text-gray-600">Categories</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
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
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <span className="mr-3">🛡️</span>
            Safety Management
          </h1>
          <p className="text-gray-600 mt-1">
            Monitor and manage the content safety system
          </p>
        </div>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="text-red-400 mr-2">⚠️</div>
            <div>
              <h3 className="text-sm font-medium text-red-800">Error Loading Safety Data</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'analytics', label: 'Analytics', icon: '📈' },
            { id: 'testing', label: 'Testing', icon: '🧪' },
            { id: 'config', label: 'Configuration', icon: '⚙️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'analytics' && renderAnalyticsTab()}
        {activeTab === 'testing' && renderTestingTab()}
        {activeTab === 'config' && renderConfigTab()}
      </div>
    </div>
  );
};

export default SafetyManagement;