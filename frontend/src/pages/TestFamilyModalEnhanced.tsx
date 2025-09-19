import React, { useState } from 'react';
import AddFamilyModalEnhanced from '../components/AddFamilyModalEnhanced';
import { Button } from '../components/ui/button';
import { Users } from 'lucide-react';

const TestFamilyModalEnhanced: React.FC = () => {
  const [open, setOpen] = useState(false);

  const handleSubmit = (familyData: any) => {
    console.log('Family data submitted:', familyData);
    // Here you would typically send the data to your backend API
    alert('Family created successfully!');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center space-y-6 max-w-md">
        <h1 className="text-3xl font-bold text-gray-900">
          Family Management System
        </h1>
        <p className="text-gray-600">
          Create and manage family groups for the Cougar Mountain Zoo educational programs.
        </p>

        <Button
          onClick={() => setOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white"
          size="lg"
        >
          <Users className="h-5 w-5 mr-2" />
          Add New Family
        </Button>

        <AddFamilyModalEnhanced
          open={open}
          onOpenChange={setOpen}
          onSubmit={handleSubmit}
        />

        <div className="mt-8 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
          <h2 className="font-semibold text-gray-900 mb-2">Features:</h2>
          <ul className="text-left text-sm text-gray-600 space-y-1">
            <li>✓ Responsive modal dialog with smooth animations</li>
            <li>✓ Typeahead search for existing users</li>
            <li>✓ Add multiple children and parents</li>
            <li>✓ Removable user chips</li>
            <li>✓ Full address input</li>
            <li>✓ Form validation</li>
            <li>✓ Keyboard accessible</li>
            <li>✓ Scrollable content for long forms</li>
            <li>✓ Sticky footer with action buttons</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TestFamilyModalEnhanced;