import React, { useState, useRef, useEffect } from "react";
import { Send, Wifi, WifiOff, User, Bot, AlertCircle, Check, Clock, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { Card } from "../components/ui/card";

// Message Loading Component
function MessageLoading() {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      className="text-foreground"
    >
      <circle cx="4" cy="12" r="2" fill="currentColor">
        <animate
          id="spinner_qFRN"
          begin="0;spinner_OcgL.end+0.25s"
          attributeName="cy"
          calcMode="spline"
          dur="0.6s"
          values="12;6;12"
          keySplines=".33,.66,.66,1;.33,0,.66,.33"
        />
      </circle>
      <circle cx="12" cy="12" r="2" fill="currentColor">
        <animate
          begin="spinner_qFRN.begin+0.1s"
          attributeName="cy"
          calcMode="spline"
          dur="0.6s"
          values="12;6;12"
          keySplines=".33,.66,.66,1;.33,0,.66,.33"
        />
      </circle>
      <circle cx="20" cy="12" r="2" fill="currentColor">
        <animate
          id="spinner_OcgL"
          begin="spinner_qFRN.begin+0.2s"
          attributeName="cy"
          calcMode="spline"
          dur="0.6s"
          values="12;6;12"
          keySplines=".33,.66,.66,1;.33,0,.66,.33"
        />
      </circle>
    </svg>
  );
}

// Spinner Component for connection status
interface SpinnerProps {
  size?: number;
  color?: string;
}

const bars = Array.from({ length: 12 }, (_, i) => ({
  animationDelay: `${-1.2 + i * 0.1}s`,
  transform: `rotate(${i * 30}deg) translate(146%)`
}));

const Spinner = ({ size = 20, color = "#8f8f8f" }: SpinnerProps) => {
  return (
    <div style={{ width: size, height: size }}>
      <style>
        {`
          @keyframes spin {
              0% {
                  opacity: 0.15;
              }
              100% {
                  opacity: 1;
              }
          }
        `}
      </style>
      <div className="relative top-1/2 left-1/2" style={{ width: size, height: size }}>
        {bars.map((item, index) => (
          <div
            key={index}
            className="absolute h-[8%] w-[24%] -left-[10%] -top-[3.9%] rounded-[5px]"
            style={{ backgroundColor: color, animation: "spin 1.2s linear infinite", ...item }}
          />
        ))}
      </div>
    </div>
  );
};

// Types
interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  status: 'sending' | 'sent' | 'received' | 'error';
  isStreaming?: boolean;
  animalId?: string;
  sessionId?: string;
}

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'error';

interface ChatInterfaceProps {
  animalId?: string;
  className?: string;
}

// Chat API service
const chatApi = {
  sendMessage: async (message: string, animalId?: string, sessionId?: string) => {
    const token = localStorage.getItem('authToken');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';

    const response = await fetch(`${apiUrl}/convo_turn`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message,
        animalId,
        sessionId
      })
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  },

  streamMessage: (message: string, animalId?: string, sessionId?: string, onChunk: (chunk: string) => void, onError: (error: Error) => void) => {
    const token = localStorage.getItem('authToken');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';

    const eventSource = new EventSource(
      `${apiUrl}/convo_turn/stream?message=${encodeURIComponent(message)}&animalId=${animalId || ''}&sessionId=${sessionId || ''}&token=${token}`
    );

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.content) {
          onChunk(data.content);
        }
      } catch (error) {
        console.error('Error parsing SSE data:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      onError(new Error('Connection lost'));
      eventSource.close();
    };

    return eventSource;
  }
};

// Main Chat Interface Component
const ChatInterface: React.FC<ChatInterfaceProps> = ({
  animalId = "default",
  className = ""
}) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connected');
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [sessionId] = useState<string>(() => `session_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check connection on mount
  useEffect(() => {
    checkConnection();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const checkConnection = async () => {
    setConnectionStatus('connecting');

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      const response = await fetch(`${apiUrl}/health`);

      if (response.ok) {
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('error');
      }
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const handleStreamingResponse = (userMessageId: string, userMessage: string) => {
    setIsTyping(true);

    const assistantMessageId = Date.now().toString() + '_assistant';
    setStreamingMessageId(assistantMessageId);

    // Add initial empty message
    const assistantMessage: Message = {
      id: assistantMessageId,
      content: "",
      isUser: false,
      timestamp: new Date(),
      status: 'received',
      isStreaming: true,
      animalId,
      sessionId
    };

    setMessages(prev => [...prev, assistantMessage]);

    let accumulatedContent = "";

    // Start SSE streaming
    eventSourceRef.current = chatApi.streamMessage(
      userMessage,
      animalId,
      sessionId,
      (chunk) => {
        accumulatedContent += chunk;

        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: accumulatedContent }
            : msg
        ));
      },
      (error) => {
        console.error('Streaming error:', error);
        setIsTyping(false);

        // Mark message as complete with error
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, isStreaming: false, status: 'error' }
            : msg
        ));

        setStreamingMessageId(null);
        setConnectionStatus('error');
      }
    );

    // Handle streaming completion
    if (eventSourceRef.current) {
      eventSourceRef.current.addEventListener('end', () => {
        setIsTyping(false);
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, isStreaming: false }
            : msg
        ));
        setStreamingMessageId(null);

        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
      });
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || connectionStatus !== 'connected') return;

    const messageId = Date.now().toString();
    const userMessage: Message = {
      id: messageId,
      content: input.trim(),
      isUser: true,
      timestamp: new Date(),
      status: 'sending',
      animalId,
      sessionId
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");

    // Update message status to sent
    setTimeout(() => {
      setMessages(prev => prev.map(msg =>
        msg.id === messageId ? { ...msg, status: 'sent' } : msg
      ));

      // Start streaming response
      handleStreamingResponse(messageId, userMessage.content);
    }, 300);
  };

  const getStatusIcon = (status: Message['status']) => {
    switch (status) {
      case 'sending':
        return <Clock className="w-3 h-3 text-muted-foreground" />;
      case 'sent':
        return <Check className="w-3 h-3 text-muted-foreground" />;
      case 'received':
        return <Check className="w-3 h-3 text-primary" />;
      case 'error':
        return <AlertCircle className="w-3 h-3 text-destructive" />;
      default:
        return null;
    }
  };

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi className="w-4 h-4 text-green-500" />;
      case 'connecting':
        return <Spinner size={16} color="#8f8f8f" />;
      case 'disconnected':
      case 'error':
        return <WifiOff className="w-4 h-4 text-destructive" />;
      default:
        return null;
    }
  };

  return (
    <Card className={`flex flex-col h-[600px] max-w-3xl mx-auto ${className}`}>
      {/* Header with connection status */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-primary" />
          <h2 className="font-semibold">CMZ Chat Assistant</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {getConnectionIcon()}
            <span className="text-sm text-muted-foreground capitalize">
              {connectionStatus}
            </span>
          </div>
          <button
            onClick={() => navigate(-1)}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
            title="Close chat"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Messages area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <Bot className="w-12 h-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">
                Welcome to CMZ Chat
              </h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                Start a conversation with our AI-powered zoo assistant
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!message.isUser && (
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                )}

                <div className={`max-w-[70%] ${message.isUser ? 'order-first' : ''}`}>
                  <div
                    className={`rounded-lg px-4 py-2 ${
                      message.isUser
                        ? 'bg-primary text-primary-foreground ml-auto'
                        : 'bg-muted'
                    } ${message.isStreaming ? 'animate-pulse' : ''}`}
                  >
                    <p className="text-sm whitespace-pre-wrap">
                      {message.content}
                      {message.isStreaming && (
                        <span className="inline-block w-2 h-4 bg-current ml-1 animate-pulse" />
                      )}
                    </p>
                  </div>

                  <div className={`flex items-center gap-1 mt-1 ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                    <span className="text-xs text-muted-foreground">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {message.isUser && getStatusIcon(message.status)}
                  </div>
                </div>

                {message.isUser && (
                  <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {/* Typing indicator */}
          {isTyping && !streamingMessageId && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-primary" />
              </div>
              <div className="bg-muted rounded-lg px-4 py-2">
                <MessageLoading />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input area */}
      <form onSubmit={handleSendMessage} className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1"
            disabled={connectionStatus !== 'connected' || isTyping}
          />
          <Button
            type="submit"
            disabled={!input.trim() || connectionStatus !== 'connected' || isTyping}
            size="icon"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default ChatInterface;