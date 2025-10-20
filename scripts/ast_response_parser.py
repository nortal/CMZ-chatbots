#!/usr/bin/env python3
"""
AST-based Response Field Parser
Enhances contract validation by using Python's AST module for accurate response field extraction
"""

import ast
from typing import Set, Dict, Any, List
from pathlib import Path


class ASTResponseParser:
    """Parse Python source code using AST to extract response fields accurately"""

    def __init__(self):
        self.response_fields = {}

    def extract_response_fields_from_handler(self, file_path: Path, handler_name: str) -> Set[str]:
        """
        Extract response fields from a handler function using AST parsing

        Args:
            file_path: Path to Python file containing handler
            handler_name: Name of the handler function

        Returns:
            Set of field names that appear in response dictionaries
        """
        try:
            with open(file_path) as f:
                source = f.read()

            tree = ast.parse(source)

            # Find the handler function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == handler_name:
                    return self._extract_dict_keys_from_function(node)

            return set()

        except (SyntaxError, FileNotFoundError) as e:
            print(f"⚠️ Could not parse {file_path}: {e}")
            return set()

    def _extract_dict_keys_from_function(self, func_node: ast.FunctionDef) -> Set[str]:
        """Extract all dictionary keys from a function body"""
        fields = set()

        for node in ast.walk(func_node):
            # Look for dictionary literals: {'key': value}
            if isinstance(node, ast.Dict):
                for key in node.keys:
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        fields.add(key.value)
                    elif isinstance(key, ast.Str):  # Python < 3.8 compatibility
                        fields.add(key.s)

            # Look for dict() constructor calls: dict(key=value)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'dict':
                    for keyword in node.keywords:
                        if keyword.arg:
                            fields.add(keyword.arg)

        return fields

    def analyze_return_statement_structure(self, file_path: Path, handler_name: str) -> Dict[str, Any]:
        """
        Deep analysis of return statement structure including nested fields

        Returns:
            Dictionary with 'fields', 'nested_fields', and 'return_type' information
        """
        try:
            with open(file_path) as f:
                source = f.read()

            tree = ast.parse(source)

            # Find the handler function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == handler_name:
                    return self._analyze_returns(node)

            return {'fields': set(), 'nested_fields': {}, 'return_type': 'unknown'}

        except (SyntaxError, FileNotFoundError) as e:
            return {'fields': set(), 'nested_fields': {}, 'return_type': 'error'}

    def _analyze_returns(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze all return statements in a function"""
        all_fields = set()
        nested_fields = {}
        return_types = []

        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value:
                # Check if returning a tuple (dict, status_code)
                if isinstance(node.value, ast.Tuple) and len(node.value.elts) >= 1:
                    # First element is the response dict
                    response = node.value.elts[0]
                    fields, nested = self._extract_fields_recursive(response)
                    all_fields.update(fields)
                    nested_fields.update(nested)
                    return_types.append('tuple')

                # Direct dict return
                elif isinstance(node.value, ast.Dict):
                    fields, nested = self._extract_fields_recursive(node.value)
                    all_fields.update(fields)
                    nested_fields.update(nested)
                    return_types.append('dict')

        return {
            'fields': all_fields,
            'nested_fields': nested_fields,
            'return_type': return_types[0] if return_types else 'none'
        }

    def _extract_fields_recursive(self, node: ast.AST, prefix: str = '') -> tuple:
        """Recursively extract fields including nested structures"""
        fields = set()
        nested = {}

        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    field_name = key.value
                    full_name = f"{prefix}.{field_name}" if prefix else field_name
                    fields.add(field_name)

                    # Check if value is nested dict
                    if isinstance(value, ast.Dict):
                        nested_fields, sub_nested = self._extract_fields_recursive(value, full_name)
                        nested[field_name] = nested_fields
                        nested.update(sub_nested)

        return fields, nested


def enhance_scanner_with_ast(api_dir: Path) -> Dict[str, Set[str]]:
    """
    Enhance contract scanner with AST-based response field extraction

    Args:
        api_dir: Path to API implementation directory

    Returns:
        Dictionary mapping handler names to their response fields
    """
    parser = ASTResponseParser()
    results = {}

    impl_files = list(api_dir.rglob('*.py'))

    # Add handlers.py explicitly
    handlers_file = api_dir / 'handlers.py'
    if handlers_file.exists() and handlers_file not in impl_files:
        impl_files.append(handlers_file)

    print(f"📊 Analyzing {len(impl_files)} Python files with AST parsing...")

    for file_path in impl_files:
        try:
            with open(file_path) as f:
                source = f.read()

            tree = ast.parse(source)

            # Find all handler functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    if func_name.startswith('handle_') or any(
                        func_name.endswith(suffix) for suffix in ['_post', '_get', '_put', '_patch', '_delete']
                    ):
                        fields = parser.extract_response_fields_from_handler(file_path, func_name)
                        if fields:
                            results[func_name] = fields

        except SyntaxError:
            # Skip files with syntax errors
            continue

    print(f"  Found {len(results)} handlers with AST-parsed response fields")
    return results


# Example usage for testing
if __name__ == '__main__':
    from pathlib import Path
    import sys

    if len(sys.argv) > 1:
        api_dir = Path(sys.argv[1])
    else:
        # Default to project structure
        api_dir = Path(__file__).parent.parent / 'backend' / 'api' / 'src' / 'main' / 'python' / 'openapi_server' / 'impl'

    if not api_dir.exists():
        print(f"❌ Directory not found: {api_dir}")
        sys.exit(1)

    results = enhance_scanner_with_ast(api_dir)

    print(f"\n📋 AST Analysis Results:")
    for handler, fields in sorted(results.items()):
        print(f"  {handler}: {', '.join(sorted(fields)) if fields else 'none'}")
