import React, { useState, useRef, useEffect } from "react";
import { Send, Wifi, WifiOff, User, Bot, AlertCircle, Check, Clock, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { Card } from "../components/ui/card";
import { chatService } from "../services/ChatService";
import { ChatMessage, ConnectionStatus, ChatResponse, ChatError } from "../types/chat";

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

// Using imported types from chat service
// ChatMessage, ConnectionStatus imported from "../types/chat"

interface ChatInterfaceProps {
  animalId?: string;
  className?: string;
}

// Using ChatService for POST polling instead of SSE
// chatService imported from "../services/ChatService"

// Main Chat Interface Component
const ChatInterface: React.FC<ChatInterfaceProps> = ({
  animalId = "default",
  className = ""
}) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connected');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize session and check connection on mount
  useEffect(() => {
    // Restore session from ChatService
    const existingSession = chatService.getSessionId();
    if (existingSession) {
      setSessionId(existingSession);
    }

    // Check backend connection
    checkConnection();

    // Cleanup function for component unmount
    return () => {
      // ChatService handles request cancellation via AbortController
      // No additional cleanup needed since we removed EventSource
      console.log('Chat component unmounting - requests will be auto-cancelled');
    };
  }, []);

  const checkConnection = async () => {
    setConnectionStatus('connecting');

    try {
      const status = await chatService.checkConnection();
      setConnectionStatus(status);
    } catch (error) {
      console.error('Connection check failed:', error);
      setConnectionStatus('disconnected');
    }
  };

  const handleChatResponse = async (userMessage: string): Promise<void> => {
    setIsLoading(true);

    try {
      // Send message via ChatService POST request
      const response: ChatResponse = await chatService.sendMessage(
        userMessage,
        animalId,
        sessionId || undefined
      );

      // Update session ID if changed
      if (response.sessionId !== sessionId) {
        setSessionId(response.sessionId);
      }

      // Create assistant message from response
      const assistantMessage: ChatMessage = {
        id: response.turnId || `${Date.now()}_assistant`,
        content: response.reply,
        isUser: false,
        timestamp: new Date(response.timestamp),
        status: 'received',
        animalId: response.metadata.animalId,
        sessionId: response.sessionId
      };

      // Add assistant message to conversation
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Chat response error:', error);

      // Create error message
      const errorMessage: ChatMessage = {
        id: `${Date.now()}_error`,
        content: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date(),
        status: 'error',
        animalId,
        sessionId: sessionId || undefined,
        error: error as ChatError
      };

      setMessages(prev => [...prev, errorMessage]);

      // Update connection status if it's a connection error
      if (error instanceof Error && error.message.includes('fetch')) {
        setConnectionStatus('error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || connectionStatus !== 'connected' || isLoading) return;

    const messageId = Date.now().toString();
    const messageContent = input.trim();

    const userMessage: ChatMessage = {
      id: messageId,
      content: messageContent,
      isUser: true,
      timestamp: new Date(),
      status: 'sending',
      animalId,
      sessionId: sessionId || undefined
    };

    // Add user message and clear input
    setMessages(prev => [...prev, userMessage]);
    setInput("");

    // Update message status to sent and get response
    setMessages(prev => prev.map(msg =>
      msg.id === messageId ? { ...msg, status: 'sent' } : msg
    ));

    // Get AI response via POST request
    await handleChatResponse(messageContent);
  };

  const getStatusIcon = (status: ChatMessage['status']) => {
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
            onClick={() => {
              // Clean up current session and start fresh
              chatService.resetSession();
              setSessionId(null);
              setMessages([]);
            }}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
            title="Start new conversation"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
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
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">
                      {message.content}
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

          {/* Loading indicator */}
          {isLoading && (
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
            disabled={connectionStatus !== 'connected' || isLoading}
          />
          <Button
            type="submit"
            disabled={!input.trim() || connectionStatus !== 'connected' || isLoading}
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