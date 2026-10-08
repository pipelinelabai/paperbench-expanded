#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from grader import evaluate
if __name__ == "__main__":
    evaluate("dual-passband-angular-stable-fss", evidence_task_name="03-dual-passband-angular-stable-fss")
