#!/usr/bin/env python3
"""
Launch script for StarT Translation Manager CLI
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from translation_cli import main
    main()
except ImportError as e:
    print(f"Error importing translation_cli: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error running translation CLI: {e}")
    sys.exit(1)
