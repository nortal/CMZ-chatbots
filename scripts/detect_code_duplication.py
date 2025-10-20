#!/usr/bin/env python3
"""
Detect code duplication using OpenAI embeddings API
Generates similarity matrix and identifies refactoring candidates

Usage:
    python detect_code_duplication.py --paths backend/impl,frontend/src --threshold 0.85 --output dup.json

Environment Variables:
    OPENAI_API_KEY: Required OpenAI API key
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
import numpy as np


def extract_functions_python(file_path: str) -> List[Dict]:
    """Extract function definitions from Python files"""
    functions = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (FileNotFoundError, UnicodeDecodeError):
        return []

    current_function = None
    current_start = 0
    indent_level = 0

    for i, line in enumerate(lines, 1):
        # Detect function definition
        if re.match(r'^\s*(def|async def)\s+\w+', line):
            if current_function:
                # Save previous function
                functions.append({
                    'file': str(file_path),
                    'name': current_function,
                    'start_line': current_start,
                    'end_line': i - 1,
                    'code': ''.join(lines[current_start-1:i-1])
                })

            # Start new function
            match = re.match(r'^\s*(def|async def)\s+(\w+)', line)
            current_function = match.group(2) if match else 'unknown'
            current_start = i
            indent_level = len(line) - len(line.lstrip())

    # Add last function
    if current_function:
        functions.append({
            'file': str(file_path),
            'name': current_function,
            'start_line': current_start,
            'end_line': len(lines),
            'code': ''.join(lines[current_start-1:])
        })

    return functions


def extract_functions_typescript(file_path: str) -> List[Dict]:
    """Extract function definitions from TypeScript/JavaScript files"""
    functions = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        return []

    # Match various function patterns
    patterns = [
        r'function\s+(\w+)\s*\([^)]*\)\s*{',  # function name() {}
        r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',  # const name = () => {}
        r'(\w+)\s*:\s*\([^)]*\)\s*=>\s*{',  # name: () => {}
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            func_name = match.group(1)
            start_pos = match.start()
            line_num = content[:start_pos].count('\n') + 1

            # Extract function body (simplified - until matching brace)
            brace_count = 1
            pos = match.end()
            while pos < len(content) and brace_count > 0:
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                pos += 1

            func_code = content[match.start():pos]

            functions.append({
                'file': str(file_path),
                'name': func_name,
                'start_line': line_num,
                'end_line': line_num + func_code.count('\n'),
                'code': func_code
            })

    return functions


def should_skip_function(func: Dict) -> bool:
    """Skip functions that are expected to be similar"""
    skip_patterns = [
        'test_',           # Test functions
        '__init__',        # Constructors
        'get_',            # Simple getters
        'set_',            # Simple setters
        'serialize',       # Serialization methods
        'to_dict',         # Conversion methods
        'from_dict',       # Conversion methods
        '__str__',         # String representation
        '__repr__',        # Object representation
    ]

    func_name = func.get('name', '')
    return any(pattern in func_name for pattern in skip_patterns)


def get_embedding(client: OpenAI, text: str) -> List[float]:
    """Get embedding vector for code text"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # Limit input size
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"⚠️ Embedding error: {e}", file=sys.stderr)
        return []


def calculate_similarity(emb1: List[float], emb2: List[float]) -> float:
    """Calculate cosine similarity between embeddings"""
    if not emb1 or not emb2:
        return 0.0

    a = np.array(emb1)
    b = np.array(emb2)

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def detect_duplicates(paths: List[str], threshold: float = 0.85) -> Dict:
    """Detect duplicate code across files"""
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key, timeout=60.0)

    # Extract all functions
    all_functions = []
    for path in paths:
        path_obj = Path(path)

        if path_obj.is_file():
            # Single file
            files = [path_obj]
        else:
            # Directory - find all Python and TypeScript files
            files = list(path_obj.rglob('*.py')) + \
                    list(path_obj.rglob('*.ts')) + \
                    list(path_obj.rglob('*.tsx'))

        for file_path in files:
            # Skip test files for duplication detection
            if 'test' in str(file_path).lower():
                continue

            if file_path.suffix == '.py':
                functions = extract_functions_python(file_path)
            elif file_path.suffix in ['.ts', '.tsx']:
                functions = extract_functions_typescript(file_path)
            else:
                continue

            # Filter out functions to skip
            functions = [f for f in functions if not should_skip_function(f)]
            all_functions.extend(functions)

    print(f"📊 Found {len(all_functions)} functions to analyze")

    if len(all_functions) == 0:
        return {
            'total_functions': 0,
            'threshold': threshold,
            'duplicates_found': 0,
            'duplicates': []
        }

    # Generate embeddings
    print("🔄 Generating embeddings...")
    for i, func in enumerate(all_functions):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(all_functions)}")

        func['embedding'] = get_embedding(client, func['code'])

    # Find similar pairs
    print("🔍 Detecting duplicates...")
    duplicates = []

    for i in range(len(all_functions)):
        for j in range(i + 1, len(all_functions)):
            # Skip if same file
            if all_functions[i]['file'] == all_functions[j]['file']:
                continue

            similarity = calculate_similarity(
                all_functions[i]['embedding'],
                all_functions[j]['embedding']
            )

            if similarity >= threshold:
                duplicates.append({
                    'function1': {
                        'file': all_functions[i]['file'],
                        'name': all_functions[i]['name'],
                        'line': all_functions[i]['start_line']
                    },
                    'function2': {
                        'file': all_functions[j]['file'],
                        'name': all_functions[j]['name'],
                        'line': all_functions[j]['start_line']
                    },
                    'similarity': round(similarity, 3)
                })

    return {
        'total_functions': len(all_functions),
        'threshold': threshold,
        'duplicates_found': len(duplicates),
        'duplicates': sorted(duplicates, key=lambda x: x['similarity'], reverse=True)
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Detect code duplication using OpenAI embeddings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze backend implementation
  python detect_code_duplication.py --paths backend/api/src/main/python/openapi_server/impl --threshold 0.85 --output dup.json

  # Analyze multiple directories
  python detect_code_duplication.py --paths "backend/impl,frontend/src" --threshold 0.90 --output dup.json
        """
    )
    parser.add_argument('--paths', required=True, help='Comma-separated paths to analyze')
    parser.add_argument('--threshold', type=float, default=0.85, help='Similarity threshold (0-1), default 0.85')
    parser.add_argument('--output', required=True, help='Output JSON file')

    args = parser.parse_args()

    # Validate API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='sk-...'", file=sys.stderr)
        sys.exit(1)

    # Validate threshold
    if not 0 <= args.threshold <= 1:
        print(f"❌ Error: Threshold must be between 0 and 1, got {args.threshold}", file=sys.stderr)
        sys.exit(1)

    # Parse paths
    paths = [p.strip() for p in args.paths.split(',')]

    print(f"🔍 Detecting code duplication")
    print(f"   Paths: {', '.join(paths)}")
    print(f"   Threshold: {args.threshold}")

    # Detect duplicates
    result = detect_duplicates(paths, args.threshold)

    # Save result
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Duplication analysis complete: {args.output}")
    print(f"📊 Found {result['duplicates_found']} duplicate pairs from {result['total_functions']} functions")

    # Print top duplicates
    if result['duplicates_found'] > 0:
        print("\n🔍 Top 5 duplicates:")
        for dup in result['duplicates'][:5]:
            print(f"  {dup['similarity']:.1%} similarity:")
            print(f"    {dup['function1']['file']}:{dup['function1']['line']} - {dup['function1']['name']}")
            print(f"    {dup['function2']['file']}:{dup['function2']['line']} - {dup['function2']['name']}")
    else:
        print("\n✅ No significant code duplication found!")


if __name__ == '__main__':
    main()
