import React, { useState, useEffect, useMemo } from "react";
import {
  Search,
  Download,
  Calendar,
  ChevronDown,
  ChevronUp,
  Eye,
  Users,
  MessageSquare,
  Clock,
  CheckCircle,
  Archive,
  AlertCircle,
  Home
} from "lucide-react";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Popover, PopoverContent, PopoverTrigger } from "../components/ui/popover";
import { Calendar as CalendarComponent } from "../components/ui/calendar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import FamilyConversationView from "../components/FamilyConversationView";
import { cn } from "../lib/utils";

// Types
interface ChatSession {
  sessionId: string;
  userId: string;
  userName?: string;
  animalId: string;
  animalName?: string;
  timestamp: Date;
  messageCount: number;
  status: 'active' | 'completed' | 'archived';
  lastMessage?: string;
}

// API service
const chatHistoryApi = {
  getSessions: async (token: string, filters?: {
    userId?: string;
    animalId?: string;
    startDate?: string;
    endDate?: string;
  }) => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';

    const queryParams = new URLSearchParams();
    if (filters?.userId) queryParams.append('userId', filters.userId);
    if (filters?.animalId) queryParams.append('animalId', filters.animalId);
    if (filters?.startDate) queryParams.append('startDate', filters.startDate);
    if (filters?.endDate) queryParams.append('endDate', filters.endDate);

    const response = await fetch(`${apiUrl}/convo_history?${queryParams.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch conversation history');
    }

    return response.json();
  }
};

// Status badge component
const StatusBadge = ({ status }: { status: ChatSession['status'] }) => {
  const variants = {
    active: { color: "bg-green-100 text-green-800 border-green-200", icon: CheckCircle },
    completed: { color: "bg-blue-100 text-blue-800 border-blue-200", icon: Clock },
    archived: { color: "bg-gray-100 text-gray-800 border-gray-200", icon: Archive }
  };

  const variant = variants[status];
  const Icon = variant.icon;

  return (
    <Badge variant="outline" className={cn("flex items-center gap-1", variant.color)}>
      <Icon className="h-3 w-3" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
};

// Date range picker component
const DateRangePicker = ({
  startDate,
  endDate,
  onDateChange
}: {
  startDate?: Date;
  endDate?: Date;
  onDateChange: (start?: Date, end?: Date) => void;
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="w-[240px] justify-start text-left font-normal">
          <Calendar className="mr-2 h-4 w-4" />
          {startDate && endDate ? (
            `${format(startDate, "MMM dd")} - ${format(endDate, "MMM dd")}`
          ) : (
            "Select date range"
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-4 space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Start Date</label>
            <CalendarComponent
              mode="single"
              selected={startDate}
              onSelect={(date) => onDateChange(date, endDate)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">End Date</label>
            <CalendarComponent
              mode="single"
              selected={endDate}
              onSelect={(date) => onDateChange(startDate, date)}
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                onDateChange(undefined, undefined);
                setIsOpen(false);
              }}
            >
              Clear
            </Button>
            <Button size="sm" onClick={() => setIsOpen(false)}>
              Apply
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};

// Main component
const ChatHistory: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters and state
  const [search, setSearch] = useState("");
  const [animalFilter, setAnimalFilter] = useState<string>("all");
  const [userFilter, setUserFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [startDate, setStartDate] = useState<Date>();
  const [endDate, setEndDate] = useState<Date>();
  const [sortField, setSortField] = useState<keyof ChatSession>("timestamp");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Fetch sessions on mount and when filters change
  useEffect(() => {
    fetchSessions();
  }, [startDate, endDate]);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Not authenticated');
        return;
      }

      const filters: any = {};
      if (startDate) filters.startDate = startDate.toISOString();
      if (endDate) filters.endDate = endDate.toISOString();

      const data = await chatHistoryApi.getSessions(token, filters);

      // Transform the response data
      const transformedSessions: ChatSession[] = (data.sessions || []).map((session: any) => ({
        sessionId: session.sessionId,
        userId: session.userId || 'unknown',
        userName: session.userName || session.userId,
        animalId: session.animalId || 'default',
        animalName: session.animalName || session.animalId,
        timestamp: new Date(session.timestamp || session.createdAt),
        messageCount: session.messageCount || session.analytics?.messageCount || 0,
        status: session.status || 'active',
        lastMessage: session.lastMessage
      }));

      setSessions(transformedSessions);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
      setError('Failed to load conversation history');

      // Use mock data for development
      setSessions([
        {
          sessionId: "sess_001",
          userId: "user_001",
          userName: "Alice Johnson",
          animalId: "lion_001",
          animalName: "Lion",
          timestamp: new Date("2025-01-15T10:30:00"),
          messageCount: 45,
          status: "completed",
          lastMessage: "Thank you for teaching me about lions!"
        },
        {
          sessionId: "sess_002",
          userId: "user_002",
          userName: "Bob Smith",
          animalId: "elephant_001",
          animalName: "Elephant",
          timestamp: new Date("2025-01-14T14:20:00"),
          messageCount: 23,
          status: "active",
          lastMessage: "How do elephants communicate?"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Apply filters and search
  const filteredSessions = useMemo(() => {
    let filtered = sessions;

    // Search filter
    if (search) {
      filtered = filtered.filter(session =>
        session.sessionId.toLowerCase().includes(search.toLowerCase()) ||
        session.userName?.toLowerCase().includes(search.toLowerCase()) ||
        session.animalName?.toLowerCase().includes(search.toLowerCase()) ||
        session.lastMessage?.toLowerCase().includes(search.toLowerCase())
      );
    }

    // Animal filter
    if (animalFilter !== "all") {
      filtered = filtered.filter(session => session.animalName === animalFilter);
    }

    // User filter
    if (userFilter !== "all") {
      filtered = filtered.filter(session => session.userName === userFilter);
    }

    // Status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter(session => session.status === statusFilter);
    }

    return filtered;
  }, [sessions, search, animalFilter, userFilter, statusFilter]);

  // Sort sessions
  const sortedSessions = useMemo(() => {
    return [...filteredSessions].sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];

      if (aValue < bValue) return sortDirection === "asc" ? -1 : 1;
      if (aValue > bValue) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
  }, [filteredSessions, sortField, sortDirection]);

  // Pagination
  const paginatedSessions = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedSessions.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedSessions, currentPage]);

  const totalPages = Math.ceil(sortedSessions.length / itemsPerPage);

  // Get unique values for filters
  const uniqueAnimals = [...new Set(sessions.map(s => s.animalName).filter(Boolean))];
  const uniqueUsers = [...new Set(sessions.map(s => s.userName).filter(Boolean))];

  const handleSort = (field: keyof ChatSession) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const handleSessionClick = (sessionId: string) => {
    navigate(`/conversations/${sessionId}`);
  };

  const handleExportCSV = () => {
    const csvContent = [
      ["Session ID", "User", "Animal", "Date", "Message Count", "Status", "Last Message"],
      ...sortedSessions.map(session => [
        session.sessionId,
        session.userName || session.userId,
        session.animalName || session.animalId,
        format(session.timestamp, "yyyy-MM-dd HH:mm"),
        session.messageCount.toString(),
        session.status,
        session.lastMessage || ""
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `chat-history-${format(new Date(), "yyyy-MM-dd")}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const SortButton = ({ field, children }: { field: keyof ChatSession; children: React.ReactNode }) => (
    <Button
      variant="ghost"
      size="sm"
      className="h-auto p-0 font-medium"
      onClick={() => handleSort(field)}
    >
      <span className="flex items-center gap-1">
        {children}
        {sortField === field && (
          sortDirection === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
        )}
      </span>
    </Button>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading conversation history...</p>
        </div>
      </div>
    );
  }

  // Extract the sessions view into a separate function for reuse
  const renderSessionsView = () => (
    <>
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sessions.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.filter(s => s.status === 'active').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Messages</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.reduce((sum, s) => sum + s.messageCount, 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unique Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{uniqueUsers.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search sessions, users, animals, or messages..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Date Range */}
            <DateRangePicker
              startDate={startDate}
              endDate={endDate}
              onDateChange={(start, end) => {
                setStartDate(start);
                setEndDate(end);
              }}
            />

            {/* Animal Filter */}
            <Select value={animalFilter} onValueChange={setAnimalFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Animal" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Animals</SelectItem>
                {uniqueAnimals.map(animal => (
                  <SelectItem key={animal} value={animal}>{animal}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* User Filter (for admins/parents) */}
            {user?.role !== 'student' && (
              <Select value={userFilter} onValueChange={setUserFilter}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="User" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Users</SelectItem>
                  {uniqueUsers.map(userName => (
                    <SelectItem key={userName} value={userName}>{userName}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>
                  <SortButton field="sessionId">Session ID</SortButton>
                </TableHead>
                {user?.role !== 'student' && (
                  <TableHead>
                    <SortButton field="userName">User</SortButton>
                  </TableHead>
                )}
                <TableHead>
                  <SortButton field="animalName">Animal</SortButton>
                </TableHead>
                <TableHead>
                  <SortButton field="timestamp">Date</SortButton>
                </TableHead>
                <TableHead>
                  <SortButton field="messageCount">Messages</SortButton>
                </TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Message</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedSessions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={user?.role !== 'student' ? 8 : 7} className="text-center py-8">
                    <div className="flex flex-col items-center gap-2">
                      <AlertCircle className="h-8 w-8 text-muted-foreground" />
                      <p className="text-muted-foreground">No sessions found</p>
                      {error && <p className="text-sm text-destructive">{error}</p>}
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                paginatedSessions.map((session) => (
                  <TableRow
                    key={session.sessionId}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => handleSessionClick(session.sessionId)}
                  >
                    <TableCell className="font-mono text-sm">
                      {session.sessionId}
                    </TableCell>
                    {user?.role !== 'student' && (
                      <TableCell className="font-medium">
                        {session.userName || session.userId}
                      </TableCell>
                    )}
                    <TableCell>
                      <Badge variant="secondary">{session.animalName || session.animalId}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span>{format(session.timestamp, "MMM dd, yyyy")}</span>
                        <span className="text-xs text-muted-foreground">
                          {format(session.timestamp, "HH:mm")}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4 text-muted-foreground" />
                        {session.messageCount}
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={session.status} />
                    </TableCell>
                    <TableCell className="max-w-[200px]">
                      <p className="truncate text-sm text-muted-foreground">
                        {session.lastMessage}
                      </p>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSessionClick(session.sessionId);
                        }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {(currentPage - 1) * itemsPerPage + 1} to{" "}
            {Math.min(currentPage * itemsPerPage, sortedSessions.length)} of{" "}
            {sortedSessions.length} sessions
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const page = i + 1;
                return (
                  <Button
                    key={page}
                    variant={currentPage === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPage(page)}
                  >
                    {page}
                  </Button>
                );
              })}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </>
  );

  // For parent users, show tabs with family view
  if (user?.role === 'parent') {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Conversation History</h1>
            <p className="text-muted-foreground">
              View family conversations and your personal chat sessions
            </p>
          </div>
        </div>

        {/* Tabs for Parent View */}
        <Tabs defaultValue="family" className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="family" className="flex items-center gap-2">
              <Home className="h-4 w-4" />
              Family Overview
            </TabsTrigger>
            <TabsTrigger value="personal" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              My Sessions
            </TabsTrigger>
          </TabsList>

          <TabsContent value="family" className="space-y-4">
            <FamilyConversationView
              parentUserId={user.userId || user.id}
              onSessionClick={handleSessionClick}
            />
          </TabsContent>

          <TabsContent value="personal" className="space-y-4">
            {/* Personal sessions view - continue with the rest of the component */}
            {renderSessionsView()}
          </TabsContent>
        </Tabs>
      </div>
    );
  }

  // For non-parent users, show regular view
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Conversation History</h1>
          <p className="text-muted-foreground">
            View and manage past chat sessions
          </p>
        </div>
        <Button onClick={handleExportCSV} className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export CSV
        </Button>
      </div>
      {renderSessionsView()}
    </div>
  );
};

export default ChatHistory;