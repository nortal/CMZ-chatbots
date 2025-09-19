import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, Users, Calendar, Activity, ChevronDown, ChevronUp, Star } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface AnimalConversation {
  id: string;
  animalName: string;
  animalType: string;
  animalAvatar: string;
  conversationCount: number;
  messageCount: number;
  lastActivity: string;
  activityLevel: "low" | "medium" | "high";
  dataUsage: number; // in MB
}

interface Child {
  id: string;
  name: string;
  avatar: string;
  age: number;
  totalConversations: number;
  totalMessages: number;
  totalDataUsage: number;
  lastActive: string;
  conversations: AnimalConversation[];
}

interface ParentDashboardProps {
  children?: Child[];
}

// Mock data for development - replace with actual API calls
const mockChildren: Child[] = [
  {
    id: "1",
    name: "Emma",
    avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b47c?w=96&q=80&auto=format&fit=crop",
    age: 8,
    totalConversations: 24,
    totalMessages: 156,
    totalDataUsage: 45.2,
    lastActive: "2 hours ago",
    conversations: [
      {
        id: "c1",
        animalName: "Bella",
        animalType: "Bear",
        animalAvatar: "🐻",
        conversationCount: 8,
        messageCount: 42,
        lastActivity: "2 hours ago",
        activityLevel: "high",
        dataUsage: 12.3
      },
      {
        id: "c2",
        animalName: "Leo",
        animalType: "Lion",
        animalAvatar: "🦁",
        conversationCount: 12,
        messageCount: 78,
        lastActivity: "1 day ago",
        activityLevel: "medium",
        dataUsage: 18.7
      },
      {
        id: "c3",
        animalName: "Cougar",
        animalType: "Mountain Lion",
        animalAvatar: "🐆",
        conversationCount: 4,
        messageCount: 36,
        lastActivity: "3 days ago",
        activityLevel: "low",
        dataUsage: 14.2
      }
    ]
  },
  {
    id: "2",
    name: "Alex",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=96&q=80&auto=format&fit=crop",
    age: 10,
    totalConversations: 18,
    totalMessages: 124,
    totalDataUsage: 32.8,
    lastActive: "5 hours ago",
    conversations: [
      {
        id: "c4",
        animalName: "Max",
        animalType: "Wolf",
        animalAvatar: "🐺",
        conversationCount: 6,
        messageCount: 34,
        lastActivity: "5 hours ago",
        activityLevel: "medium",
        dataUsage: 9.4
      },
      {
        id: "c5",
        animalName: "Ruby",
        animalType: "Red Panda",
        animalAvatar: "🐼",
        conversationCount: 10,
        messageCount: 67,
        lastActivity: "1 day ago",
        activityLevel: "high",
        dataUsage: 15.6
      },
      {
        id: "c6",
        animalName: "Hoppy",
        animalType: "Rabbit",
        animalAvatar: "🐰",
        conversationCount: 2,
        messageCount: 23,
        lastActivity: "4 days ago",
        activityLevel: "low",
        dataUsage: 7.8
      }
    ]
  }
];

const getActivityColor = (level: "low" | "medium" | "high") => {
  switch (level) {
    case "high": return "bg-green-500";
    case "medium": return "bg-yellow-500";
    case "low": return "bg-red-500";
    default: return "bg-gray-500";
  }
};

const getActivityBadgeVariant = (level: "low" | "medium" | "high"): "default" | "secondary" | "destructive" => {
  switch (level) {
    case "high": return "default";
    case "medium": return "secondary";
    case "low": return "destructive";
    default: return "secondary";
  }
};

const formatDataUsage = (usage: number) => {
  if (usage < 1024) return `${usage.toFixed(1)} MB`;
  return `${(usage / 1024).toFixed(1)} GB`;
};

const AnimatedProgressBar = ({ value, className = "" }: { value: number; className?: string }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setProgress(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  return (
    <div className={`w-full ${className}`}>
      <Progress value={progress} className="h-2" />
    </div>
  );
};

const ChildCard = ({ child }: { child: Child }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [animationKey, setAnimationKey] = useState(0);

  useEffect(() => {
    if (isExpanded) {
      setAnimationKey(prev => prev + 1);
    }
  }, [isExpanded]);

  return (
    <Card className="w-full transition-all duration-300 hover:shadow-lg">
      <CardHeader
        className="cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Avatar className="h-12 w-12">
              <AvatarImage src={child.avatar} alt={child.name} />
              <AvatarFallback>{child.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-lg">{child.name}</CardTitle>
              <p className="text-sm text-muted-foreground">Age {child.age} • Last active {child.lastActive}</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <MessageCircle className="h-4 w-4" />
                <span>{child.totalConversations} conversations</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Activity className="h-4 w-4" />
                <span>{formatDataUsage(child.totalDataUsage)} used</span>
              </div>
            </div>
            <Button variant="ghost" size="sm">
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <CardContent className="pt-0">
              <div className="grid gap-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="bg-muted/50 rounded-lg p-3">
                    <div className="flex items-center space-x-2 mb-1">
                      <MessageCircle className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">Total Messages</span>
                    </div>
                    <p className="text-2xl font-bold">{child.totalMessages}</p>
                  </div>
                  <div className="bg-muted/50 rounded-lg p-3">
                    <div className="flex items-center space-x-2 mb-1">
                      <Users className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium">Animals</span>
                    </div>
                    <p className="text-2xl font-bold">{child.conversations.length}</p>
                  </div>
                  <div className="bg-muted/50 rounded-lg p-3">
                    <div className="flex items-center space-x-2 mb-1">
                      <Activity className="h-4 w-4 text-purple-500" />
                      <span className="text-sm font-medium">Data Usage</span>
                    </div>
                    <p className="text-2xl font-bold">{formatDataUsage(child.totalDataUsage)}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-semibold flex items-center space-x-2">
                    <Star className="h-4 w-4" />
                    <span>Animal Conversations</span>
                  </h4>
                  {child.conversations.map((conversation, index) => (
                    <motion.div
                      key={conversation.id}
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: index * 0.1, duration: 0.3 }}
                      className="border rounded-lg p-4 bg-card hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className="text-2xl">{conversation.animalAvatar}</div>
                          <div>
                            <h5 className="font-medium">{conversation.animalName}</h5>
                            <p className="text-sm text-muted-foreground">{conversation.animalType}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={getActivityBadgeVariant(conversation.activityLevel)}>
                            {conversation.activityLevel} activity
                          </Badge>
                          <div className={`w-2 h-2 rounded-full ${getActivityColor(conversation.activityLevel)}`} />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                        <div>
                          <p className="text-xs text-muted-foreground">Conversations</p>
                          <p className="font-semibold">{conversation.conversationCount}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Messages</p>
                          <p className="font-semibold">{conversation.messageCount}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Data Used</p>
                          <p className="font-semibold">{formatDataUsage(conversation.dataUsage)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Last Active</p>
                          <p className="font-semibold text-xs">{conversation.lastActivity}</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span>Message Activity</span>
                          <span>{Math.round((conversation.messageCount / child.totalMessages) * 100)}%</span>
                        </div>
                        <AnimatedProgressBar
                          key={`${animationKey}-${conversation.id}`}
                          value={(conversation.messageCount / child.totalMessages) * 100}
                        />
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

const ParentDashboard = ({ children = mockChildren }: ParentDashboardProps) => {
  const totalChildren = children.length;
  const totalConversations = children.reduce((sum, child) => sum + child.totalConversations, 0);
  const totalMessages = children.reduce((sum, child) => sum + child.totalMessages, 0);
  const totalDataUsage = children.reduce((sum, child) => sum + child.totalDataUsage, 0);

  // TODO: Fetch actual data from API
  // useEffect(() => {
  //   fetchParentData();
  // }, []);

  return (
    <div className="min-h-screen bg-background p-4 md:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Parent Dashboard</h1>
          <p className="text-muted-foreground">Monitor your children's animal conversation activities</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Children</p>
                  <p className="text-2xl font-bold">{totalChildren}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <MessageCircle className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Conversations</p>
                  <p className="text-2xl font-bold">{totalConversations}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-purple-500" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Messages</p>
                  <p className="text-2xl font-bold">{totalMessages}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-orange-500" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Data Usage</p>
                  <p className="text-2xl font-bold">{formatDataUsage(totalDataUsage)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">Children Overview</h2>
          <div className="space-y-4">
            {children.map((child) => (
              <ChildCard key={child.id} child={child} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParentDashboard;