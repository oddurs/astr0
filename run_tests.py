#!/usr/bin/env python3
"""
astr0 Test Runner

A clean test runner with multiple output modes for the astr0 test suite.

Usage:
    python run_tests.py              # Quick run (default)
    python run_tests.py -v           # Verbose output  
    python run_tests.py --full       # Full output with coverage
    python run_tests.py --module time    # Run specific module tests
    python run_tests.py --failed     # Re-run failed tests only
"""

import subprocess
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="astr0 Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    Quick test run
  python run_tests.py -v                 Verbose output
  python run_tests.py --full             Full coverage report
  python run_tests.py --module sun       Test sun module only
  python run_tests.py --module precision Test precision module
  python run_tests.py -k "parse"         Run tests matching 'parse'
  python run_tests.py --failed           Re-run failed tests
  python run_tests.py --fast             Skip slow tests
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show verbose test output')
    parser.add_argument('--full', action='store_true',
                        help='Full run with coverage report')
    parser.add_argument('--module', '-m', type=str,
                        help='Run tests for specific module (e.g., time, sun, angles)')
    parser.add_argument('--failed', action='store_true',
                        help='Re-run only failed tests from last run')
    parser.add_argument('--fast', action='store_true',
                        help='Skip slow tests')
    parser.add_argument('-k', type=str,
                        help='Run tests matching expression')
    parser.add_argument('--watch', action='store_true',
                        help='Watch mode - re-run on file changes')
    parser.add_argument('extra', nargs='*',
                        help='Additional pytest arguments')
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Output mode
    if args.full:
        cmd.extend(['-v', '--cov=astr0', '--cov-report=term-missing', '--cov-report=html'])
        print_header("Full Test Run with Coverage")
    elif args.verbose:
        cmd.append('-v')
        print_header("Verbose Test Run")
    else:
        cmd.append('-q')
        print_header("Quick Test Run")
    
    # Test selection
    if args.module:
        module_path = find_module_tests(args.module)
        if module_path:
            cmd.append(str(module_path))
        else:
            print(f"Error: No tests found for module '{args.module}'")
            print(f"Available modules: {', '.join(list_modules())}")
            sys.exit(1)
    
    if args.failed:
        cmd.append('--lf')
    
    if args.fast:
        cmd.extend(['-m', 'not slow'])
    
    if args.k:
        cmd.extend(['-k', args.k])
    
    # Add extra arguments
    cmd.extend(args.extra)
    
    # Run tests
    print(f"  Command: {' '.join(cmd)}\n")
    print("─" * 60)
    
    result = subprocess.run(cmd)
    
    return result.returncode


def print_header(title: str):
    """Print a nice header."""
    print()
    print("╭" + "─" * 58 + "╮")
    print(f"│  ✦ {title:<53} │")
    print("╰" + "─" * 58 + "╯")
    print()


def find_module_tests(module: str) -> Path | None:
    """Find test file for a given module."""
    tests_dir = Path(__file__).parent / 'tests'
    
    # Check core modules
    core_test = tests_dir / 'core' / f'test_{module}.py'
    if core_test.exists():
        return core_test
    
    # Check CLI tests
    cli_test = tests_dir / 'cli' / f'test_{module}.py'
    if cli_test.exists():
        return cli_test
    
    # Check output tests
    output_test = tests_dir / 'output' / f'test_{module}.py'
    if output_test.exists():
        return output_test
    
    # Check for partial match
    for test_file in tests_dir.rglob('test_*.py'):
        if module.lower() in test_file.stem.lower():
            return test_file
    
    return None


def list_modules() -> list[str]:
    """List available test modules."""
    tests_dir = Path(__file__).parent / 'tests'
    modules = []
    
    for test_file in tests_dir.rglob('test_*.py'):
        name = test_file.stem.replace('test_', '')
        modules.append(name)
    
    return sorted(set(modules))


if __name__ == '__main__':
    sys.exit(main())
