# OreImouto Translations Hub (`oreimouto-translations`)

Public community localization repository for **OreImouto Re:Port** using a clean Bring-Your-Own-Game (BYOG) language-pack model: localized CSV overlays are packed into standalone Godot `.pck` modules mounted under `res://assets/data/lang/<locale>/`.

---

## 1. Repository Layout

- `template/` — Canonical source files (`manifest.json`, `speakers.csv`, `scene_titles.csv`, `toasts.csv`, `ores.csv`, `osis.csv`, `bgm.csv`, `ui.csv`, `scenarios/*.csv`). Do not break template ID alignment. `template/ui.csv` (`KEY,TEXT`) is synchronized from `oreimo/translations/ui.csv` via `oreimo/scripts/tools/sync_i18n.py`.
- `locales/<locale>/` — Individual language packs (`en/`, `ja/`, `ru/`, `zh/`, etc.), each containing `manifest.json`, root CSVs, `scenarios/*.csv`, optional `choices.csv`, and optional locale `fonts/`. Packs with `"ui_only": true` (such as `ja/`) carry only `manifest.json` and `ui.csv` and rely on the user's installed Base ISO (`lang_base.pck`) for scenario and database text.
- `docs/TRANSLATION_GUIDE.md` — Contributor guide covering pack structure, manifest schema, CSV tables, keyword highlight markup, and local testing.
- `schema/manifest.schema.json` — JSON Schema for `manifest.json` (required keys: `id`, `locale`, `name`, `short`, `version`, `description`, `team`, `translators`; optional `$schema`, `ui_only`, `progress`, `tags`, `fonts`, `links`).
- `catalog.json` — Release index consumed by the in-game language downloader.
- `tools/` — Pure-Python >=3.11 core CI/CLI tools (`validate.py`, `build_pck.py`, `generate_catalog.py`). Synchronization of `template/ui.csv`, `locales/en/osis.csv`, and `catalog.json` with the engine repository (`oreimo`) is performed via `oreimo/scripts/tools/sync_i18n.py` (`check`, `push`, `pull`, `sync`).
- `.github/workflows/{validate,release}.yml` — CI validation and GitHub Releases publishing pipelines.

---

## 2. Format & Validation Rules

1. **Encoding:** Strict UTF-8 **without BOM** and LF (`\n`) line endings on all CSV, JSON, and Markdown files.
2. **Canonical IDs & Structure:**
   - Root CSV headers must match `tools/validate.py` (`REQUIRED_ROOT_CSVS`). For `"ui_only": true` packs, `manifest.json` and `ui.csv` are required while scenario/database CSVs are omitted so Base ISO text (`lang_base.pck`) passes through.
   - `ui.csv` keys must cover all keys in `template/ui.csv` without duplicates, preserving `printf` format specifiers (`%s`, `%d`, `%02d`, etc.) and `\n` line breaks.
   - `osis.csv` uses canonical 333 asset keys (`TKA...`) with unique `KEY` and `STYLE` in `normal`, `shout`, or empty.
   - `bgm.csv` row order encodes Disc 1 vs Disc 2 for shared `TRACK_ID`s (17 IDs repeat between Disc 1 and Disc 2); never reorder or deduplicate rows.
   - `speakers.csv` IDs must remain aligned with `template/speakers.csv`.
   - Scenario CSV columns are `ID,SPEAKER,TEXT` aligned row-for-row against `template/scenarios/`, preserving PSP keyword highlight tags (`[...]` / `【...】`).
3. **Locale Progress Heuristics (`tools/generate_catalog.py`):**
   - `zh` / `zh_*`: Japanese Kana (`\u3040-\u30ff`) is flagged as untranslated.
   - `ru`: Requires Cyrillic (or shared non-Latin punctuation matching the template); raw Latin/Japanese lines are counted as untranslated.
   - `en`: Any non-Japanese line counts as translated.
4. **Public Legal Hygiene:** Never include proprietary game assets or internal engineering slang; keep all notices aligned with neutral BYOG / legal original-copy terminology (see `README.md` / `LICENSE`).

---

## 3. CLI & CI Verification Commands

Run these from the repository root (`/home/andre/Documents/oreimouto-translations`) before pushing or packaging:

```bash
# 1. Validate all locales against schema and template
python3 tools/validate.py --all

# Validate a single locale
python3 tools/validate.py --locale ru

# 2. Build Godot v4 language overlay PCK(s) into dist/ (mounted at res://assets/data/lang/<locale>/)
# Note: For regional locales (e.g. locales/zh with "locale": "zh_CN"), -o must use the lowercase manifest locale
# so generate_catalog.py resolves size_bytes and sha256 from dist/.
python3 tools/build_pck.py locales/ru -o dist/lang_ru.pck
python3 tools/build_pck.py locales/zh -o dist/lang_zh_cn.pck

# 3. Regenerate catalog.json with progress metrics and SHA-256 checksums
# (Build .pck files into dist/ first; otherwise size_bytes=0 and sha256="")
python3 tools/generate_catalog.py --release-tag v1.0.3 -o catalog.json
```
