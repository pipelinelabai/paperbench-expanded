#!/usr/bin/env python3
"""Implement the complete build/solve/export/derive chain for one variant."""
import argparse

VARIANTS = ('mimo_final', 'single_initial', 'single_stub', 'h2_10p7', 'h2_11p7', 'mimo_nostub')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', required=True, choices=VARIANTS)
    args = parser.parse_args()
    raise SystemExit(f'Incomplete starter: implement genuine HFSS reproduction for {args.variant}; read /home/paper/addendum.md')


if __name__ == '__main__':
    main()
