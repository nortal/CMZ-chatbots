/**
 * Content Filter Indicator Component for CMZ Chatbots user interface.
 *
 * This component provides real-time feedback to users about content safety,
 * including:
 * - Live content validation as users type
 * - Safety level indicators (safe, warning, danger)
 * - Educational messaging for inappropriate content
 * - Safe alternative suggestions
 * - Child-friendly error handling
 */

import React, { useState, useEffect, useRef } from 'react';
import { GuardrailsService, ContentValidationResponse } from '../../services/GuardrailsService';

interface ContentFilterProps {
  content: string;
  userId?: string;
  conversationId?: string;
  animalId?: string;
  onValidationResult?: (result: ContentValidationResponse) => void;
  onSafeAlternative?: (safeContent: string) => void;
  debounceMs?: number;
  showLiveIndicator?: boolean;
  className?: string;
}

interface SafetyIndicatorProps {
  level: 'safe' | 'warning' | 'danger' | 'checking';
  message: string;
  showIcon?: boolean;
}

const SafetyIndicator: React.FC<SafetyIndicatorProps> = ({
  level,
  message,
  showIcon = true
}) => {
  const getIndicatorStyle = (level: string) => {
    switch (level) {
      case 'safe':
        return {
          backgroundColor: '#D1FAE5', // green-100
          borderColor: '#10B981', // green-500
          textColor: '#065F46', // green-800
          icon: '✅'
        };
      case 'warning':
        return {
          backgroundColor: '#FEF3C7', // yellow-100
          borderColor: '#F59E0B', // yellow-500
          textColor: '#92400E', // yellow-800
          icon: '⚠️'
        };
      case 'danger':
        return {
          backgroundColor: '#FEE2E2', // red-100
          borderColor: '#EF4444', // red-500
          textColor: '#991B1B', // red-800
          icon: '🚫'
        };
      case 'checking':
        return {
          backgroundColor: '#F3F4F6', // gray-100
          borderColor: '#9CA3AF', // gray-400
          textColor: '#374151', // gray-700
          icon: '🔍'
        };
      default:
        return {
          backgroundColor: '#F3F4F6',
          borderColor: '#9CA3AF',
          textColor: '#374151',
          icon: '❓'
        };
    }
  };

  const style = getIndicatorStyle(level);

  return (
    <div
      className="px-3 py-2 rounded-lg border text-sm flex items-center space-x-2"
      style={{
        backgroundColor: style.backgroundColor,
        borderColor: style.borderColor,
        color: style.textColor
      }}
    >
      {showIcon && <span>{style.icon}</span>}
      <span>{message}</span>
    </div>
  );
};

const ContentFilterIndicator: React.FC<ContentFilterProps> = ({
  content,
  userId,
  conversationId,
  animalId,
  onValidationResult,
  onSafeAlternative,
  debounceMs = 1000,
  showLiveIndicator = true,
  className = ''
}) => {
  const [validationResult, setValidationResult] = useState<ContentValidationResponse | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [safetyLevel, setSafetyLevel] = useState<'safe' | 'warning' | 'danger' | 'checking'>('safe');
  const [message, setMessage] = useState('');
  const [showSafeAlternative, setShowSafeAlternative] = useState(false);
  const [hasError, setHasError] = useState(false);

  const guardrailsService = new GuardrailsService();
  const debounceRef = useRef<NodeJS.Timeout>();
  const lastValidatedContent = useRef<string>('');

  const validateContent = async (contentToValidate: string) => {
    if (!contentToValidate || contentToValidate.trim().length === 0) {
      setSafetyLevel('safe');
      setMessage('');
      setValidationResult(null);
      return;
    }

    // Skip validation if content hasn't changed significantly
    if (contentToValidate === lastValidatedContent.current) {
      return;
    }

    // Skip validation for very short content
    if (!guardrailsService.shouldValidateContent(contentToValidate)) {
      setSafetyLevel('safe');
      setMessage('');
      setValidationResult(null);
      return;
    }

    try {
      setIsValidating(true);
      setHasError(false);
      setSafetyLevel('checking');
      setMessage('Checking content safety...');

      const result = await guardrailsService.validateContent({
        content: contentToValidate,
        context: {
          userId,
          conversationId,
          animalId
        }
      });

      lastValidatedContent.current = contentToValidate;
      setValidationResult(result);

      // Determine safety level and message
      const indicator = guardrailsService.getSafetyLevelIndicator(result.riskScore);
      setSafetyLevel(indicator.level);

      // Use custom message from backend or generate appropriate message
      const displayMessage = guardrailsService.formatSafetyMessage(result);
      setMessage(displayMessage || indicator.message);

      // Show safe alternative if available
      setShowSafeAlternative(!!result.safeAlternative);

      // Notify parent component
      if (onValidationResult) {
        onValidationResult(result);
      }

    } catch (error) {
      console.error('Content validation failed:', error);
      setHasError(true);
      setSafetyLevel('warning');
      setMessage('We\'re having trouble checking your message right now. Please try again.');
      setValidationResult(null);
    } finally {
      setIsValidating(false);
    }
  };

  // Debounced validation effect
  useEffect(() => {
    // Skip validation if we're already validating, content is too short, or there's an ongoing error
    if (isValidating || !content || content.trim().length === 0 || hasError) {
      return;
    }

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      validateContent(content);
    }, debounceMs);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [content, userId, conversationId, animalId, isValidating, hasError]);

  const handleUseSafeAlternative = () => {
    if (validationResult?.safeAlternative && onSafeAlternative) {
      onSafeAlternative(validationResult.safeAlternative);
      setShowSafeAlternative(false);
    }
  };

  // Don't show indicator for empty content or if disabled
  if (!showLiveIndicator || !content || content.trim().length === 0) {
    return null;
  }

  // Don't show indicator for safe content with no message
  if (safetyLevel === 'safe' && !message) {
    return null;
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Main Safety Indicator */}
      <SafetyIndicator
        level={isValidating ? 'checking' : safetyLevel}
        message={message || 'Content looks good!'}
        showIcon={true}
      />

      {/* Safe Alternative Option */}
      {showSafeAlternative && validationResult?.safeAlternative && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <span className="text-blue-500 mt-0.5">💡</span>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-blue-800 mb-1">
                Try this instead:
              </h4>
              <p className="text-sm text-blue-700 mb-2">
                "{validationResult.safeAlternative}"
              </p>
              <button
                onClick={handleUseSafeAlternative}
                className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors"
              >
                Use This Version
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Educational Guidance for Blocked Content */}
      {safetyLevel === 'danger' && validationResult?.result === 'blocked' && (
        <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <span className="text-purple-500 mt-0.5">🎓</span>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-purple-800 mb-1">
                Let's learn about animals instead!
              </h4>
              <p className="text-sm text-purple-700">
                What would you like to know about your favorite animal?
                I can tell you about their habitats, behaviors, or conservation efforts!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Escalation Notice */}
      {validationResult?.requiresEscalation && (
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <span className="text-yellow-500 mt-0.5">👋</span>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-yellow-800 mb-1">
                Getting Help
              </h4>
              <p className="text-sm text-yellow-700">
                A zookeeper will help answer your question to make sure
                you get the best and safest information!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Debug Info (for development) */}
      {process.env.NODE_ENV === 'development' && validationResult && (
        <details className="text-xs text-gray-500">
          <summary className="cursor-pointer">Debug Info</summary>
          <pre className="mt-1 p-2 bg-gray-100 rounded overflow-auto">
            {JSON.stringify({
              result: validationResult.result,
              riskScore: validationResult.riskScore,
              processingTime: validationResult.processingTimeMs,
              validationId: validationResult.validationId
            }, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
};

// Companion hook for easy integration with form inputs
export const useContentFilter = (
  initialContent: string = '',
  options: {
    userId?: string;
    conversationId?: string;
    animalId?: string;
    debounceMs?: number;
  } = {}
) => {
  const [content, setContent] = useState(initialContent);
  const [validationResult, setValidationResult] = useState<ContentValidationResponse | null>(null);
  const [isSafe, setIsSafe] = useState(true);

  const handleValidationResult = (result: ContentValidationResponse) => {
    setValidationResult(result);
    setIsSafe(result.valid && result.result !== 'blocked');
  };

  const handleSafeAlternative = (safeContent: string) => {
    setContent(safeContent);
  };

  return {
    content,
    setContent,
    validationResult,
    isSafe,
    ContentFilterComponent: () => (
      <ContentFilterIndicator
        content={content}
        userId={options.userId}
        conversationId={options.conversationId}
        animalId={options.animalId}
        onValidationResult={handleValidationResult}
        onSafeAlternative={handleSafeAlternative}
        debounceMs={options.debounceMs}
      />
    )
  };
};

export default ContentFilterIndicator;