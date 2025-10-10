#!/usr/bin/env python3
"""
Comprehensive code review using OpenAI API
Analyzes code for style, security, DRY, SOLID, and duplication

Usage:
    python openai_code_review.py --file path/to/file.py --focus style,security --output report.json

Environment Variables:
    OPENAI_API_KEY: Required OpenAI API key
"""

import argparse
import json
import os
import sys
from pathlib import Path
from openai import OpenAI
from openai.types.chat import ChatCompletion


def analyze_code(file_path: str, focus_areas: list[str], model: str = "gpt-4") -> dict:
    """
    Analyze a single code file using OpenAI API

    Args:
        file_path: Path to code file to analyze
        focus_areas: List of focus areas (style, security, dry, solid, react-best-practices)

    Returns:
        Dictionary with analysis results
    """
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key, timeout=60.0)

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        return {
            "file": file_path,
            "error": "File not found",
            "issues": []
        }
    except UnicodeDecodeError:
        return {
            "file": file_path,
            "error": "Unable to decode file (binary or non-UTF8)",
            "issues": []
        }

    # Build focus prompt
    focus_prompt = {
        'style': 'PEP 8 compliance, naming conventions, code organization, docstring completeness',
        'security': 'SQL injection, XSS, secrets exposure, authentication gaps, input validation',
        'dry': 'Code duplication, repeated patterns, missing abstractions, refactoring opportunities',
        'solid': 'Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion',
        'react-best-practices': 'Hooks usage, component structure, state management, performance optimization'
    }

    focus_text = '\n'.join([f"- {focus}: {focus_prompt.get(focus, focus)}" for focus in focus_areas])

    # Determine language
    ext = Path(file_path).suffix
    language_map = {
        '.py': 'python',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.js': 'javascript',
        '.jsx': 'javascript'
    }
    language = language_map.get(ext, 'unknown')

    prompt = f"""
You are a senior software engineer reviewing code for a production system.

Analyze the following code file and provide detailed findings for:
{focus_text}

For each issue found, provide:
1. Severity (CRITICAL, HIGH, MEDIUM, LOW)
2. Line number (if applicable)
3. Description of the issue
4. Recommended fix
5. Example of corrected code (if applicable)

Code File: {file_path}
Language: {language}

```{language}
{code}
```

Return your analysis as a JSON object with this structure:
{{
  "file": "{file_path}",
  "language": "{language}",
  "summary": "Brief overview of code quality",
  "issues": [
    {{
      "severity": "HIGH",
      "category": "security" or "style" or "dry" or "solid",
      "line": 42,
      "description": "Hardcoded secret in code",
      "recommendation": "Use environment variables",
      "example": "api_key = os.getenv('API_KEY')"
    }}
  ],
  "strengths": ["Well-documented functions", "Good error handling"],
  "metrics": {{
    "lines_of_code": 250,
    "complexity_estimate": "medium",
    "test_coverage": "unknown"
  }}
}}

IMPORTANT: Return ONLY valid JSON, no additional text.
"""

    try:
        response: ChatCompletion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a senior code reviewer focused on production quality. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except json.JSONDecodeError as e:
        # Fallback for malformed JSON
        return {
            "file": file_path,
            "language": language,
            "summary": f"Analysis completed with JSON parsing error: {e}",
            "issues": [],
            "error": f"JSON decode error: {e}"
        }
    except Exception as e:
        return {
            "file": file_path,
            "language": language,
            "summary": f"Analysis failed: {str(e)}",
            "issues": [],
            "error": str(e)
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='OpenAI Code Review',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single file for security and style
  python openai_code_review.py --file auth.py --focus security,style --output auth_review.json

  # Full analysis
  python openai_code_review.py --file module.py --focus style,security,dry,solid --output review.json
        """
    )
    parser.add_argument('--file', required=True, help='File to analyze')
    parser.add_argument('--focus', required=True, help='Comma-separated focus areas')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--model', default='gpt-4', help='OpenAI model to use (default: gpt-4, use gpt-3.5-turbo for cost savings)')

    args = parser.parse_args()

    # Validate API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='sk-...'", file=sys.stderr)
        sys.exit(1)

    # Parse focus areas
    focus_areas = [f.strip() for f in args.focus.split(',')]

    print(f"🔍 Analyzing {args.file} for: {', '.join(focus_areas)}")
    print(f"   Using model: {args.model}")

    # Analyze
    result = analyze_code(args.file, focus_areas, args.model)

    # Save result
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Analysis complete: {args.output}")

    # Print summary
    if 'error' in result:
        print(f"\n⚠️ Error: {result['error']}")
        return

    issues_by_severity = {}
    for issue in result.get('issues', []):
        severity = issue.get('severity', 'UNKNOWN')
        issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1

    print("\n📊 Issue Summary:")
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = issues_by_severity.get(severity, 0)
        if count > 0:
            emoji = {'CRITICAL': '🚨', 'HIGH': '⚠️', 'MEDIUM': '💡', 'LOW': 'ℹ️'}.get(severity, '•')
            print(f"  {emoji} {severity}: {count}")

    if not issues_by_severity:
        print("  ✅ No issues found!")

    # Print strengths
    if result.get('strengths'):
        print("\n💪 Strengths:")
        for strength in result['strengths'][:3]:  # Top 3
            print(f"  • {strength}")


if __name__ == '__main__':
    main()
