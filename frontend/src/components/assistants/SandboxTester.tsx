/**
 * SandboxTester Component
 *
 * Provides a chat interface for testing sandbox assistant configurations
 * before promoting them to live environments.
 *
 * Features:
 * - Real-time chat testing with sandbox assistant
 * - TTL countdown display and expiration warnings
 * - Sandbox status management (draft -> tested -> promoted)
 * - Conversation history and metrics
 * - Promotion controls for tested configurations
 *
 * T045 - User Story 2: Test Assistant Changes Safely
 */

import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Send, Clock, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { SandboxService, SandboxResponse, ChatRequest, ChatResponse } from '@/services/SandboxService';

interface SandboxTesterProps {
  sandbox: SandboxResponse;
  onBack: () => void;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const SandboxTester: React.FC<SandboxTesterProps> = ({ sandbox, onBack }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [ttlProgress, setTTLProgress] = useState<number>(0);
  const [isExpired, setIsExpired] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Update countdown timer
  useEffect(() => {
    const updateTimer = () => {
      const remaining = SandboxService.getTimeRemaining(sandbox.expiresAt);
      const progress = SandboxService.getTTLProgress(sandbox.expiresAt);

      setTimeRemaining(remaining);
      setTTLProgress(progress);
      setIsExpired(remaining === 0);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [sandbox.expiresAt]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatTimeRemaining = (milliseconds: number): string => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || isExpired) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError('');

    try {
      const chatRequest: ChatRequest = {
        message: userMessage.content,
        context: {
          sessionId: sandbox.sandboxId,
          userId: 'sandbox-tester'
        }
      };

      const response: ChatResponse = await SandboxService.testSandboxChat(sandbox.sandboxId, chatRequest);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromoteSandbox = async () => {
    try {
      await SandboxService.promoteSandbox(sandbox.sandboxId);
      // Show success message or navigate back
      alert('Sandbox promoted to live assistant successfully!');
      onBack();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to promote sandbox');
    }
  };

  const getStatusInfo = () => {
    const status = SandboxService.getSandboxStatus(sandbox);
    switch (status) {
      case 'draft':
        return { icon: Clock, color: 'text-gray-500', label: 'Draft - Not Tested' };
      case 'tested':
        return { icon: CheckCircle, color: 'text-green-500', label: 'Tested - Ready for Promotion' };
      case 'expired':
        return { icon: AlertCircle, color: 'text-red-500', label: 'Expired' };
      default:
        return { icon: Clock, color: 'text-gray-500', label: 'Unknown' };
    }
  };

  const statusInfo = getStatusInfo();
  const StatusIcon = statusInfo.icon;
  const hasMessages = messages.length > 0;
  const canPromote = hasMessages && !sandbox.isPromoted && !isExpired;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Sandbox List
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {sandbox.animalId ? `${sandbox.animalId} Sandbox` : 'New Assistant Sandbox'}
            </h1>
            <div className="flex items-center space-x-2 mt-1">
              <StatusIcon className={`h-4 w-4 ${statusInfo.color}`} />
              <span className="text-sm text-gray-600">{statusInfo.label}</span>
            </div>
          </div>
        </div>

        {canPromote && (
          <Button onClick={handlePromoteSandbox} className="bg-green-600 hover:bg-green-700">
            <TrendingUp className="h-4 w-4 mr-2" />
            Promote to Live
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <CardHeader className="flex-shrink-0">
              <CardTitle>Test Conversation</CardTitle>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
                  {error}
                </div>
              )}
            </CardHeader>

            <CardContent className="flex-1 flex flex-col overflow-hidden">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto mb-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <p>Start a conversation to test this sandbox assistant</p>
                    <p className="text-sm mt-2">Your first message will mark this sandbox as "tested"</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="flex-shrink-0">
                {isExpired ? (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    This sandbox has expired and can no longer be tested.
                  </div>
                ) : (
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                      placeholder="Type your message..."
                      className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={isLoading}
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || isLoading}
                    >
                      {isLoading ? (
                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Time Remaining */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Time Remaining</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {isExpired ? 'Expired' : formatTimeRemaining(timeRemaining)}
                  </div>
                  <div className="text-sm text-gray-600">
                    {isExpired ? 'Sandbox has expired' : 'Minutes:Seconds'}
                  </div>
                </div>

                {!isExpired && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span>TTL Progress</span>
                      <span>{Math.round(ttlProgress)}%</span>
                    </div>
                    <Progress value={ttlProgress} className="h-2" />
                  </div>
                )}

                {ttlProgress > 75 && !isExpired && (
                  <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-3 py-2 rounded text-sm">
                    Sandbox expiring soon! Test quickly or create a new one.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Sandbox Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Sandbox Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="font-medium">Sandbox ID</div>
                  <div className="text-gray-600 font-mono text-xs">{sandbox.sandboxId}</div>
                </div>

                <div>
                  <div className="font-medium">Personality</div>
                  <div className="text-gray-600">{sandbox.personalityId}</div>
                </div>

                <div>
                  <div className="font-medium">Guardrail</div>
                  <div className="text-gray-600">{sandbox.guardrailId}</div>
                </div>

                <div>
                  <div className="font-medium">Conversations</div>
                  <div className="text-gray-600">{sandbox.conversationCount}</div>
                </div>

                <div>
                  <div className="font-medium">Created</div>
                  <div className="text-gray-600">{new Date(sandbox.created.at).toLocaleString()}</div>
                </div>

                {sandbox.lastConversationAt && (
                  <div>
                    <div className="font-medium">Last Tested</div>
                    <div className="text-gray-600">{new Date(sandbox.lastConversationAt).toLocaleString()}</div>
                  </div>
                )}

                {sandbox.isPromoted && sandbox.promotedAt && (
                  <div>
                    <div className="font-medium">Promoted</div>
                    <div className="text-gray-600">{new Date(sandbox.promotedAt).toLocaleString()}</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Status Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {sandbox.isPromoted ? (
                  <Badge variant="default" className="w-full justify-center">
                    Already Promoted
                  </Badge>
                ) : canPromote ? (
                  <Button onClick={handlePromoteSandbox} className="w-full bg-green-600 hover:bg-green-700">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Promote to Live
                  </Button>
                ) : hasMessages ? (
                  <div className="text-sm text-gray-600 text-center">
                    Continue testing to enable promotion
                  </div>
                ) : (
                  <div className="text-sm text-gray-600 text-center">
                    Send a message to start testing
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};