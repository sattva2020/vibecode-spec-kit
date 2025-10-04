#!/usr/bin/env python3
"""
Memory Bank CLI - Entry Point
VS Code Memory Bank with Spec Kit Integration
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from cli.cli import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error: Failed to import CLI modules: {e}")
    print("Please ensure all required dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
