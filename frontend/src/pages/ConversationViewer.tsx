import React, { useState, useRef, useCallback, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Download,
  FileText,
  FileJson,
  Printer,
  Search,
  Calendar,
  Clock,
  MessageSquare,
  Trash2,
  Bot,
  User
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Separator } from "../components/ui/separator";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "../components/ui/dropdown-menu";
import { useAuth } from "../contexts/AuthContext";

// Types
interface Message {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: Date;
  tokensUsed?: number;
}

interface ConversationData {
  id: string;
  title: string;
  date: Date;
  duration: string;
  messageCount: number;
  animalId: string;
  animalName?: string;
  messages: Message[];
  tokensTotal?: number;
  sentiment?: string;
  topics?: string[];
}

// API service
const conversationApi = {
  getConversation: async (token: string, sessionId: string) => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';

    const response = await fetch(`${apiUrl}/convo_history?sessionId=${sessionId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch conversation');
    }

    return response.json();
  },

  deleteConversation: async (token: string, sessionId: string) => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';

    const response = await fetch(`${apiUrl}/convo_history?sessionId=${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to delete conversation');
    }

    return response.status === 204;
  }
};

// Custom hook for auto-scroll
function useAutoScroll(options: { smooth?: boolean; content?: any } = {}) {
  const { smooth = false, content } = options;
  const scrollRef = useRef<HTMLDivElement>(null);
  const lastContentHeight = useRef(0);

  const scrollToBottom = useCallback(() => {
    if (!scrollRef.current) return;

    const targetScrollTop =
      scrollRef.current.scrollHeight - scrollRef.current.clientHeight;

    scrollRef.current.scrollTo({
      top: targetScrollTop,
      behavior: smooth ? "smooth" : "auto",
    });
  }, [smooth]);

  useEffect(() => {
    const scrollElement = scrollRef.current;
    if (!scrollElement) return;

    const currentHeight = scrollElement.scrollHeight;
    if (currentHeight !== lastContentHeight.current) {
      scrollToBottom();
      lastContentHeight.current = currentHeight;
    }
  }, [content, scrollToBottom]);

  return { scrollRef, scrollToBottom };
}

// Back button component
const BackButton = ({ onClick }: { onClick: () => void }) => {
  return (
    <Button
      variant="outline"
      className="group relative overflow-hidden"
      onClick={onClick}
    >
      <span className="flex items-center gap-2">
        <ArrowLeft className="h-4 w-4" />
        Back
      </span>
    </Button>
  );
};

// Message bubble component
const MessageBubble = ({
  message,
  isSearchHighlighted,
  animalName
}: {
  message: Message;
  isSearchHighlighted: boolean;
  animalName?: string;
}) => {
  const isUser = message.sender === "user";

  return (
    <div
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} ${
        isSearchHighlighted
          ? "bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-2"
          : ""
      }`}
    >
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback>
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div
        className={`flex flex-col max-w-[70%] ${
          isUser ? "items-end" : "items-start"
        }`}
      >
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-muted"
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
          <span>{isUser ? "You" : animalName || "Assistant"}</span>
          <span>•</span>
          <span>{message.timestamp.toLocaleTimeString()}</span>
          {message.tokensUsed && (
            <>
              <span>•</span>
              <span>{message.tokensUsed} tokens</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// Main component
const ConversationViewer: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [conversationData, setConversationData] = useState<ConversationData | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredMessages, setFilteredMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { scrollRef, scrollToBottom } = useAutoScroll({
    smooth: true,
    content: filteredMessages.length,
  });

  // Fetch conversation data
  useEffect(() => {
    if (!sessionId) return;

    const fetchConversation = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('authToken');
        if (!token) {
          setError('Not authenticated');
          return;
        }

        const data = await conversationApi.getConversation(token, sessionId);

        // Transform the response data
        const messages: Message[] = (data.messages || []).map((msg: any, index: number) => ({
          id: `msg_${index}`,
          content: msg.content || msg.userMessage || msg.assistantReply || '',
          sender: msg.role === 'assistant' || msg.assistantReply ? 'assistant' : 'user',
          timestamp: new Date(msg.timestamp || Date.now()),
          tokensUsed: msg.tokensUsed
        }));

        setConversationData({
          id: sessionId,
          title: `Conversation with ${data.sessionInfo?.animalName || 'Animal'}`,
          date: new Date(data.sessionInfo?.createdAt || Date.now()),
          duration: calculateDuration(data.sessionInfo?.createdAt, data.sessionInfo?.updatedAt),
          messageCount: messages.length,
          animalId: data.sessionInfo?.animalId || 'default',
          animalName: data.sessionInfo?.animalName,
          messages,
          tokensTotal: messages.reduce((sum, msg) => sum + (msg.tokensUsed || 0), 0),
          sentiment: data.sessionInfo?.sentiment,
          topics: data.sessionInfo?.topics
        });

        setFilteredMessages(messages);
      } catch (err) {
        console.error('Failed to fetch conversation:', err);
        setError('Failed to load conversation');

        // Mock data for development
        const mockMessages: Message[] = [
          {
            id: "1",
            content: "Tell me about lions!",
            sender: "user",
            timestamp: new Date("2025-01-15T10:30:00"),
            tokensUsed: 5
          },
          {
            id: "2",
            content: "Lions are magnificent big cats! They're known as the 'king of the jungle' even though they actually live in savannas. Did you know that a lion's roar can be heard up to 5 miles away? They use this powerful voice to communicate with their pride and mark their territory.",
            sender: "assistant",
            timestamp: new Date("2025-01-15T10:30:15"),
            tokensUsed: 47
          },
          {
            id: "3",
            content: "That's amazing! How do they hunt?",
            sender: "user",
            timestamp: new Date("2025-01-15T10:31:00"),
            tokensUsed: 7
          },
          {
            id: "4",
            content: "Lions are incredible hunters! The lionesses do most of the hunting for the pride. They work together as a team, using smart strategies. Some lionesses chase the prey while others wait in ambush. They usually hunt at dawn or dusk when it's cooler. Their teamwork is what makes them so successful!",
            sender: "assistant",
            timestamp: new Date("2025-01-15T10:31:30"),
            tokensUsed: 52
          }
        ];

        setConversationData({
          id: sessionId,
          title: "Conversation with Lion",
          date: new Date("2025-01-15T10:30:00"),
          duration: "2m 30s",
          messageCount: 4,
          animalId: "lion_001",
          animalName: "Lion",
          messages: mockMessages,
          tokensTotal: 111,
          sentiment: "positive",
          topics: ["animal behavior", "hunting", "habitat"]
        });

        setFilteredMessages(mockMessages);
      } finally {
        setLoading(false);
      }
    };

    fetchConversation();
  }, [sessionId]);

  // Filter messages based on search
  useEffect(() => {
    if (!conversationData) return;

    if (searchQuery.trim() === "") {
      setFilteredMessages(conversationData.messages);
    } else {
      const filtered = conversationData.messages.filter((message) =>
        message.content.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredMessages(filtered);
    }
  }, [searchQuery, conversationData]);

  const calculateDuration = (start: string, end: string): string => {
    if (!start || !end) return "N/A";
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    const duration = endTime - startTime;
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  const handleExport = (format: "pdf" | "txt" | "json") => {
    if (!conversationData) return;

    const data =
      format === "json"
        ? JSON.stringify(conversationData, null, 2)
        : conversationData.messages
            .map(
              (m) =>
                `[${m.timestamp.toLocaleString()}] ${m.sender}: ${m.content}`
            )
            .join("\n\n");

    const blob = new Blob([data], {
      type: format === "json" ? "application/json" : "text/plain",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `conversation-${conversationData.id}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDelete = async () => {
    if (!conversationData) return;

    if (
      window.confirm(
        "Are you sure you want to permanently delete this conversation? This action cannot be undone."
      )
    ) {
      try {
        const token = localStorage.getItem('authToken');
        if (!token) return;

        await conversationApi.deleteConversation(token, conversationData.id);
        navigate("/conversations/history");
      } catch (err) {
        console.error("Failed to delete conversation:", err);
        alert("Failed to delete conversation");
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading conversation...</p>
        </div>
      </div>
    );
  }

  if (error || !conversationData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-destructive">{error || "Conversation not found"}</p>
          <Button
            className="mt-4"
            onClick={() => navigate("/conversations/history")}
          >
            Back to History
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <BackButton onClick={() => navigate("/conversations/history")} />
              <div>
                <h1 className="text-2xl font-bold">{conversationData.title}</h1>
                <p className="text-sm text-muted-foreground">
                  {conversationData.animalName} • {conversationData.date.toLocaleDateString()}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon">
                    <Download className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => handleExport("pdf")}>
                    <FileText className="h-4 w-4 mr-2" />
                    Export as PDF
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleExport("txt")}>
                    <FileText className="h-4 w-4 mr-2" />
                    Export as TXT
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleExport("json")}>
                    <FileJson className="h-4 w-4 mr-2" />
                    Export as JSON
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Button variant="outline" size="icon" onClick={handlePrint}>
                <Printer className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar with metadata */}
          <div className="lg:col-span-1 space-y-6">
            {/* Session Metadata */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Session Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    {conversationData.date.toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">{conversationData.duration}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">
                    {conversationData.messageCount} messages
                  </span>
                </div>
                <Separator />
                <div className="space-y-2">
                  <p className="text-sm font-medium">Tokens Used</p>
                  <p className="text-2xl font-bold">
                    {conversationData.tokensTotal?.toLocaleString() || 0}
                  </p>
                </div>
                {conversationData.sentiment && (
                  <>
                    <Separator />
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Sentiment</p>
                      <Badge variant="secondary">{conversationData.sentiment}</Badge>
                    </div>
                  </>
                )}
                {conversationData.topics && conversationData.topics.length > 0 && (
                  <>
                    <Separator />
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Topics</p>
                      <div className="flex flex-wrap gap-1">
                        {conversationData.topics.map((topic, index) => (
                          <Badge key={index} variant="outline">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Delete Conversation (admin only) */}
            {user?.role === 'admin' && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Danger Zone</CardTitle>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="destructive"
                    size="sm"
                    className="w-full"
                    onClick={handleDelete}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Conversation
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Main conversation area */}
          <div className="lg:col-span-3">
            <Card className="h-[calc(100vh-200px)]">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search in conversation..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button variant="outline" size="sm" onClick={scrollToBottom}>
                    Scroll to bottom
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="flex-1 overflow-hidden">
                <div
                  ref={scrollRef}
                  className="h-full overflow-y-auto pr-4 pb-4"
                >
                  <div className="space-y-6">
                    {filteredMessages.length === 0 ? (
                      <div className="text-center py-8">
                        <p className="text-muted-foreground">
                          {searchQuery
                            ? "No messages match your search"
                            : "No messages in this conversation"}
                        </p>
                      </div>
                    ) : (
                      filteredMessages.map((message) => (
                        <MessageBubble
                          key={message.id}
                          message={message}
                          animalName={conversationData.animalName}
                          isSearchHighlighted={
                            searchQuery.trim() !== "" &&
                            message.content
                              .toLowerCase()
                              .includes(searchQuery.toLowerCase())
                          }
                        />
                      ))
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationViewer;