#!/usr/bin/env python3
"""Implement the complete build/solve/export/derive chain for one variant."""
import argparse

VARIANTS = ('unit_normal', 'unit_tm15', 'unit_tm30', 'unit_tm45', 'array_ms', 'array_pec', 'af_patterns')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', required=True, choices=VARIANTS)
    args = parser.parse_args()
    raise SystemExit(f'Incomplete starter: implement genuine HFSS reproduction for {args.variant}; read /home/paper/addendum.md')


if __name__ == '__main__':
    main()
