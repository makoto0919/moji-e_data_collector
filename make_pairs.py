#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
import argparse

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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs_dir", default="refs", help="SVG directory (default: refs)")
    ap.add_argument("--out", default="data/pairs.json", help="Output path (default: data/pairs.json)")
    ap.add_argument("--svg_url_prefix", default="refs/", help="svgUrl prefix in pairs.json (default: refs/)")
    ap.add_argument("--pair_id_prefix", default="pair", help="pairId prefix (default: pair)")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON (bigger file)")
    args = ap.parse_args()

    refs_dir = Path(args.refs_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    svgs = sorted([p for p in refs_dir.glob("*.svg") if p.is_file()])
    if not svgs:
        raise SystemExit(f"No SVG files found in: {refs_dir.resolve()}")

    pairs = []
    svg_url_prefix = args.svg_url_prefix.rstrip("/") + "/"

    # 直積生成：全svg × 全ひらがな
    for svg in svgs:
        svg_url = svg_url_prefix + svg.name
        svg_stem = svg.stem

        for ch in HIRAGANA:
            # pairIdは必ず一意に（svg+char）
            # 例: pair__crab__あ
            pair_id = f"{args.pair_id_prefix}__{svg_stem}__{ch}"

            pairs.append({
                "pairId": pair_id,
                "char": ch,
                "svgUrl": svg_url
            })

    if args.pretty:
        text = json.dumps(pairs, ensure_ascii=False, indent=2)
    else:
        # サイズを抑えたいとき（おすすめ）
        text = json.dumps(pairs, ensure_ascii=False, separators=(",", ":"))

    out_path.write_text(text, encoding="utf-8")
    print(f"✅ wrote: {out_path}  pairs={len(pairs)}  svgs={len(svgs)}  chars={len(HIRAGANA)}")

if __name__ == "__main__":
    main()