#!/usr/bin/env python3
"""
Validation Tool for OreImouto Translation Packs.
Verifies syntax, UTF-8 encoding (no BOM), canonical speaker IDs, scenario row alignment, and manifest schema.
"""

import argparse
import csv
import json
import os
import sys
from typing import Dict, List, Set, Tuple

REQUIRED_MANIFEST_KEYS = {"id", "locale", "name", "short", "version", "description", "team", "translators"}
REQUIRED_ROOT_CSVS = {
    "speakers.csv": ["SPEAKER_ID", "NAME"],
    "scene_titles.csv": ["SCENE_ID", "TITLE"],
    "toasts.csv": ["TOAST_KEY", "TEXT"],
    "ores.csv": ["ORE_ID", "TITLE", "DESCRIPTION"],
    "osis.csv": ["KEY", "STYLE", "TEXT"],
    "bgm.csv": ["TRACK_ID", "TITLE"],
    "ui.csv": ["KEY", "TEXT"],
}
SCENARIO_COLUMNS = ["ID", "SPEAKER", "TEXT"]


class ValidationError:
    def __init__(self, file_path: str, message: str, line_num: int = None):
        self.file_path = file_path
        self.message = message
        self.line_num = line_num

    def __str__(self):
        if self.line_num is not None:
            return f"  [ERROR] {self.file_path}:{self.line_num} -> {self.message}"
        return f"  [ERROR] {self.file_path} -> {self.message}"


def check_file_encoding(path: str) -> List[ValidationError]:
    errors = []
    try:
        with open(path, "rb") as f:
            raw = f.read(3)
            if raw == b"\xef\xbb\xbf":
                errors.append(ValidationError(path, "File has UTF-8 BOM, standard UTF-8 without BOM required."))
        with open(path, "r", encoding="utf-8") as f:
            f.read()
    except UnicodeDecodeError as e:
        errors.append(ValidationError(path, f"Invalid UTF-8 encoding: {e}"))
    except Exception as e:
        errors.append(ValidationError(path, f"Failed to read file: {e}"))
    return errors


def load_canonical_speakers(template_speakers_path: str) -> Set[str]:
    canonical = set()
    if not os.path.isfile(template_speakers_path):
        return canonical
    with open(template_speakers_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if row and row[0].strip():
                canonical.add(row[0].strip())
    return canonical


def validate_manifest_json(path: str, expected_locale: str) -> List[ValidationError]:
    errors = check_file_encoding(path)
    if errors:
        return errors

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [ValidationError(path, f"JSON parse error: {e}")]

    for k in REQUIRED_MANIFEST_KEYS:
        if k not in data or data[k] is None or data[k] == "":
            errors.append(ValidationError(path, f"Missing or empty required manifest field: '{k}'"))

    translators = data.get("translators")
    if translators is not None and not isinstance(translators, list):
        errors.append(ValidationError(path, f"Field 'translators' must be a list of strings"))

    tags = data.get("tags")
    if tags is not None and not isinstance(tags, (dict, list)):
        errors.append(ValidationError(path, f"Field 'tags' must be a dictionary or list"))

    fonts = data.get("fonts")
    if fonts is not None and not isinstance(fonts, dict):
        errors.append(ValidationError(path, f"Field 'fonts' must be a dictionary"))

    links = data.get("links")
    if links is not None and not isinstance(links, dict):
        errors.append(ValidationError(path, f"Field 'links' must be a dictionary"))

    loc = data.get("locale", "").strip().lower()
    if loc != expected_locale and not loc.startswith(expected_locale + "_") and not loc.startswith(expected_locale + "-"):
        errors.append(ValidationError(path, f"Locale in manifest ('{loc}') does not match directory ('{expected_locale}')"))

    return errors


def validate_csv_table(path: str, expected_header: List[str]) -> Tuple[List[ValidationError], List[List[str]]]:
    errors = check_file_encoding(path)
    rows = []
    if errors:
        return errors, rows

    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                errors.append(ValidationError(path, "File is completely empty"))
                return errors, rows

            clean_header = [h.strip() for h in header]
            if clean_header != expected_header:
                errors.append(
                    ValidationError(
                        path,
                        f"Invalid CSV header: expected {expected_header}, got {clean_header}",
                        1,
                    )
                )

            for line_idx, r in enumerate(reader, start=2):
                if len(r) != len(expected_header):
                    errors.append(
                        ValidationError(
                            path,
                            f"Column count mismatch: expected {len(expected_header)}, got {len(r)}",
                            line_idx,
                        )
                    )
                rows.append(r)
    except Exception as e:
        errors.append(ValidationError(path, f"CSV parsing failed: {e}"))

    return errors, rows


def validate_speakers(path: str, canonical_speakers: Set[str]) -> List[ValidationError]:
    errors, rows = validate_csv_table(path, REQUIRED_ROOT_CSVS["speakers.csv"])
    if errors:
        return errors

    seen_ids = set()
    for idx, r in enumerate(rows, start=2):
        if not r or not r[0].strip():
            continue
        spk_id = r[0].strip()
        name = r[1].strip() if len(r) > 1 else ""

        if spk_id in seen_ids:
            errors.append(ValidationError(path, f"Duplicate SPEAKER_ID: '{spk_id}'", idx))
        seen_ids.add(spk_id)

        if not spk_id.startswith("SPK_"):
            errors.append(ValidationError(path, f"Speaker ID '{spk_id}' must start with 'SPK_'", idx))

        if canonical_speakers and spk_id not in canonical_speakers:
            errors.append(
                ValidationError(
                    path,
                    f"Unknown SPEAKER_ID '{spk_id}' not found in canonical template",
                    idx,
                )
            )

        if not name:
            errors.append(ValidationError(path, f"Empty name for speaker '{spk_id}'", idx))

    return errors


def validate_scenarios(
    locale_sc_dir: str,
    template_sc_dir: str,
    canonical_speakers: Set[str],
) -> List[ValidationError]:
    errors = []
    if not os.path.isdir(locale_sc_dir):
        return [ValidationError(locale_sc_dir, "Scenarios directory does not exist")]

    locale_files = {f for f in os.listdir(locale_sc_dir) if f.endswith(".csv")}
    template_files = {f for f in os.listdir(template_sc_dir) if f.endswith(".csv")}

    missing_files = template_files - locale_files
    if missing_files:
        errors.append(
            ValidationError(
                locale_sc_dir,
                f"Missing {len(missing_files)} scenario file(s) from template: {sorted(missing_files)[:5]}...",
            )
        )

    for sc_file in sorted(locale_files):
        sc_path = os.path.join(locale_sc_dir, sc_file)
        tmpl_path = os.path.join(template_sc_dir, sc_file)

        sc_errors, sc_rows = validate_csv_table(sc_path, SCENARIO_COLUMNS)
        errors.extend(sc_errors)
        if sc_errors:
            continue

        if os.path.isfile(tmpl_path):
            _, tmpl_rows = validate_csv_table(tmpl_path, SCENARIO_COLUMNS)
            if len(sc_rows) != len(tmpl_rows):
                errors.append(
                    ValidationError(
                        sc_path,
                        f"Row count mismatch with template: expected {len(tmpl_rows)}, got {len(sc_rows)}",
                    )
                )
            else:
                for idx, (sr, tr) in enumerate(zip(sc_rows, tmpl_rows), start=2):
                    if sr[0].strip() != tr[0].strip():
                        errors.append(
                            ValidationError(
                                sc_path,
                                f"Row {idx} KEY mismatch: expected '{tr[0]}', got '{sr[0]}'",
                                idx,
                            )
                        )
                        break

        for idx, r in enumerate(sc_rows, start=2):
            spk = r[1].strip() if len(r) > 1 else ""
            if spk and canonical_speakers and spk not in canonical_speakers:
                errors.append(
                    ValidationError(
                        sc_path,
                        f"Invalid SPEAKER_ID '{spk}' in dialogue",
                        idx,
                    )
                )

    return errors


def validate_locale(locale_dir: str, template_dir: str) -> List[ValidationError]:
    errors = []
    loc = os.path.basename(os.path.normpath(locale_dir)).lower()

    # 1. manifest.json
    manifest_path = os.path.join(locale_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        errors.append(ValidationError(manifest_path, "manifest.json is missing"))
    else:
        errors.extend(validate_manifest_json(manifest_path, loc))

    # 2. Canonical speakers from template
    canonical_speakers = load_canonical_speakers(os.path.join(template_dir, "speakers.csv"))

    # 3. Root CSVs
    for fn, header in REQUIRED_ROOT_CSVS.items():
        csv_path = os.path.join(locale_dir, fn)
        if not os.path.isfile(csv_path):
            errors.append(ValidationError(csv_path, f"Required root file '{fn}' is missing"))
            continue

        if fn == "speakers.csv":
            errors.extend(validate_speakers(csv_path, canonical_speakers))
        else:
            table_errors, _ = validate_csv_table(csv_path, header)
            errors.extend(table_errors)

    # 4. Scenarios
    sc_dir = os.path.join(locale_dir, "scenarios")
    tmpl_sc_dir = os.path.join(template_dir, "scenarios")
    errors.extend(validate_scenarios(sc_dir, tmpl_sc_dir, canonical_speakers))

    return errors


def main():
    parser = argparse.ArgumentParser(description="OreImouto Translation Validator")
    parser.add_argument("--locale", help="Validate a specific locale (e.g. 'ru' or 'locales/ru')")
    parser.add_argument("--all", action="store_true", help="Validate all locales in locales/")
    parser.add_argument("--repo-root", default=".", help="Root directory of oreimouto-translations")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    template_dir = os.path.join(repo_root, "template")
    locales_dir = os.path.join(repo_root, "locales")

    if not os.path.isdir(template_dir):
        print(f"[ERROR] Template directory not found: {template_dir}", file=sys.stderr)
        sys.exit(2)

    locales_to_check = []
    if args.locale:
        p = os.path.abspath(args.locale) if os.path.isdir(args.locale) else os.path.join(locales_dir, args.locale)
        locales_to_check.append(p)
    elif args.all or not args.locale:
        if os.path.isdir(locales_dir):
            for d in sorted(os.listdir(locales_dir)):
                full_d = os.path.join(locales_dir, d)
                if os.path.isdir(full_d) and not d.startswith("."):
                    locales_to_check.append(full_d)

    if not locales_to_check:
        print("[ERROR] No locales found to validate", file=sys.stderr)
        sys.exit(2)

    all_passed = True
    for loc_dir in locales_to_check:
        loc_name = os.path.basename(loc_dir)
        print(f"[*] Validating locale: {loc_name} ({loc_dir})...")
        errors = validate_locale(loc_dir, template_dir)
        if errors:
            all_passed = False
            print(f"[FAIL] {loc_name} has {len(errors)} error(s):")
            for e in errors[:20]:
                print(str(e))
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more errors.")
        else:
            print(f"[PASS] {loc_name} passed all validation checks cleanly.")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
