#!/usr/bin/env python3
"""
Parse ENDPOINT-WORK.md to extract all implemented endpoints for testing
"""
import re
import json

def parse_endpoint_work():
    """Extract all implemented endpoints from ENDPOINT-WORK.md"""

    with open('/Users/keithstegbauer/repositories/CMZ-chatbots/ENDPOINT-WORK.md', 'r') as f:
        content = f.read()

    # Find the "IMPLEMENTED" section (between ## ✅ IMPLEMENTED and ## 🔧 IMPLEMENTED BUT FAILING)
    implemented_match = re.search(
        r'## ✅ IMPLEMENTED.*?(?=## 🔧 IMPLEMENTED BUT FAILING)',
        content,
        re.DOTALL
    )

    if not implemented_match:
        print("Could not find IMPLEMENTED section")
        return []

    implemented_section = implemented_match.group(0)

    # Extract endpoint patterns like "- **GET /path**" or "- **POST /path**"
    endpoint_pattern = r'-\s+\*\*([A-Z]+)\s+([/\w{}\-]+)\*\*(?:\s+-\s+(.+?)(?:\s+→\s+`(.+?)`)?(?:\s+\[(.+?)\])?)?$'

    endpoints = []
    for line in implemented_section.split('\n'):
        match = re.match(endpoint_pattern, line.strip())
        if match:
            method, path, description, handler, status = match.groups()
            endpoints.append({
                'method': method,
                'path': path,
                'description': description or '',
                'handler': handler or '',
                'status': status or '',
                'category': None  # Will be set based on section
            })

    # Categorize endpoints by section headers
    current_category = None
    categorized = []

    for line in implemented_section.split('\n'):
        # Check for category headers
        if line.startswith('### '):
            current_category = line.replace('###', '').strip()
        elif line.strip().startswith('- **'):
            match = re.match(endpoint_pattern, line.strip())
            if match:
                method, path, description, handler, status = match.groups()
                categorized.append({
                    'method': method,
                    'path': path,
                    'description': description or '',
                    'handler': handler or '',
                    'status': status or '',
                    'category': current_category
                })

    return categorized

def generate_test_plan(endpoints):
    """Generate test plan from endpoints"""

    # Group by category
    by_category = {}
    for ep in endpoints:
        cat = ep['category'] or 'Uncategorized'
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(ep)

    # Generate test plan
    test_plan = {
        'total_endpoints': len(endpoints),
        'categories': {}
    }

    for category, eps in by_category.items():
        test_plan['categories'][category] = {
            'count': len(eps),
            'endpoints': eps
        }

    return test_plan

if __name__ == '__main__':
    endpoints = parse_endpoint_work()
    test_plan = generate_test_plan(endpoints)

    # Save to JSON
    with open('validation-reports/val_20251010_123732/endpoint_test_plan.json', 'w') as f:
        json.dump(test_plan, f, indent=2)

    # Print summary
    print(f"✅ Parsed {test_plan['total_endpoints']} endpoints")
    print(f"\n📊 Categories:")
    for category, data in test_plan['categories'].items():
        print(f"  {category}: {data['count']} endpoints")

    print(f"\n📄 Test plan saved to: endpoint_test_plan.json")
