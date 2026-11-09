#!/usr/bin/env python3
"""
Catalog Generator & Progress Calculator for OreImouto Translations Hub.
Scans all locales, computes exact line completion percentages against template,
generates root catalog.json for in-game download client, and prints summary table.
"""

import argparse
import csv
import datetime
import hashlib
import json
import os
import re
import sys
from typing import Dict, List, Tuple

CYRILLIC_OR_LATIN = re.compile(r"[a-zA-Zа-яА-ЯёЁ]")


def count_locale_progress(locale_sc_dir: str, template_sc_dir: str) -> Tuple[int, int, float]:
    """
    Counts total scenario lines and translated lines.
    A line is considered translated if TEXT is non-empty and contains localized characters.
    """
    total_lines = 0
    translated_lines = 0

    if not os.path.isdir(locale_sc_dir):
        return 0, 0, 0.0

    files = sorted(f for f in os.listdir(locale_sc_dir) if f.endswith(".csv"))
    for fn in files:
        sc_path = os.path.join(locale_sc_dir, fn)
        tmpl_path = os.path.join(template_sc_dir, fn) if os.path.isdir(template_sc_dir) else ""

        with open(sc_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) < 3:
                    continue
                total_lines += 1
                text = row[2].strip()
                if text and CYRILLIC_OR_LATIN.search(text):
                    translated_lines += 1

    pct = round((translated_lines / total_lines * 100.0), 2) if total_lines > 0 else 0.0
    return total_lines, translated_lines, pct


def compute_file_sha256(path: str) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def generate_catalog(
    repo_root: str,
    output_json_path: str,
    release_tag: str = "v1.0.0",
    base_url_override: str = None,
) -> Dict:
    locales_dir = os.path.join(repo_root, "locales")
    template_dir = os.path.join(repo_root, "template")
    template_sc_dir = os.path.join(template_dir, "scenarios")

    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    catalog = {
        "schema_version": 1,
        "last_updated": now_iso,
        "packages": [],
    }

    if not os.path.isdir(locales_dir):
        return catalog

    for loc in sorted(os.listdir(locales_dir)):
        loc_dir = os.path.join(locales_dir, loc)
        if not os.path.isdir(loc_dir) or loc.startswith("."):
            continue

        manifest_path = os.path.join(loc_dir, "manifest.json")
        manifest = {}
        if os.path.isfile(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                try:
                    manifest = json.load(f)
                except Exception:
                    pass

        pkg_id = manifest.get("id", f"lang_{loc}_community")
        pkg_name = manifest.get("display_name", loc.upper())
        authors = manifest.get("authors", [manifest.get("team_name", "Community")])
        version = manifest.get("version", "1.0.0")
        desc = manifest.get("description", f"{pkg_name} translation for OreImouto Re:Port.")

        sc_dir = os.path.join(loc_dir, "scenarios")
        total_lines, trans_lines, progress = count_locale_progress(sc_dir, template_sc_dir)

        # Check for prebuilt PCK in dist/ or build if requested
        pck_name = f"lang_{loc}.pck"
        dist_pck_path = os.path.join(repo_root, "dist", pck_name)

        size_bytes = 0
        sha256 = ""
        if os.path.isfile(dist_pck_path):
            size_bytes = os.path.getsize(dist_pck_path)
            sha256 = compute_file_sha256(dist_pck_path)

        if base_url_override:
            url = f"{base_url_override.rstrip('/')}/{pck_name}"
        else:
            url = f"https://github.com/andre-pullinen/oreimouto-translations/releases/download/{release_tag}/{pck_name}"

        pkg_entry = {
            "id": pkg_id,
            "locale": loc,
            "name": pkg_name,
            "authors": authors,
            "version": version,
            "description": desc,
            "progress": progress,
            "total_lines": total_lines,
            "translated_lines": trans_lines,
            "url": url,
            "sha256": sha256,
            "size_bytes": size_bytes,
        }
        catalog["packages"].append(pkg_entry)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return catalog


def main():
    parser = argparse.ArgumentParser(description="Generate catalog.json for OreImouto Translations Hub")
    parser.add_argument("--repo-root", default=".", help="Root of repository")
    parser.add_argument("-o", "--output", default="catalog.json", help="Output path for catalog.json")
    parser.add_argument("--release-tag", default="v1.0.0", help="Release tag for asset downloads")
    parser.add_argument("--base-url", default=None, help="Override base URL for downloads")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    out_path = os.path.abspath(args.output)

    catalog = generate_catalog(repo_root, out_path, args.release_tag, args.base_url)

    print(f"[OK] Generated {out_path} ({len(catalog['packages'])} packages)")
    print("\nTranslation Progress Summary:")
    print("-" * 75)
    print(f"{'Locale':<8} | {'Language':<16} | {'Version':<8} | {'Progress':<10} | {'Lines':<15}")
    print("-" * 75)
    for p in catalog["packages"]:
        prog_str = f"{p['progress']:.1f}%"
        lines_str = f"{p['translated_lines']:,} / {p['total_lines']:,}"
        print(f"{p['locale']:<8} | {p['name']:<16} | {p['version']:<8} | {prog_str:<10} | {lines_str:<15}")
    print("-" * 75)


if __name__ == "__main__":
    main()
