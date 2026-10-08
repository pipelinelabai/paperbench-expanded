#!/usr/bin/env python3
"""Implement solver-free reconstruction from native exports, not paper values."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', required=True, type=Path)
    parser.add_argument('--check', action='store_true')
    parser.parse_args()
    raise SystemExit('Incomplete starter: implement all scored-file derivations from raw/; --check must compare without changing the submitted files')


if __name__ == '__main__':
    main()
