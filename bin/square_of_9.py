#!/usr/bin/env python3
"""
Gann Square of 9 calculator.

Given a base (pivot) price, computes the price levels at each 45-degree
step around the "square root spiral" for a number of outward rings.

Usage:
    python3 square_of_9.py <base_price> [--rings N]

Example:
    python3 square_of_9.py 100 --rings 2
"""

import argparse
import math


CARDINAL_ANGLES = {0, 90, 180, 270, 360}


def compute_levels(base_price: float, rings: int):
    """Return a list of (angle, price, kind) tuples for `rings` full rotations."""
    sqrt0 = math.sqrt(base_price)
    levels = []
    max_angle = 360 * rings
    angle = 0
    while angle <= max_angle:
        sqrt_theta = sqrt0 + (angle / 360.0) * 2
        price = sqrt_theta ** 2
        normalized_angle = angle % 360
        if normalized_angle in CARDINAL_ANGLES or normalized_angle == 0:
            kind = "cardinal (基本角)"
        else:
            kind = "ordinal (對角)"
        levels.append((angle, price, kind))
        angle += 45
    return levels


def compute_support_levels(base_price: float, rings: int):
    """Return descending price levels (support side), stopping if price would go non-positive."""
    sqrt0 = math.sqrt(base_price)
    levels = []
    max_angle = 360 * rings
    angle = 45
    while angle <= max_angle:
        sqrt_theta = sqrt0 - (angle / 360.0) * 2
        if sqrt_theta <= 0:
            break
        price = sqrt_theta ** 2
        normalized_angle = angle % 360
        kind = "cardinal (基本角)" if normalized_angle in CARDINAL_ANGLES else "ordinal (對角)"
        levels.append((angle, price, kind))
        angle += 45
    return levels


def main():
    parser = argparse.ArgumentParser(description="Gann Square of 9 calculator")
    parser.add_argument("base_price", type=float, help="基準（樞紐）價格")
    parser.add_argument("--rings", type=int, default=1, help="要往外計算幾圈（每圈 360 度），預設 1")
    args = parser.parse_args()

    print(f"基準價格 (0°): {args.base_price}")
    print()
    print("=== 壓力位（往上，價格 > 基準）===")
    print(f"{'角度':>6} | {'價位':>12} | 類型")
    print("-" * 40)
    for angle, price, kind in compute_levels(args.base_price, args.rings):
        if angle == 0:
            continue
        print(f"{angle:>5}° | {price:>12.2f} | {kind}")

    print()
    print("=== 支撐位（往下，價格 < 基準）===")
    print(f"{'角度':>6} | {'價位':>12} | 類型")
    print("-" * 40)
    support = compute_support_levels(args.base_price, args.rings)
    if not support:
        print("(基準價格過低，無法往下推算完整支撐位)")
    for angle, price, kind in support:
        print(f"{angle:>5}° | {price:>12.2f} | {kind}")


if __name__ == "__main__":
    main()
