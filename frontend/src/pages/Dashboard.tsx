import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Users, MessageCircle, Zap, BarChart3, AlertCircle, TrendingUp } from 'lucide-react';

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  onClick?: () => void;
}

const DashboardCard: React.FC<DashboardCardProps> = ({ 
  title, 
  value, 
  icon, 
  change, 
  changeType = 'neutral',
  onClick 
}) => {
  const changeColor = changeType === 'positive' ? 'text-green-600' : 
                     changeType === 'negative' ? 'text-red-600' : 'text-gray-600';
  
  return (
    <div 
      className={`bg-white p-6 rounded-lg border hover:shadow-md transition-shadow ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {change && (
            <p className={`text-sm mt-1 ${changeColor}`}>
              {change}
            </p>
          )}
        </div>
        <div className="p-3 bg-green-50 rounded-full">
          {icon}
        </div>
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) return null;

  const getPersonalizedGreeting = () => {
    const hour = new Date().getHours();
    const timeOfDay = hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening';
    return `Good ${timeOfDay}, ${user.displayName}!`;
  };

  const getDashboardContent = () => {
    switch (user.role) {
      case 'admin':
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <DashboardCard
              title="Total Active Users"
              value="247"
              icon={<Users className="w-6 h-6 text-green-600" />}
              change="+12 this week"
              changeType="positive"
            />
            <DashboardCard
              title="Total Animals"
              value="24"
              icon={<Zap className="w-6 h-6 text-green-600" />}
              change="3 GPTs active"
              changeType="neutral"
            />
            <DashboardCard
              title="Active Conversations"
              value="89"
              icon={<MessageCircle className="w-6 h-6 text-green-600" />}
              change="+15% today"
              changeType="positive"
            />
          </div>
        );

      case 'zookeeper':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <DashboardCard
              title="Animal Interactions"
              value="156"
              icon={<Zap className="w-6 h-6 text-green-600" />}
              change="+23% this week"
              changeType="positive"
            />
            <DashboardCard
              title="Active Chats"
              value="42"
              icon={<MessageCircle className="w-6 h-6 text-green-600" />}
              change="Peak: 3:30 PM"
              changeType="neutral"
            />
            <DashboardCard
              title="Visitor Engagement"
              value="4.2/5"
              icon={<TrendingUp className="w-6 h-6 text-green-600" />}
              change="Above average"
              changeType="positive"
            />
          </div>
        );

      case 'educator':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <DashboardCard
              title="Family Groups"
              value="18"
              icon={<Users className="w-6 h-6 text-green-600" />}
              change="3 new this week"
              changeType="positive"
            />
            <DashboardCard
              title="Educational Sessions"
              value="7"
              icon={<MessageCircle className="w-6 h-6 text-green-600" />}
              change="2 scheduled today"
              changeType="neutral"
            />
            <DashboardCard
              title="Student Engagement"
              value="92%"
              icon={<TrendingUp className="w-6 h-6 text-green-600" />}
              change="+8% improvement"
              changeType="positive"
            />
          </div>
        );

      case 'member':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <DashboardCard
              title="Your Conversations"
              value="12"
              icon={<MessageCircle className="w-6 h-6 text-green-600" />}
              change="Last chat: 2 hours ago"
              changeType="neutral"
            />
            <DashboardCard
              title="Favorite Animals"
              value="5"
              icon={<Zap className="w-6 h-6 text-green-600" />}
              change="Explore more animals"
              changeType="positive"
            />
          </div>
        );

      case 'visitor':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <DashboardCard
              title="Available Animals"
              value="24"
              icon={<Zap className="w-6 h-6 text-green-600" />}
              change="Start chatting now!"
              changeType="positive"
            />
            <DashboardCard
              title="Zoo Information"
              value="Updated"
              icon={<AlertCircle className="w-6 h-6 text-green-600" />}
              change="Hours, events & more"
              changeType="neutral"
            />
          </div>
        );

      default:
        return null;
    }
  };

  const getQuickActions = () => {
    switch (user.role) {
      case 'admin':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <button className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left">
              <h3 className="font-medium text-gray-900 mb-2">Manage Users</h3>
              <p className="text-sm text-gray-600">Add, edit, or remove user accounts</p>
            </button>
            <button className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left">
              <h3 className="font-medium text-gray-900 mb-2">System Health</h3>
              <p className="text-sm text-gray-600">Check system status and logs</p>
            </button>
            <button className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left">
              <h3 className="font-medium text-gray-900 mb-2">Analytics</h3>
              <p className="text-sm text-gray-600">View usage and performance reports</p>
            </button>
          </div>
        );

      case 'zookeeper':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left">
              <h3 className="font-medium text-gray-900 mb-2">Animal Configuration</h3>
              <p className="text-sm text-gray-600">Update animal personalities and details</p>
            </button>
            <button className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left">
              <h3 className="font-medium text-gray-900 mb-2">View Conversations</h3>
              <p className="text-sm text-gray-600">Monitor recent animal interactions</p>
            </button>
          </div>
        );

      case 'educator':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left">
              <h3 className="font-medium text-gray-900 mb-2">Manage Families</h3>
              <p className="text-sm text-gray-600">Add new family groups and members</p>
            </button>
            <button className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left">
              <h3 className="font-medium text-gray-900 mb-2">Educational Content</h3>
              <p className="text-sm text-gray-600">Update knowledge base materials</p>
            </button>
          </div>
        );

      default:
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="p-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-left">
              <h3 className="font-medium mb-2">Chat with Animals</h3>
              <p className="text-sm text-green-100">Start a conversation with our zoo animals</p>
            </button>
            <button className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left">
              <h3 className="font-medium text-gray-900 mb-2">Zoo Information</h3>
              <p className="text-sm text-gray-600">Hours, events, and visitor information</p>
            </button>
          </div>
        );
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {getPersonalizedGreeting()}
        </h1>
        <p className="text-gray-600">
          {user.role === 'admin' && "Monitor and manage your zoo's digital ecosystem."}
          {user.role === 'zookeeper' && "Manage animal interactions and visitor experiences."}
          {user.role === 'educator' && "Coordinate educational programs and family engagement."}
          {user.role === 'member' && "Welcome back! Continue your zoo journey."}
          {user.role === 'visitor' && "Welcome to Cougar Mountain Zoo! Start exploring."}
        </p>
      </div>

      {getDashboardContent()}

      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        {getQuickActions()}
      </div>

      {user.role === 'admin' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-yellow-600 mr-3" />
            <div>
              <h3 className="font-medium text-yellow-800">System Notice</h3>
              <p className="text-sm text-yellow-700 mt-1">
                Scheduled maintenance window: Sunday 2:00 AM - 4:00 AM PST
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;