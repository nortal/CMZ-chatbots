# User Search Component Documentation

## Overview

The UserSearch component provides a comprehensive user search interface for the CMZ platform with multiple filter criteria, results display, and responsive design.

**Created**: 2025-10-13
**Component Path**: `frontend/src/components/UserSearch.tsx`
**Page Path**: `frontend/src/pages/UserSearchPage.tsx`
**Status**: Ready for integration

## Features

### Search Filters
- **First Name**: Text input for searching by first name
- **Last Name**: Text input for searching by last name
- **Age**: Numeric input with validation (0-120)
- **Role Type**: Dropdown select with options:
  - All Roles (default)
  - Parent
  - Student
  - Admin
  - Zookeeper
  - Visitor
- **Number of Visits**: Numeric input for filtering by zoo visit count

### User Experience
- **Responsive Design**: Mobile-first design that adapts to all screen sizes
- **Accessibility**: Full ARIA labels, keyboard navigation, and semantic HTML
- **Loading States**: Visual feedback during API calls with spinner
- **Error Handling**: User-friendly error messages with context
- **Empty States**: Clear guidance when no results found or no search performed
- **Results Table**: Comprehensive user information display

### Results Display
The search results table includes:
- Name (with grade for students)
- Email address
- Role badge
- Age
- Number of visits
- Phone number
- Account creation date

## Backend API Integration

### Endpoint
```
GET /user
```

### Query Parameters
The component builds query parameters from active filters:

```typescript
{
  query: string        // Combined first name and last name
  age: string          // Numeric age value
  role: string         // Role type filter
  visits: string       // Number of visits filter
  page_size: string    // Results per page (default: 50)
}
```

### Expected Response Format
```typescript
interface PagedUsers {
  items: User[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

interface User {
  userId: string;
  email: string;
  displayName: string;
  role: 'parent' | 'student' | 'admin' | 'zookeeper' | 'visitor';
  phone?: string;
  age?: number;
  grade?: string;
  visits?: number;
  created?: {
    at: string;
  };
}
```

### Backend Requirements

**⚠️ IMPORTANT**: The backend `/user` endpoint must support the following:

1. **Query Parameter Combinations**: Accept multiple simultaneous filters
2. **Name Search**: Support searching by partial first/last name in `query` parameter
3. **Role Filtering**: Filter by user role type
4. **Age Filtering**: Filter by exact age or age range
5. **Visits Filtering**: Filter by number of zoo visits
6. **Pagination**: Support `page_size` parameter for result limiting

**Current Backend Status** (as of 2025-10-13):
- ✅ Basic `/user` endpoint exists
- ✅ Supports `query` and `role` parameters
- ⚠️ May need enhancement for `age` and `visits` parameters
- ⚠️ Verify PagedUsers response format matches backend implementation

### Backend Implementation Notes

If the backend doesn't fully support all filter parameters yet, refer to:
- `backend/api/openapi_spec.yaml` - OpenAPI specification for /user endpoint
- `backend/api/src/main/python/openapi_server/impl/handlers.py` - User search handler
- Consider adding query parameter support for age and visits filtering

## Installation & Integration

### Step 1: Add Route to Application

Edit `frontend/src/App.tsx` to add the UserSearch route:

```tsx
import UserSearchPage from './pages/UserSearchPage';

// In your routing configuration:
<Route path="/admin/user-search" element={<UserSearchPage />} />
// OR
<Route path="/users/search" element={<UserSearchPage />} />
```

### Step 2: Add Navigation Link

Add a navigation link in the appropriate menu (e.g., admin sidebar):

```tsx
import { Search } from 'lucide-react';

<NavLink to="/admin/user-search">
  <Search className="h-5 w-5 mr-2" />
  User Search
</NavLink>
```

### Step 3: Verify Dependencies

All required dependencies are already in package.json:
- ✅ `lucide-react` - Icons
- ✅ `react` - Framework
- ✅ `typescript` - Type checking
- ✅ Tailwind CSS - Styling

No additional installation needed!

## Usage Examples

### Basic Route Integration

```tsx
// In App.tsx or routing configuration
import UserSearchPage from './pages/UserSearchPage';

function App() {
  return (
    <Routes>
      {/* ... other routes ... */}
      <Route path="/admin/user-search" element={<UserSearchPage />} />
    </Routes>
  );
}
```

### Role-Based Access Control

```tsx
// In App.tsx with protected routes
import { useAuth } from './contexts/AuthContext';

function ProtectedUserSearch() {
  const { user } = useAuth();

  if (!user || user.role !== 'admin') {
    return <Navigate to="/dashboard" />;
  }

  return <UserSearchPage />;
}

// Then in routes:
<Route path="/admin/user-search" element={<ProtectedUserSearch />} />
```

### Dashboard Integration

Add a "User Search" card to the admin dashboard:

```tsx
// In Dashboard.tsx
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate('/admin/user-search')}
      className="p-4 bg-white border rounded-lg hover:shadow-md transition-shadow text-left"
    >
      <h3 className="font-medium text-gray-900 mb-2">Search Users</h3>
      <p className="text-sm text-gray-600">Find users by name, age, role, and visit history</p>
    </button>
  );
};
```

## Component Architecture

### File Structure
```
frontend/src/
├── components/
│   └── UserSearch.tsx        # Main search component
├── pages/
│   └── UserSearchPage.tsx    # Page wrapper
└── config/
    └── api.ts                # API configuration (already exists)
```

### Key Functions

#### `handleSearch()`
Executes user search with current filter values:
- Validates at least one filter is active
- Builds query parameters from filters
- Calls backend API
- Updates results state
- Handles errors gracefully

#### `handleClearFilters()`
Resets all filters and results to initial state:
- Clears all filter inputs
- Removes search results
- Resets error state
- Clears "has searched" flag

#### `handleFilterChange()`
Updates individual filter values:
- Type-safe field updates
- Clears error state on input
- Maintains other filter values

### State Management

```typescript
// Filter state
const [filters, setFilters] = useState<UserSearchFilters>({
  firstName: '',
  lastName: '',
  age: '',
  roleType: '',
  numberOfVisits: ''
});

// Results state
const [results, setResults] = useState<User[]>([]);
const [totalResults, setTotalResults] = useState(0);

// UI state
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [hasSearched, setHasSearched] = useState(false);
```

## Styling & Theming

### Color Scheme
- **Primary**: Green (`green-600`, `green-700`) - matches CMZ branding
- **Background**: Gray (`gray-50`) - page background
- **Cards**: White with shadow
- **Text**: Gray scale for hierarchy

### Responsive Breakpoints
- **Mobile**: < 768px - Single column layout
- **Tablet**: 768px - 1024px - Two column filters
- **Desktop**: > 1024px - Three column filters

### Tailwind Classes Used
Key utility classes for customization:
- `max-w-7xl` - Maximum content width
- `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3` - Responsive grid
- `focus:ring-green-500` - Focus states
- `hover:bg-gray-50` - Hover effects

## Accessibility Features

### ARIA Labels
- All form inputs have descriptive `aria-label` attributes
- Error messages use `role="alert"`
- Table headers use proper `scope` attributes

### Keyboard Navigation
- Tab order follows logical flow
- All interactive elements keyboard accessible
- Form submission on Enter key
- Clear button accessible via keyboard

### Screen Reader Support
- Semantic HTML structure
- Descriptive labels for all controls
- Loading state announcements
- Error message announcements

## Testing Recommendations

### Manual Testing Checklist
- [ ] Search with single filter (each type)
- [ ] Search with multiple filters combined
- [ ] Search with no filters (should show validation error)
- [ ] Clear filters functionality
- [ ] Responsive design on mobile, tablet, desktop
- [ ] Loading state visibility
- [ ] Error handling with backend down
- [ ] Empty results state display
- [ ] Table scrolling with many results
- [ ] Form submission on Enter key
- [ ] Keyboard navigation through all controls

### Test Users
Use existing test users from the CMZ database:
- `parent1@test.cmz.org` - Parent role
- `student1@test.cmz.org` - Student role
- `test@cmz.org` - Various roles

### Backend Testing
```bash
# Test API endpoint directly
curl -X GET "http://localhost:8080/user?query=Test&role=parent&page_size=10" \
  -H "Content-Type: application/json"

# Expected: JSON array of matching users
```

## Known Limitations

1. **Pagination**: Currently loads first 50 results only
   - Future enhancement: Add pagination controls
   - Consider adding infinite scroll

2. **Advanced Filters**: Limited to exact/basic matching
   - Future enhancement: Age ranges (18-25, 26-40, etc.)
   - Consider visit count ranges (0-5, 6-10, etc.)

3. **Export Functionality**: No CSV/Excel export
   - Future enhancement: Add export button for results

4. **Saved Searches**: Cannot save filter combinations
   - Future enhancement: Allow saving common searches

5. **Backend Dependency**: Assumes `/user` endpoint supports all parameters
   - Verify backend implementation matches requirements
   - May need backend updates for full functionality

## Troubleshooting

### Issue: "Search failed" error
**Cause**: Backend API not responding or CORS issue
**Solution**:
1. Verify backend is running: `curl http://localhost:8080/user`
2. Check CORS configuration in `backend/api/src/main/python/openapi_server/__main__.py`
3. Ensure `X-User-Id` header is allowed

### Issue: No results found when users exist
**Cause**: Backend filter parameters not implemented
**Solution**:
1. Check backend logs for filter parameter handling
2. Verify OpenAPI spec defines all query parameters
3. Update handler in `impl/handlers.py` to support filters

### Issue: Table not responsive on mobile
**Cause**: Wide table content
**Solution**: Already implemented with `overflow-x-auto` wrapper

### Issue: Component not found when importing
**Cause**: File path incorrect
**Solution**: Verify import path: `import UserSearch from '../components/UserSearch'`

## Future Enhancements

### High Priority
1. **Pagination Controls**: Add previous/next page navigation
2. **Results Per Page**: Allow user to select 10, 25, 50, 100 results
3. **Export to CSV**: Download search results as CSV file
4. **Backend Validation**: Verify all filter parameters supported

### Medium Priority
1. **Advanced Filters**: Age ranges, visit count ranges
2. **Saved Searches**: Save common filter combinations
3. **User Details Modal**: Click row to view full user details
4. **Bulk Actions**: Select multiple users for bulk operations
5. **Sort Options**: Sort results by name, date, visits, etc.

### Low Priority
1. **Search History**: Show recent searches
2. **Quick Filters**: Pre-defined filter buttons (e.g., "Active Students")
3. **Visual Charts**: Display search results statistics
4. **Print View**: Printer-friendly results format

## Related Documentation

- **Backend API**: `backend/api/openapi_spec.yaml`
- **User Handlers**: `backend/api/src/main/python/openapi_server/impl/handlers.py`
- **API Config**: `frontend/src/config/api.ts`
- **Auth Context**: `frontend/src/contexts/AuthContext.tsx`
- **Add Family Modal**: `frontend/src/components/AddFamilyModalV2.tsx` (similar search pattern)

## Support

For questions or issues:
1. Check this documentation first
2. Review backend API specification
3. Test API endpoint directly with curl
4. Verify frontend console for errors
5. Check backend logs for API errors

**Last Updated**: 2025-10-13
**Component Version**: 1.0.0
**Author**: Claude Code Assistant
