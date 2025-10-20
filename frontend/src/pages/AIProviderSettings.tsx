import React, { useState, useEffect } from 'react';
import { Brain, Key, DollarSign, Save, Plus, Trash2, AlertCircle, CheckCircle } from 'lucide-react';

interface GPTConfig {
  id: string;
  name: string;
  gptId: string;
  animalId?: string;
  createdAt: string;
  lastModified: string;
  status: 'active' | 'inactive' | 'pending';
}

interface AIProviderSettings {
  provider: 'chatgpt' | 'claude' | 'gemini';
  apiKey: string;
  organizationId?: string;
  monthlyBudget?: number;
  currentSpend?: number;
  gpts: GPTConfig[];
}

const AIProviderSettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<AIProviderSettings>({
    provider: 'chatgpt',
    apiKey: '',
    organizationId: '',
    monthlyBudget: 500,
    currentSpend: 127.43,
    gpts: [
      {
        id: '1',
        name: 'Bella the Bear',
        gptId: 'gpt-bella-bear-v1',
        animalId: 'animal-001',
        createdAt: '2024-01-15',
        lastModified: '2024-03-10',
        status: 'active'
      },
      {
        id: '2',
        name: 'Leo the Lion',
        gptId: 'gpt-leo-lion-v1',
        animalId: 'animal-002',
        createdAt: '2024-02-01',
        lastModified: '2024-03-12',
        status: 'active'
      }
    ]
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [newGPTName, setNewGPTName] = useState('');

  const handleSave = async () => {
    setSaveStatus('saving');
    // Simulate API call
    setTimeout(() => {
      setSaveStatus('saved');
      setIsEditing(false);
      setTimeout(() => setSaveStatus('idle'), 3000);
    }, 1000);
  };

  const handleCreateGPT = () => {
    if (newGPTName.trim()) {
      const newGPT: GPTConfig = {
        id: Date.now().toString(),
        name: newGPTName,
        gptId: `gpt-${newGPTName.toLowerCase().replace(/\s+/g, '-')}-v1`,
        createdAt: new Date().toISOString().split('T')[0],
        lastModified: new Date().toISOString().split('T')[0],
        status: 'pending'
      };
      setSettings(prev => ({
        ...prev,
        gpts: [...prev.gpts, newGPT]
      }));
      setNewGPTName('');
    }
  };

  const handleDeleteGPT = (id: string) => {
    setSettings(prev => ({
      ...prev,
      gpts: prev.gpts.filter(gpt => gpt.id !== id)
    }));
  };

  const maskApiKey = (key: string) => {
    if (!key) return '';
    return `${key.substring(0, 7)}${'*'.repeat(20)}${key.substring(key.length - 4)}`;
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Provider Settings</h1>
        <p className="text-gray-600">Configure your AI provider, API credentials, and manage GPT instances</p>
      </div>

      {/* Provider Selection */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center mb-4">
          <Brain className="w-5 h-5 mr-2 text-indigo-600" />
          <h2 className="text-xl font-semibold">AI Provider</h2>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <button
            className={`p-4 rounded-lg border-2 transition-all ${
              settings.provider === 'chatgpt'
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSettings(prev => ({ ...prev, provider: 'chatgpt' }))}
            disabled={!isEditing}
          >
            <div className="font-semibold mb-1">ChatGPT</div>
            <div className="text-sm text-gray-600">OpenAI GPT Models</div>
          </button>

          <button
            className={`p-4 rounded-lg border-2 transition-all ${
              settings.provider === 'claude'
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 hover:border-gray-300'
            } opacity-50 cursor-not-allowed`}
            disabled
          >
            <div className="font-semibold mb-1">Claude</div>
            <div className="text-sm text-gray-600">Coming Soon</div>
          </button>

          <button
            className={`p-4 rounded-lg border-2 transition-all ${
              settings.provider === 'gemini'
                ? 'border-indigo-600 bg-indigo-50'
                : 'border-gray-200 hover:border-gray-300'
            } opacity-50 cursor-not-allowed`}
            disabled
          >
            <div className="font-semibold mb-1">Gemini</div>
            <div className="text-sm text-gray-600">Coming Soon</div>
          </button>
        </div>
      </div>

      {/* API Configuration */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Key className="w-5 h-5 mr-2 text-indigo-600" />
            <h2 className="text-xl font-semibold">API Configuration</h2>
          </div>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
            <div className="flex items-center space-x-2">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={isEditing ? settings.apiKey : maskApiKey(settings.apiKey)}
                onChange={(e) => setSettings(prev => ({ ...prev, apiKey: e.target.value }))}
                disabled={!isEditing}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50"
                placeholder="sk-..."
              />
              <button
                onClick={() => setShowApiKey(!showApiKey)}
                className="px-3 py-2 text-gray-600 hover:text-gray-800"
              >
                {showApiKey ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Organization ID (Optional)</label>
            <input
              type="text"
              value={settings.organizationId}
              onChange={(e) => setSettings(prev => ({ ...prev, organizationId: e.target.value }))}
              disabled={!isEditing}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50"
              placeholder="org-..."
            />
          </div>

          {isEditing && (
            <div className="flex justify-end space-x-2 pt-4">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
              >
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </button>
            </div>
          )}

          {saveStatus === 'saved' && (
            <div className="flex items-center text-green-600 mt-2">
              <CheckCircle className="w-4 h-4 mr-2" />
              <span className="text-sm">Settings saved successfully</span>
            </div>
          )}
        </div>
      </div>

      {/* Billing Information */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center mb-4">
          <DollarSign className="w-5 h-5 mr-2 text-indigo-600" />
          <h2 className="text-xl font-semibold">Billing & Usage</h2>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Budget</label>
            <div className="flex items-center">
              <span className="mr-2 text-gray-600">$</span>
              <input
                type="number"
                value={settings.monthlyBudget}
                onChange={(e) => setSettings(prev => ({ ...prev, monthlyBudget: Number(e.target.value) }))}
                disabled={!isEditing}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-50"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Current Month Spend</label>
            <div className="text-2xl font-semibold text-gray-900">
              ${settings.currentSpend?.toFixed(2)}
            </div>
            {settings.monthlyBudget && (
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      (settings.currentSpend || 0) / settings.monthlyBudget > 0.8
                        ? 'bg-red-600'
                        : 'bg-green-600'
                    }`}
                    style={{ width: `${Math.min(((settings.currentSpend || 0) / settings.monthlyBudget) * 100, 100)}%` }}
                  />
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {((settings.currentSpend || 0) / settings.monthlyBudget * 100).toFixed(1)}% of budget used
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* GPT Management */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">GPT Instances</h2>
          <div className="text-sm text-gray-600">
            {settings.gpts.length} active GPTs
          </div>
        </div>

        <div className="mb-4">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={newGPTName}
              onChange={(e) => setNewGPTName(e.target.value)}
              placeholder="Enter animal name to create new GPT..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleCreateGPT()}
            />
            <button
              onClick={handleCreateGPT}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create GPT
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {settings.gpts.map((gpt) => (
            <div key={gpt.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <h3 className="font-semibold text-gray-900">{gpt.name}</h3>
                    <span className={`ml-3 px-2 py-1 text-xs rounded-full ${
                      gpt.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : gpt.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {gpt.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    <span className="font-mono">{gpt.gptId}</span>
                    {gpt.animalId && (
                      <span className="ml-3">• Linked to Animal: {gpt.animalId}</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Created: {gpt.createdAt} • Last modified: {gpt.lastModified}
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteGPT(gpt.id)}
                  className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {settings.gpts.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Brain className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No GPT instances created yet</p>
            <p className="text-sm mt-1">Create a new GPT for each animal in your zoo</p>
          </div>
        )}

        <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-sm text-amber-800">
              <p className="font-semibold mb-1">Knowledge Base Upload</p>
              <p>When creating a new animal, a corresponding GPT will be automatically created. You can upload knowledge base documents directly to the GPT through the OpenAI platform or via API integration.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIProviderSettingsPage;