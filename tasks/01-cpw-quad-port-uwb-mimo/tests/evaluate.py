#!/usr/bin/env python3
# /// script
# dependencies = ["anthropic>=0.75.0", "numpy>=1.24.0", "scipy>=1.10.0"]
# ///
"""Thin wrapper; grading logic lives in src/grader.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from grader import evaluate

if __name__ == "__main__":
    evaluate("cpw-quad-port-uwb-mimo", evidence_task_name="01-cpw-quad-port-uwb-mimo")
