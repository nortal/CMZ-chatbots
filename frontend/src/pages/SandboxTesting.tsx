/**
 * SandboxTesting Page Component
 *
 * Main page for managing and testing sandbox assistant configurations.
 * Provides overview of active sandboxes, creation interface, and testing workflows.
 *
 * Features:
 * - List all active sandbox assistants
 * - Create new sandbox from existing assistant
 * - Navigate to sandbox testing interface
 * - Manage sandbox lifecycle (create -> test -> promote/delete)
 * - Auto-cleanup expired sandboxes
 *
 * T046 - User Story 2: Test Assistant Changes Safely
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Plus, Clock, TestTube, Play, Trash2, AlertCircle, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardAction } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { SandboxTester } from '@/components/assistants/SandboxTester';
import { SandboxService, SandboxResponse, CreateSandboxRequest } from '@/services/SandboxService';

interface SandboxTestingProps {}

interface CreateSandboxDialogProps {
  open: boolean;
  onClose: () => void;
  onSandboxCreated: (sandbox: SandboxResponse) => void;
}

const CreateSandboxDialog: React.FC<CreateSandboxDialogProps> = ({ open, onClose, onSandboxCreated }) => {
  const [selectedAssistant, setSelectedAssistant] = useState<string>('');
  const [selectedPersonality, setSelectedPersonality] = useState<string>('');
  const [selectedGuardrail, setSelectedGuardrail] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // Mock data - in real implementation, these would come from API
  const assistants = [
    { id: 'bella-bear', name: 'Bella the Bear' },
    { id: 'casey-cougar', name: 'Casey the Cougar' },
    { id: 'ollie-otter', name: 'Ollie the Otter' }
  ];

  const personalities = [
    { id: 'friendly-educator', name: 'Friendly Educator' },
    { id: 'playful-companion', name: 'Playful Companion' },
    { id: 'wise-mentor', name: 'Wise Mentor' }
  ];

  const guardrails = [
    { id: 'child-safe', name: 'Child Safe' },
    { id: 'educational', name: 'Educational' },
    { id: 'family-friendly', name: 'Family Friendly' }
  ];

  const handleCreateSandbox = async () => {
    if (!selectedPersonality || !selectedGuardrail) {
      setError('Please select both personality and guardrail');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const createRequest: CreateSandboxRequest = {
        animalId: selectedAssistant || undefined,
        personalityId: selectedPersonality,
        guardrailId: selectedGuardrail,
        knowledgeBaseFileIds: []
      };

      const newSandbox = await SandboxService.createSandbox(createRequest);
      onSandboxCreated(newSandbox);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create sandbox');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg max-w-md w-full p-6">
          <h2 className="text-xl font-semibold mb-4">Create Sandbox Assistant</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Base Assistant (Optional)
              </label>
              <select
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                value={selectedAssistant}
                onChange={(e) => setSelectedAssistant(e.target.value)}
              >
                <option value="">New Assistant</option>
                {assistants.map((assistant) => (
                  <option key={assistant.id} value={assistant.id}>
                    {assistant.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Personality *
              </label>
              <select
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                value={selectedPersonality}
                onChange={(e) => setSelectedPersonality(e.target.value)}
                required
              >
                <option value="">Select Personality</option>
                {personalities.map((personality) => (
                  <option key={personality.id} value={personality.id}>
                    {personality.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Guardrail *
              </label>
              <select
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                value={selectedGuardrail}
                onChange={(e) => setSelectedGuardrail(e.target.value)}
                required
              >
                <option value="">Select Guardrail</option>
                {guardrails.map((guardrail) => (
                  <option key={guardrail.id} value={guardrail.id}>
                    {guardrail.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <Button variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button onClick={handleCreateSandbox} disabled={loading}>
              {loading ? 'Creating...' : 'Create Sandbox'}
            </Button>
          </div>
        </div>
      </div>
    </Dialog>
  );
};

const SandboxCard: React.FC<{ sandbox: SandboxResponse; onAction: (action: string, sandbox: SandboxResponse) => void }> = ({
  sandbox,
  onAction
}) => {
  const navigate = useNavigate();
  const status = SandboxService.getSandboxStatus(sandbox);
  const timeRemaining = SandboxService.formatTimeRemaining(sandbox.expiresAt);
  const ttlProgress = SandboxService.getTTLProgress(sandbox.expiresAt);

  const getStatusBadge = () => {
    switch (status) {
      case 'draft':
        return <Badge variant="secondary">Draft</Badge>;
      case 'tested':
        return <Badge variant="default">Tested</Badge>;
      case 'expired':
        return <Badge variant="destructive">Expired</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'draft':
        return <TestTube className="h-4 w-4 text-gray-500" />;
      case 'tested':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'expired':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">
            {sandbox.animalId ? `${sandbox.animalId} Sandbox` : 'New Assistant Sandbox'}
          </CardTitle>
          <CardAction>
            {getStatusBadge()}
          </CardAction>
        </div>
        <div className="text-sm text-gray-600">
          Created {new Date(sandbox.created.at).toLocaleDateString()}
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="text-sm">
              {status === 'expired' ? 'Expired' : `${timeRemaining} remaining`}
            </span>
          </div>

          {status !== 'expired' && (
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span>Time to Live</span>
                <span>{Math.round(ttlProgress)}%</span>
              </div>
              <Progress value={ttlProgress} className="h-2" />
            </div>
          )}

          <div className="text-sm text-gray-600">
            <div>Conversations: {sandbox.conversationCount}</div>
            <div>Personality: {sandbox.personalityId}</div>
            <div>Guardrail: {sandbox.guardrailId}</div>
          </div>

          <div className="flex space-x-2 pt-2">
            <Button
              size="sm"
              onClick={() => navigate(`/sandbox-testing/${sandbox.sandboxId}`)}
              disabled={status === 'expired'}
            >
              <Play className="h-4 w-4 mr-1" />
              Test
            </Button>

            {status === 'tested' && !sandbox.isPromoted && (
              <Button
                size="sm"
                variant="default"
                onClick={() => onAction('promote', sandbox)}
              >
                Promote to Live
              </Button>
            )}

            <Button
              size="sm"
              variant="destructive"
              onClick={() => onAction('delete', sandbox)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const SandboxTesting: React.FC<SandboxTestingProps> = () => {
  const { sandboxId } = useParams();
  const navigate = useNavigate();
  const [sandboxes, setSandboxes] = useState<SandboxResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const loadSandboxes = async () => {
    try {
      setLoading(true);
      const response = await SandboxService.listSandboxes();
      setSandboxes(response.sandboxes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sandboxes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSandboxes();
  }, []);

  const handleSandboxAction = async (action: string, sandbox: SandboxResponse) => {
    try {
      switch (action) {
        case 'promote':
          await SandboxService.promoteSandbox(sandbox.sandboxId);
          break;
        case 'delete':
          await SandboxService.deleteSandbox(sandbox.sandboxId);
          break;
      }
      await loadSandboxes(); // Refresh list
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${action} sandbox`);
    }
  };

  const handleSandboxCreated = (newSandbox: SandboxResponse) => {
    setSandboxes(prev => [...prev, newSandbox]);
    navigate(`/sandbox-testing/${newSandbox.sandboxId}`);
  };

  // If we have a sandboxId, show the individual sandbox tester
  if (sandboxId) {
    const currentSandbox = sandboxes.find(s => s.sandboxId === sandboxId);
    if (!currentSandbox && !loading) {
      return (
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Sandbox Not Found</h1>
            <p className="text-gray-600 mb-4">The requested sandbox may have expired or been deleted.</p>
            <Button onClick={() => navigate('/sandbox-testing')}>
              Back to Sandbox List
            </Button>
          </div>
        </div>
      );
    }

    return currentSandbox ? (
      <SandboxTester sandbox={currentSandbox} onBack={() => navigate('/sandbox-testing')} />
    ) : (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading sandbox...</div>
      </div>
    );
  }

  // Show sandbox list view
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sandbox Testing</h1>
          <p className="text-gray-600 mt-2">
            Test assistant configurations safely before promoting to live
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Sandbox
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">Loading sandboxes...</div>
      ) : sandboxes.length === 0 ? (
        <div className="text-center py-12">
          <TestTube className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No sandbox assistants</h3>
          <p className="text-gray-600 mb-4">Create your first sandbox to start testing configurations</p>
          <Button onClick={() => setCreateDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Sandbox
          </Button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {sandboxes.map((sandbox) => (
            <SandboxCard
              key={sandbox.sandboxId}
              sandbox={sandbox}
              onAction={handleSandboxAction}
            />
          ))}
        </div>
      )}

      <CreateSandboxDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSandboxCreated={handleSandboxCreated}
      />
    </div>
  );
};

export default SandboxTesting;