# PUBLIC-ANIMAL-PORTAL-ADVICE.md

## Best Practices and Lessons Learned for Public Animal Portal Implementation

### Role Detection Strategy

**Key Insight**: Role detection should happen at multiple layers for security and consistency.

**Implementation Priority**:
1. **JWT Claims** (Most Reliable): Backend sets role claim in JWT token during authentication
2. **User Object**: Store role in user profile from backend
3. **Email Pattern** (Fallback): Use email patterns as last resort
4. **Database Lookup** (Most Secure): Always verify role server-side

**Example JWT Payload**:
```json
{
  "sub": "user123",
  "email": "parent1@test.cmz.org",
  "role": "parent",
  "permissions": ["view_animals", "chat", "view_own_children"],
  "exp": 1234567890
}
```

### Common Pitfalls and Solutions

#### 1. Role Detection Failures
**Problem**: User gets wrong landing page due to incorrect role detection
**Solution**:
- Implement fallback chain: JWT → Database → Email Pattern → Default
- Add manual role override in user profile settings
- Log role detection for debugging

#### 2. Infinite Redirect Loops
**Problem**: Role-based routing causes redirect loops
**Solution**:
```typescript
// Prevent redirect loops
const [hasRedirected, setHasRedirected] = useState(false);

useEffect(() => {
  if (!hasRedirected && user && location.pathname === '/') {
    setHasRedirected(true);
    navigate(getRoleBasedPath(user.role));
  }
}, [user, hasRedirected]);
```

#### 3. Mixed Permissions
**Problem**: Parents who are also volunteers have multiple roles
**Solution**: Implement role hierarchy and primary role selection
```typescript
const roleHierarchy = ['admin', 'zookeeper', 'volunteer', 'parent', 'student', 'visitor'];
const primaryRole = user.roles
  .sort((a, b) => roleHierarchy.indexOf(a) - roleHierarchy.indexOf(b))[0];
```

### Mobile-First Design Requirements

**Critical for Zoo Visitors**:
- Many users will access via mobile at the zoo
- QR codes at exhibits need mobile-optimized pages
- Consider offline capability for poor connectivity areas

**Implementation**:
```css
/* Mobile-first breakpoints */
.animal-card {
  /* Mobile: Full width */
  width: 100%;

  /* Tablet: 2 columns */
  @media (min-width: 768px) {
    width: 50%;
  }

  /* Desktop: 3 columns */
  @media (min-width: 1024px) {
    width: 33.333%;
  }
}
```

### Performance Optimization Techniques

#### 1. Animal Data Caching
```typescript
// Use React Query or SWR for intelligent caching
const { data: animals } = useSWR('/api/animals', fetcher, {
  revalidateOnFocus: false,
  dedupingInterval: 60000, // 1 minute
  fallbackData: cachedAnimals
});
```

#### 2. Image Lazy Loading
```typescript
const AnimalImage = ({ src, alt }) => (
  <img
    loading="lazy"
    src={src}
    alt={alt}
    className="animal-image"
  />
);
```

#### 3. Virtual Scrolling for Large Lists
```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={animals.length}
  itemSize={200}
  width="100%"
>
  {({ index, style }) => (
    <AnimalCard style={style} animal={animals[index]} />
  )}
</FixedSizeList>
```

### Security Best Practices

#### 1. Never Trust Client-Side Role Checks
```typescript
// Bad: Client-side only
if (user.role === 'admin') {
  showAdminButton(); // Easily bypassed
}

// Good: Server validates every request
const response = await fetch('/api/admin/action', {
  headers: { Authorization: `Bearer ${token}` }
});
// Server checks token and role before proceeding
```

#### 2. Implement Route Guards
```typescript
const RequireRole = ({ roles, children }) => {
  const { user } = useAuth();
  const [authorized, setAuthorized] = useState(null);

  useEffect(() => {
    // Verify with backend
    fetch('/api/verify-role', {
      method: 'POST',
      body: JSON.stringify({ requiredRoles: roles })
    }).then(res => setAuthorized(res.ok));
  }, [roles]);

  if (authorized === false) return <AccessDenied />;
  if (authorized === null) return <Loading />;
  return children;
};
```

### Testing Strategies

#### 1. Role-Based Test Accounts
Create test accounts for each role:
- `visitor@test.cmz.org` - Basic access
- `student1@test.cmz.org` - Student features
- `parent1@test.cmz.org` - Parent dashboard
- `keeper@test.cmz.org` - Zookeeper tools
- `admin@test.cmz.org` - Full access

#### 2. Automated E2E Tests
```typescript
// Playwright test example
test.describe('Role-based routing', () => {
  test('visitor sees public animal list', async ({ page }) => {
    await loginAs(page, 'visitor@test.cmz.org');
    await expect(page).toHaveURL('/animals');
    await expect(page.locator('h1')).toContainText('Meet Our Animal Ambassadors');
  });

  test('admin sees dashboard', async ({ page }) => {
    await loginAs(page, 'admin@test.cmz.org');
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });
});
```

### Accessibility Considerations

**WCAG 2.1 AA Compliance**:
```typescript
const AnimalCard = ({ animal }) => (
  <article
    role="article"
    aria-labelledby={`animal-${animal.id}-name`}
  >
    <h3 id={`animal-${animal.id}-name`}>{animal.name}</h3>
    <button
      aria-label={`Chat with ${animal.name}`}
      onClick={startChat}
    >
      <MessageCircle aria-hidden="true" />
      <span>Chat</span>
    </button>
  </article>
);
```

### Gradual Rollout Strategy

**Phase 1**: Shadow Mode
- New portal exists at `/animals/new`
- Old dashboard remains default
- A/B test with small user group

**Phase 2**: Opt-in
- Users can choose preferred landing page
- Preference saved in user profile
- Gather feedback and iterate

**Phase 3**: Default Switch
- New portal becomes default
- Old dashboard still accessible
- Monitor metrics and issues

**Phase 4**: Full Migration
- Remove old routing logic
- Optimize based on usage patterns
- Document for future reference

### Monitoring and Analytics

Track key metrics:
```typescript
// Analytics events
const trackUserFlow = (event) => {
  analytics.track(event, {
    userRole: user.role,
    timestamp: new Date().toISOString(),
    sessionId: session.id,
    device: getDeviceType(),
    path: window.location.pathname
  });
};

// Track critical events
trackUserFlow('login_success');
trackUserFlow('animal_selected');
trackUserFlow('chat_started');
trackUserFlow('role_based_redirect');
```

### Error Recovery Patterns

```typescript
const PublicAnimalList = () => {
  const [error, setError] = useState(null);
  const [retries, setRetries] = useState(0);

  const fetchAnimals = async () => {
    try {
      const response = await fetch('/api/animals');
      if (!response.ok) throw new Error('Failed to load');
      const data = await response.json();
      setAnimals(data);
    } catch (err) {
      setError(err);
      if (retries < 3) {
        setTimeout(() => {
          setRetries(r => r + 1);
          fetchAnimals();
        }, 1000 * Math.pow(2, retries)); // Exponential backoff
      }
    }
  };

  if (error && retries >= 3) {
    return <ErrorFallback onRetry={() => {
      setRetries(0);
      fetchAnimals();
    }} />;
  }
};
```

### Database Considerations

**Optimize Animal Queries for Public View**:
```sql
-- Create index for active animals
CREATE INDEX idx_animals_active_status ON animals(status)
WHERE status = 'active';

-- Materialized view for public animal data
CREATE MATERIALIZED VIEW public_animals AS
SELECT
  animalId,
  name,
  species,
  personality,
  habitat,
  emoji,
  imageUrl
FROM animals
WHERE status = 'active'
WITH DATA;

REFRESH MATERIALIZED VIEW public_animals;
```

### Future-Proofing

**Extensibility Points**:
1. **Plugin System**: Allow zoo-specific customizations
2. **Theme Support**: Different zoos can brand their portals
3. **Feature Flags**: Enable/disable features per deployment
4. **API Versioning**: Support multiple frontend versions
5. **Internationalization**: Prepare for multi-language support

```typescript
// Feature flag example
const features = {
  enableFavorites: process.env.REACT_APP_ENABLE_FAVORITES === 'true',
  enableSearch: process.env.REACT_APP_ENABLE_SEARCH === 'true',
  enableCategories: process.env.REACT_APP_ENABLE_CATEGORIES === 'true'
};

{features.enableSearch && <SearchBar />}
{features.enableFavorites && <FavoritesButton />}
```

## Conclusion

The public animal portal with role-based routing transforms the CMZ platform from an admin-focused tool to a visitor-friendly experience. Key success factors:

1. **Reliable role detection** with multiple fallbacks
2. **Mobile-first design** for zoo visitors
3. **Performance optimization** for quick interactions
4. **Security-first approach** with server validation
5. **Gradual rollout** with monitoring
6. **Accessibility** for all users
7. **Error resilience** with graceful fallbacks

This implementation provides a foundation for engaging zoo visitors while maintaining administrative capabilities for staff.