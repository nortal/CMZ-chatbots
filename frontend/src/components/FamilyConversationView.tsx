import React, { useState, useEffect } from "react";
import { Users, ChevronRight, Calendar, MessageSquare, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";

interface ChildUser {
  userId: string;
  name: string;
  lastActive?: Date;
  conversationCount: number;
}

interface ChildConversation {
  sessionId: string;
  childId: string;
  childName: string;
  animalName: string;
  timestamp: Date;
  messageCount: number;
  lastMessage?: string;
  sentiment?: string;
}

interface FamilyConversationViewProps {
  parentUserId: string;
  onSessionClick?: (sessionId: string) => void;
}

const FamilyConversationView: React.FC<FamilyConversationViewProps> = ({
  parentUserId,
  onSessionClick
}) => {
  const navigate = useNavigate();
  const [children, setChildren] = useState<ChildUser[]>([]);
  const [selectedChild, setSelectedChild] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ChildConversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFamilyData();
  }, [parentUserId]);

  const fetchFamilyData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) return;

      // Fetch family members
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      const familyResponse = await fetch(`${apiUrl}/families/manage?parentUserId=${parentUserId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (familyResponse.ok) {
        const familyData = await familyResponse.json();
        // Transform family members to children list
        const childUsers: ChildUser[] = (familyData.children || []).map((child: any) => ({
          userId: child.userId,
          name: child.name || child.username,
          lastActive: child.lastActive ? new Date(child.lastActive) : undefined,
          conversationCount: child.conversationCount || 0
        }));
        setChildren(childUsers);
      } else {
        // Use mock data for development
        setChildren([
          {
            userId: "child_001",
            name: "Alice Johnson",
            lastActive: new Date("2025-01-19T10:00:00"),
            conversationCount: 12
          },
          {
            userId: "child_002",
            name: "Bob Johnson",
            lastActive: new Date("2025-01-18T15:30:00"),
            conversationCount: 8
          }
        ]);
      }

      // Fetch conversations for all children
      await fetchChildConversations();
    } catch (error) {
      console.error("Failed to fetch family data:", error);
      // Use mock data
      setChildren([
        {
          userId: "child_001",
          name: "Alice Johnson",
          lastActive: new Date("2025-01-19T10:00:00"),
          conversationCount: 12
        },
        {
          userId: "child_002",
          name: "Bob Johnson",
          lastActive: new Date("2025-01-18T15:30:00"),
          conversationCount: 8
        }
      ]);

      setConversations([
        {
          sessionId: "sess_child_001",
          childId: "child_001",
          childName: "Alice Johnson",
          animalName: "Lion",
          timestamp: new Date("2025-01-19T10:00:00"),
          messageCount: 15,
          lastMessage: "Thank you for teaching me about lions!",
          sentiment: "positive"
        },
        {
          sessionId: "sess_child_002",
          childId: "child_002",
          childName: "Bob Johnson",
          animalName: "Elephant",
          timestamp: new Date("2025-01-18T15:30:00"),
          messageCount: 22,
          lastMessage: "Elephants are so smart!",
          sentiment: "positive"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchChildConversations = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) return;

      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';

      // Fetch conversations for parent's children
      const response = await fetch(`${apiUrl}/convo_history?parentUserId=${parentUserId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        const childConvos: ChildConversation[] = (data.sessions || []).map((session: any) => ({
          sessionId: session.sessionId,
          childId: session.userId,
          childName: session.userName || "Unknown",
          animalName: session.animalName || "Animal",
          timestamp: new Date(session.timestamp || session.createdAt),
          messageCount: session.messageCount || 0,
          lastMessage: session.lastMessage,
          sentiment: session.sentiment
        }));
        setConversations(childConvos);
      }
    } catch (error) {
      console.error("Failed to fetch child conversations:", error);
    }
  };

  const handleSessionClick = (sessionId: string) => {
    if (onSessionClick) {
      onSessionClick(sessionId);
    } else {
      navigate(`/conversations/${sessionId}`);
    }
  };

  const filteredConversations = selectedChild
    ? conversations.filter(conv => conv.childId === selectedChild)
    : conversations;

  const getSentimentBadge = (sentiment?: string) => {
    if (!sentiment) return null;

    const sentimentColors = {
      positive: "bg-green-100 text-green-800",
      neutral: "bg-gray-100 text-gray-800",
      negative: "bg-red-100 text-red-800"
    };

    return (
      <Badge className={sentimentColors[sentiment as keyof typeof sentimentColors] || "bg-gray-100 text-gray-800"}>
        {sentiment}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading family conversations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Family Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Family Members
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              variant={selectedChild === null ? "default" : "outline"}
              className="justify-start"
              onClick={() => setSelectedChild(null)}
            >
              <Users className="h-4 w-4 mr-2" />
              All Children ({children.length})
            </Button>
            {children.map(child => (
              <Button
                key={child.userId}
                variant={selectedChild === child.userId ? "default" : "outline"}
                className="justify-start"
                onClick={() => setSelectedChild(child.userId)}
              >
                <div className="flex items-center justify-between w-full">
                  <span>{child.name}</span>
                  <Badge variant="secondary">{child.conversationCount}</Badge>
                </div>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Conversation Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Conversations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredConversations.length}</div>
            <p className="text-xs text-muted-foreground">
              {selectedChild ? "Selected child" : "All children"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Children</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {children.filter(c => c.lastActive &&
                (new Date().getTime() - c.lastActive.getTime()) < 7 * 24 * 60 * 60 * 1000
              ).length}
            </div>
            <p className="text-xs text-muted-foreground">Last 7 days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Messages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {filteredConversations.reduce((sum, conv) => sum + conv.messageCount, 0)}
            </div>
            <p className="text-xs text-muted-foreground">Across all conversations</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Average Sentiment</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {filteredConversations.filter(c => c.sentiment === 'positive').length >
               filteredConversations.length / 2 ? '😊' : '😐'}
            </div>
            <p className="text-xs text-muted-foreground">
              {Math.round((filteredConversations.filter(c => c.sentiment === 'positive').length /
                Math.max(filteredConversations.length, 1)) * 100)}% positive
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Conversations List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Conversations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredConversations.length === 0 ? (
              <div className="text-center py-8">
                <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  No conversations found for {selectedChild ? "this child" : "your children"}
                </p>
              </div>
            ) : (
              filteredConversations.map(conversation => (
                <div
                  key={conversation.sessionId}
                  className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 cursor-pointer transition-colors"
                  onClick={() => handleSessionClick(conversation.sessionId)}
                >
                  <div className="flex items-start gap-4">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Users className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium">{conversation.childName}</p>
                        <span className="text-muted-foreground">•</span>
                        <Badge variant="outline">{conversation.animalName}</Badge>
                        {getSentimentBadge(conversation.sentiment)}
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        {conversation.lastMessage || "No messages"}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {format(conversation.timestamp, "MMM dd, yyyy")}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {format(conversation.timestamp, "HH:mm")}
                        </span>
                        <span className="flex items-center gap-1">
                          <MessageSquare className="h-3 w-3" />
                          {conversation.messageCount} messages
                        </span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FamilyConversationView;