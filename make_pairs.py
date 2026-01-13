#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

HIRAGANA = list(
    "あいうえお"
    "かきくけこ"
    "さしすせそ"
    "たちつてと"
    "なにぬねの"
    "はひふへほ"
    "まみむめも"
    "やゆよ"
    "らりるれろ"
    "わをん"
    "がぎぐげご"
    "ざじずぜぞ"
    "だぢづでど"
    "ばびぶべぼ"
)

# ★ ここが絶対位置
SVG_BASE_URL = "https://makoto0919.github.io/moji-e_data_collector/refs/"

def main():
    refs_dir = Path("refs")
    out_path = Path("data/pairs.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    svgs = sorted(p for p in refs_dir.glob("*.svg") if p.is_file())
    if not svgs:
        raise SystemExit("No SVG files found in refs/")

    pairs = []

    for svg in svgs:
        svg_url = SVG_BASE_URL + svg.name
        stem = svg.stem

        for ch in HIRAGANA:
            pair_id = f"pair__{stem}__{ch}"
            pairs.append({
                "pairId": pair_id,
                "char": ch,
                "svgUrl": svg_url
            })

    out_path.write_text(
        json.dumps(pairs, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8"
    )

    print(f"✅ wrote {out_path}  pairs={len(pairs)}")

if __name__ == "__main__":
    main()