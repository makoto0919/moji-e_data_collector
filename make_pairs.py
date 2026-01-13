#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
from pathlib import Path

# 対象ひらがな（ユーザー提示）
HIRAGANA = list("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼ")

# ファイル名に含まれる最初のひらがな（上記集合内）を拾う
HIRAGANA_SET = set(HIRAGANA)

def infer_char_from_filename(name: str) -> str | None:
    # 例: pair_あ_0001.svg / あ_012.svg / さ-shape.svg など
    for ch in name:
        if ch in HIRAGANA_SET:
            return ch
    return None

def read_mapping_file(mapping_path: Path) -> dict[str, str]:
    """
    TSV/CSV対応（1行: filename<TAB or ,>char）
    例:
      pair_000001.svg,あ
      pair_000002.svg\tい
    """
    m: dict[str, str] = {}
    if not mapping_path.exists():
        raise FileNotFoundError(f"mapping file not found: {mapping_path}")
    for line in mapping_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" in line:
            fn, ch = line.split("\t", 1)
        elif "," in line:
            fn, ch = line.split(",", 1)
        else:
            raise ValueError(f"mapping line must contain tab or comma: {line}")
        fn, ch = fn.strip(), ch.strip()
        if ch not in HIRAGANA_SET:
            raise ValueError(f"invalid hiragana in mapping: {ch} (line: {line})")
        m[fn] = ch
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs_dir", default="refs", help="SVG directory (default: refs)")
    ap.add_argument("--out", default="data/pairs.json", help="Output JSON path (default: data/pairs.json)")
    ap.add_argument("--svg_url_prefix", default="refs/", help="Prefix used in pairs.json svgUrl (default: refs/)")
    ap.add_argument("--pair_id_prefix", default="pair_", help="pairId prefix (default: pair_)")
    ap.add_argument("--mapping", default="", help="Optional mapping TSV/CSV: filename<tab or ,>hiragana")
    ap.add_argument("--strict", action="store_true", help="Fail if char cannot be inferred and no mapping entry")
    args = ap.parse_args()

    refs_dir = Path(args.refs_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    mapping = {}
    if args.mapping:
        mapping = read_mapping_file(Path(args.mapping))

    svgs = sorted([p for p in refs_dir.glob("*.svg") if p.is_file()])
    if not svgs:
        raise SystemExit(f"No SVG files found in: {refs_dir.resolve()}")

    pairs = []
    missing = []

    for i, p in enumerate(svgs, start=1):
        filename = p.name

        ch = infer_char_from_filename(filename)
        if ch is None and filename in mapping:
            ch = mapping[filename]

        if ch is None:
            missing.append(filename)
            if args.strict:
                continue
            # strictでない場合は、とりあえず "?" にして後から埋められるようにする
            ch = "?"

        pair_id = f"{args.pair_id_prefix}{p.stem}"  # pair_<stem>
        svg_url = args.svg_url_prefix.rstrip("/") + "/" + filename

        pairs.append({
            "pairId": pair_id,
            "char": ch,
            "svgUrl": svg_url
        })

    # strictモードで欠損がある場合は止める
    if args.strict and missing:
        msg = (
            "Some SVG filenames do not include a recognizable hiragana and are not in mapping.\n"
            "Add them to mapping file or rename them.\n"
            f"Missing ({len(missing)}):\n  " + "\n  ".join(missing[:50]) +
            ("\n  ..." if len(missing) > 50 else "")
        )
        raise SystemExit(msg)

    out_path.write_text(json.dumps(pairs, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ wrote: {out_path}  (count={len(pairs)})")
    if missing:
        print(f"⚠️ char推定できないファイルが {len(missing)} 件あります（char='?' で出力）:")
        for fn in missing[:50]:
            print("  -", fn)
        if len(missing) > 50:
            print("  ...")

if __name__ == "__main__":
    main()
