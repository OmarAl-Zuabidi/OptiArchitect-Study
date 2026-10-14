"""Allows ``python -m optiarchitect`` (same as the ``optiarchitect`` command)."""
import sys

from optiarchitect.cli import main

if __name__ == "__main__":
    sys.exit(main())
