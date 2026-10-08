#!/usr/bin/env python3
"""Implement the complete build/solve/export/derive chain for one variant."""
import argparse

VARIANTS = ('te_00', 'te_30', 'te_60', 'te_86', 'tm_00', 'tm_30', 'tm_60', 'tm_83')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', required=True, choices=VARIANTS)
    args = parser.parse_args()
    raise SystemExit(f'Incomplete starter: implement genuine HFSS reproduction for {args.variant}; read /home/paper/addendum.md')


if __name__ == '__main__':
    main()
