# Call Graph Analysis for Contract Validation

**Purpose**: Improve scanner accuracy by following function delegation chains

**Problem**: Current scanner can't follow delegation patterns like `handle_auth_post() → handle_login_post()`

---

## The Challenge

### Example Delegation Pattern

```python
# In auth_controller.py (generated)
def handle_auth_post(body: Any) -> Tuple[Any, int]:
    # Delegates to actual implementation
    return handle_login_post(body)

# In handlers.py (implementation)
def handle_login_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    # Actual implementation
    email = body.get('username') or body.get('email')
    password = body.get('password')
    return authenticate_user(email, password)
```

**Current Scanner Behavior**: Reports "API Impl: none" for `handle_auth_post` because it doesn't see field extraction

**Desired Behavior**: Follow delegation to `handle_login_post` and report actual fields used

---

## Solution Approach

### Option 1: Static Call Graph with AST (Recommended)

**Advantages**:
- Pure Python, no external dependencies
- Accurate for simple delegation
- Fast performance

**Implementation**:

```python
import ast
from typing import Dict, Set, List

class CallGraphAnalyzer:
    """Build call graph from Python source using AST"""

    def __init__(self, impl_dir: Path):
        self.impl_dir = impl_dir
        self.call_graph = {}  # func_name → [called_funcs]

    def build_call_graph(self) -> Dict[str, List[str]]:
        """Build call graph for all Python files in impl directory"""

        for file_path in self.impl_dir.rglob('*.py'):
            with open(file_path) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    caller = node.name
                    callees = []

                    # Find function calls within this function
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                callees.append(child.func.id)

                    self.call_graph[caller] = callees

        return self.call_graph

    def follow_delegation(self, func_name: str, max_depth: int = 3) -> List[str]:
        """Follow delegation chain from func_name"""
        visited = set()
        chain = []

        def traverse(current, depth):
            if depth > max_depth or current in visited:
                return
            visited.add(current)
            chain.append(current)

            for callee in self.call_graph.get(current, []):
                traverse(callee, depth + 1)

        traverse(func_name, 0)
        return chain
```

**Usage in Scanner**:

```python
# In validate_contracts.py

def scan_api_handlers(self):
    # 1. Build call graph first
    analyzer = CallGraphAnalyzer(Path(self.api_dir))
    call_graph = analyzer.build_call_graph()

    # 2. For each handler, follow delegation
    for handler_name in detected_handlers:
        delegation_chain = analyzer.follow_delegation(handler_name)

        # 3. Aggregate fields from all functions in chain
        all_request_fields = set()
        all_response_fields = set()

        for func in delegation_chain:
            fields = self.extract_fields_from_function(func)
            all_request_fields.update(fields['request'])
            all_response_fields.update(fields['response'])

        self.api_contracts[handler_name] = {
            'request_fields': all_request_fields,
            'response_fields': all_response_fields,
            'delegation_chain': delegation_chain
        }
```

---

### Option 2: Dynamic Analysis with Import Tracing

**Advantages**:
- Handles dynamic calls
- Can detect runtime behavior

**Disadvantages**:
- Requires executing code (security risk)
- Slower performance
- Complex setup

**Not Recommended** for contract validation use case

---

### Option 3: Hybrid Approach (Medium Complexity)

Combine static AST analysis with limited pattern matching:

1. **AST for direct calls**: `return handle_login_post(body)`
2. **Pattern matching for common idioms**: `handler = create_handler(); handler.method()`
3. **Explicit delegation markers**: Detect comments like `# Delegates to: handle_login_post`

---

## Implementation Priority

### Phase 1 (Week 4, Days 1-2)
✅ Implement basic AST call graph builder
✅ Add delegation chain following (max depth 3)
✅ Integrate with existing scanner

### Phase 2 (Week 4, Days 3-4)
✅ Handle method calls on objects (`self.method()`, `handler.method()`)
✅ Add caching for performance
✅ Test on real codebase delegation patterns

### Phase 3 (Future Enhancement)
⚠️ Cross-file analysis (imports)
⚠️ Dynamic dispatch resolution
⚠️ Visualization of call graphs

---

## Testing Strategy

### Unit Tests

```python
def test_simple_delegation():
    source = '''
def handle_auth_post(body):
    return handle_login_post(body)

def handle_login_post(body):
    email = body.get('email')
    return {'token': email}
'''
    analyzer = CallGraphAnalyzer()
    graph = analyzer.parse_source(source)

    assert 'handle_auth_post' in graph
    assert 'handle_login_post' in graph['handle_auth_post']

def test_delegation_chain():
    # Test multi-level delegation (A → B → C)
    ...

def test_circular_delegation():
    # Ensure max_depth prevents infinite loops
    ...
```

### Integration Tests

```bash
# Run on actual codebase
python3 scripts/validate_contracts.py --enable-call-graph

# Should show delegation chains in output:
# handle_auth_post → handle_login_post
#   Request fields: username, password (from handle_login_post)
```

---

## Performance Considerations

### Optimization 1: Cache Call Graph
Build call graph once, reuse for all validations:

```python
# Cache call graph to file
import pickle

graph_cache = Path('validation-reports/.call_graph_cache.pkl')

if graph_cache.exists():
    with open(graph_cache, 'rb') as f:
        call_graph = pickle.load(f)
else:
    analyzer = CallGraphAnalyzer()
    call_graph = analyzer.build_call_graph()
    with open(graph_cache, 'wb') as f:
        pickle.dump(call_graph, f)
```

### Optimization 2: Incremental Analysis
Only rebuild call graph for modified files:

```python
def get_modified_files(since_timestamp):
    # Use git to find modified files
    result = subprocess.run(['git', 'diff', '--name-only', since_timestamp], ...)
    return result.stdout.decode().split('\n')

# Only re-analyze modified files
for file in get_modified_files(last_scan_time):
    analyzer.update_for_file(file)
```

### Performance Targets

- **Call graph build**: < 2 seconds for 100 files
- **Delegation follow**: < 100ms per handler
- **Total scanner overhead**: < 20% increase

---

## False Positive Reduction

### Before Call Graph Analysis

```
POST /auth
├─ OpenAPI: [username, password]
├─ Frontend: [username, password]
└─ Backend: [none]  ← WRONG! Scanner missed delegation
```

**False Positive**: 85% of "API Impl: none" warnings

### After Call Graph Analysis

```
POST /auth
├─ OpenAPI: [username, password]
├─ Frontend: [username, password]
└─ Backend: [username, password] (via delegation: handle_auth_post → handle_login_post)
```

**Expected Improvement**: Reduce false positives from 85% to < 20%

---

## Limitations & Known Issues

### Limitation 1: Dynamic Dispatch
```python
# Call graph can't resolve this statically
method_name = 'handle_' + operation
handler = getattr(self, method_name)
return handler(body)
```

**Mitigation**: Add explicit delegation markers or use naming conventions

### Limitation 2: Cross-Module Imports
```python
# Requires import resolution
from other_module import handle_login
return handle_login(body)
```

**Mitigation**: Phase 3 enhancement for import tracking

### Limitation 3: Conditional Delegation
```python
if condition:
    return handle_login_post(body)
else:
    return handle_register_post(body)
```

**Mitigation**: Follow all branches, aggregate fields

---

## Implementation Checklist

### Code Changes
- [ ] Create `scripts/call_graph_analyzer.py`
- [ ] Add `CallGraphAnalyzer` class with AST parsing
- [ ] Integrate into `validate_contracts.py`
- [ ] Add `--enable-call-graph` CLI flag
- [ ] Update report to show delegation chains

### Testing
- [ ] Unit tests for call graph building
- [ ] Unit tests for delegation following
- [ ] Integration test on real codebase
- [ ] Performance benchmarking

### Documentation
- [ ] Update VALIDATE-CONTRACTS-ADVICE.md
- [ ] Add examples to README
- [ ] Document CLI flags

---

## Success Metrics

### Baseline (Current Scanner)
- False positive rate: 85%
- Scanner accuracy: 15%
- Developer trust: Low

### Target (With Call Graph Analysis)
- False positive rate: < 20%
- Scanner accuracy: > 80%
- Developer trust: High

### Validation
- Compare scanner results before/after on known-working endpoints
- Measure reduction in "API Impl: none" false warnings
- Track developer feedback on validation reports

---

**Last Updated**: 2025-10-11
**Status**: 📋 Documented - Ready for Implementation
**Next Steps**: Implement Phase 1 in Week 4
