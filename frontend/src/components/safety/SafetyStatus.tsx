/**
 * Safety Status Component for CMZ Chatbots admin dashboard.
 *
 * This component displays real-time safety system status, including:
 * - Overall system health
 * - Individual service status (OpenAI, Guardrails, Analytics)
 * - Recent activity metrics
 * - Performance indicators
 * - Quick access to safety analytics
 */

import React, { useState, useEffect } from 'react';
import { GuardrailsService, SafetyStatus, SafetyMetrics } from '../../services/GuardrailsService';

interface SafetyStatusProps {
  className?: string;
  refreshInterval?: number; // in milliseconds, default 30 seconds
  showDetailedMetrics?: boolean;
}

interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'degraded';
  label: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, label }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#10B981'; // green
      case 'degraded': return '#F59E0B'; // yellow
      case 'offline': return '#EF4444'; // red
      default: return '#6B7280'; // gray
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return '✅';
      case 'degraded': return '⚠️';
      case 'offline': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <span className="text-lg">{getStatusIcon(status)}</span>
      <span className="font-medium">{label}</span>
      <span
        className="px-2 py-1 rounded-full text-xs font-semibold text-white"
        style={{ backgroundColor: getStatusColor(status) }}
      >
        {status.toUpperCase()}
      </span>
    </div>
  );
};

const SafetyStatusComponent: React.FC<SafetyStatusProps> = ({
  className = '',
  refreshInterval = 30000,
  showDetailedMetrics = false
}) => {
  const [safetyStatus, setSafetyStatus] = useState<SafetyStatus | null>(null);
  const [safetyMetrics, setSafetyMetrics] = useState<SafetyMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const guardrailsService = new GuardrailsService();

  const fetchSafetyData = async () => {
    try {
      setError(null);

      const [statusResult, metricsResult] = await Promise.allSettled([
        guardrailsService.getSafetyStatus(),
        showDetailedMetrics ? guardrailsService.getSafetyMetrics('1h') : Promise.resolve(null)
      ]);

      if (statusResult.status === 'fulfilled') {
        setSafetyStatus(statusResult.value);
      } else {
        console.error('Failed to fetch safety status:', statusResult.reason);
        setError('Unable to load safety status');
      }

      if (metricsResult.status === 'fulfilled' && metricsResult.value) {
        setSafetyMetrics(metricsResult.value);
      }

      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching safety data:', err);
      setError('Failed to load safety information');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSafetyData();

    const interval = setInterval(fetchSafetyData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval, showDetailedMetrics]);

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#10B981'; // green
      case 'degraded': return '#F59E0B'; // yellow
      case 'critical': return '#EF4444'; // red
      case 'offline': return '#6B7280'; // gray
      default: return '#6B7280';
    }
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '💚';
      case 'degraded': return '💛';
      case 'critical': return '❤️';
      case 'offline': return '💔';
      default: return '❓';
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatResponseTime = (ms: number): string => {
    if (ms >= 1000) {
      return (ms / 1000).toFixed(1) + 's';
    }
    return Math.round(ms) + 'ms';
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !safetyStatus) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="text-center">
          <div className="text-red-500 text-4xl mb-2">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Safety System Unavailable
          </h3>
          <p className="text-gray-600 mb-4">
            {error || 'Unable to connect to safety services'}
          </p>
          <button
            onClick={fetchSafetyData}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 flex items-center">
          <span className="mr-2">🛡️</span>
          Safety System Status
        </h2>
        <div className="text-sm text-gray-500">
          {lastUpdated && `Updated ${lastUpdated.toLocaleTimeString()}`}
        </div>
      </div>

      {/* Overall Health Status */}
      <div className="mb-6">
        <div className="flex items-center space-x-3 mb-2">
          <span className="text-2xl">{getHealthStatusIcon(safetyStatus.healthStatus)}</span>
          <div>
            <h3 className="text-lg font-semibold">Overall Health</h3>
            <span
              className="px-3 py-1 rounded-full text-sm font-semibold text-white"
              style={{ backgroundColor: getHealthStatusColor(safetyStatus.healthStatus) }}
            >
              {safetyStatus.healthStatus.toUpperCase()}
            </span>
          </div>
        </div>
        {!safetyStatus.isEnabled && (
          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-yellow-800 text-sm">
              ⚠️ Safety system is currently disabled
            </p>
          </div>
        )}
      </div>

      {/* Service Status */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">Service Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-3 border border-gray-200 rounded-lg">
            <StatusIndicator status={safetyStatus.services.openai} label="OpenAI Moderation" />
          </div>
          <div className="p-3 border border-gray-200 rounded-lg">
            <StatusIndicator status={safetyStatus.services.guardrails} label="Custom Guardrails" />
          </div>
          <div className="p-3 border border-gray-200 rounded-lg">
            <StatusIndicator status={safetyStatus.services.analytics} label="Analytics" />
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">Recent Activity (Last Hour)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {formatNumber(safetyStatus.recentActivity.validationsLastHour)}
            </div>
            <div className="text-sm text-blue-800">Content Validations</div>
          </div>
          <div className="text-center p-3 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {formatNumber(safetyStatus.recentActivity.flaggedLastHour)}
            </div>
            <div className="text-sm text-yellow-800">Content Flagged</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {formatResponseTime(safetyStatus.recentActivity.avgResponseTime)}
            </div>
            <div className="text-sm text-green-800">Avg Response Time</div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics (if enabled) */}
      {showDetailedMetrics && safetyMetrics && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">Detailed Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 border border-gray-200 rounded-lg">
              <div className="text-xl font-bold text-gray-900">
                {(safetyMetrics.flaggedContentRate * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Flagged Rate</div>
            </div>
            <div className="text-center p-3 border border-gray-200 rounded-lg">
              <div className="text-xl font-bold text-gray-900">
                {(safetyMetrics.blockedContentRate * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Blocked Rate</div>
            </div>
            <div className="text-center p-3 border border-gray-200 rounded-lg">
              <div className="text-xl font-bold text-gray-900">
                {(safetyMetrics.escalationRate * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Escalation Rate</div>
            </div>
            <div className="text-center p-3 border border-gray-200 rounded-lg">
              <div className="text-xl font-bold text-gray-900">
                {formatNumber(safetyMetrics.uniqueUsers)}
              </div>
              <div className="text-sm text-gray-600">Unique Users</div>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={fetchSafetyData}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          🔄 Refresh
        </button>
        <button
          onClick={() => window.open('/admin/safety-analytics', '_blank')}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
        >
          📊 View Analytics
        </button>
        <button
          onClick={() => window.open('/admin/guardrails-config', '_blank')}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors"
        >
          ⚙️ Configure Rules
        </button>
      </div>

      {/* Footer Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            Last system check: {new Date(safetyStatus.lastCheck).toLocaleString()}
          </span>
          <span className={`flex items-center ${safetyStatus.isEnabled ? 'text-green-600' : 'text-red-600'}`}>
            <span className="w-2 h-2 rounded-full mr-2" style={{
              backgroundColor: safetyStatus.isEnabled ? '#10B981' : '#EF4444'
            }}></span>
            Safety {safetyStatus.isEnabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SafetyStatusComponent;