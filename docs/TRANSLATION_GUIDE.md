# OreImouto Re:Port — Translation Guide

Welcome to the **OreImouto Re:Port** community translation guide! This document explains how translation packs are organized, how to create or update a translation, and how to check and test your work locally.

## 1. How Translations Work

All game text — dialogue, menus, character names, scene titles, notifications, O.R.E. topics, OSIS prompts, soundtrack titles, and UI strings — is stored in plain UTF-8 CSV spreadsheets.

Each language folder is packed into a single `.pck` file (`lang_<locale>.pck`) mounted under `res://assets/data/lang/<locale>/`, overriding the original Japanese text from your Base ISO (`lang_base.pck`). When players use the in-game downloader, the game reads [`catalog.json`](../catalog.json) to check for updates and verify downloaded packs.

## 2. Directory Structure of a Language Pack

Each translation pack lives inside `locales/<locale_dir>/`:

```
locales/<locale_dir>/
├── manifest.json       # Pack details shown in settings & the download catalog
├── speakers.csv        # Character ID -> Character name
├── scene_titles.csv    # SCENE_ID -> Chapter/Scene title
├── toasts.csv          # TOAST_KEY -> System/unlock notification
├── ores.csv            # ORE_ID -> O.R.E. topic title & description
├── osis.csv            # KEY, STYLE, TEXT -> Tsukkomi exclamation choices
├── bgm.csv             # TRACK_ID, TITLE -> Soundtrack titles
├── ui.csv              # KEY, TEXT -> Menus, buttons, and settings
├── choices.csv         # (Optional) SOURCE, TEXT -> In-script choice label overrides
├── fonts/              # (Optional) Custom .ttf/.otf fonts and license (e.g., OFL.txt)
└── scenarios/          # 569 scenario dialogue CSVs (300 Disc 1 + 269 Disc 2)
    ├── AKYO_0000A.csv  # Disc 1 scenario (no underscore prefix)
    ├── _AKYO_0000A.csv # Disc 2 scenario (leading underscore prefix)
    └── ...
```

### UI-Only Language Packs (`"ui_only": true`)
A language pack can translate only the game menus while letting original dialogue and database text pass through from the user's installed Base ISO (`lang_base.pck`). For example, [`locales/ja/`](../locales/ja/manifest.json) sets `"ui_only": true` and includes only `manifest.json` and `ui.csv`, omitting the other root CSVs and `scenarios/`.

## 3. Starting a New Language Translation

1. **Fork & Clone** this repository.
2. **Choose your folder name:** Pick a short language code (such as `es` for Spanish, `fr` for French, `de` for German, `pt` for Portuguese, `zh` for Chinese, or `ko` for Korean).
   - Note: `tools/validate.py` checks that `"locale"` in `manifest.json` (lowercased) matches the folder name (`locales/es` → `"locale": "es"`) or starts with `<folder>_` / `<folder>-` (for example, `locales/zh/` uses `"locale": "zh_CN"` and `"id": "lang_zh_cn"`).
3. **Copy the master template:**
   ```bash
   cp -r template locales/<your_code>
   ```
4. **Update `manifest.json`:**
   ```json
   {
     "$schema": "https://raw.githubusercontent.com/andre-pullinen/oreimouto-translations/main/schema/manifest.schema.json",
     "id": "lang_es",
     "locale": "es",
     "name": "Español",
     "short": "ESP",
     "version": "1.0.0",
     "description": "Traducción al español de Ore no Imouto Portable para PC.",
     "team": "Spanish Translation Team",
     "translators": [
       "Translator 1",
       "Translator 2"
     ],
     "progress": 100.0,
     "tags": {},
     "fonts": {},
     "links": {
       "website": "https://your-translation-team.org",
       "discord": "https://discord.gg/example"
     }
   }
   ```

   **Required Manifest Fields** (validated against [`schema/manifest.schema.json`](../schema/manifest.schema.json)):
   - **`id`**: Package ID (for example, `lang_es`, `lang_ru`, `lang_zh_cn`).
   - **`locale`**: Language code (for example, `es`, `ru`, `en`, `zh_CN`). Must match or share the prefix of your folder name.
   - **`name`**: Native language name shown in-game (for example, `Español`, `Русский`, `简体中文`).
   - **`short`**: 3-letter uppercase badge shown in the UI (for example, `ESP`, `RUS`, `ENG`).
   - **`version`**: Pack version (for example, `1.0.0`).
   - **`description`**: Short summary of what the pack translates.
   - **`team`**: Name of your translation team or maintainer.
   - **`translators`**: List of contributor names.

   **Optional Manifest Fields:**
   - **`$schema`**: Schema link for editor autocompletion and checks.
   - **`progress`**: Optional completion percentage (`0.0`–`100.0`). For full packs, `tools/generate_catalog.py` calculates `progress`, `total_lines`, and `translated_lines` automatically from `scenarios/`.
   - **`ui_only`**: Set `true` for UI-only packs (like `ja`) that ship only `manifest.json` + `ui.csv` and pass through scenario/database text from the user's Base ISO (`lang_base.pck`).
   - **`tags`**: Optional status badges shown in-game (`partial`, `beta`, `wip`, `ai`) mapped to short Markdown descriptions, a list of tag names, or `{}` when finished.
   - **`fonts`**: Optional font overrides mapping roles (`ui`, `ui_bold`, `ui_medium`, `dialogue`, `speaker`, `accent`, `fallback`, `cjk`) to font paths inside your pack.
   - **`links`**: Optional project links (`website`, `discord`, `vk`, `romhacking`, `ruvn`, `baidu_tieba`, etc.).

### Custom Fonts (`fonts/`)
If your language needs characters missing from the game's default fonts (or a custom typeface), put open-licensed `.ttf` or `.otf` font files along with their license (such as `OFL.txt`) in `locales/<your_code>/fonts/` and point to them in `manifest.json` (see [`locales/zh/manifest.json`](../locales/zh/manifest.json)):

```json
"fonts": {
  "ui": "fonts/NotoSansSC-Medium.otf",
  "dialogue": "fonts/NotoSansSC-Medium.otf",
  "speaker": "fonts/NotoSansSC-Medium.otf",
  "accent": "fonts/NotoSansSC-Medium.otf",
  "fallback": "fonts/NotoSansSC-Medium.otf"
}
```

## 4. Translating Files

### 4.1. Scenarios (`scenarios/*.csv`)
There are 569 scenario CSV files: **300 Disc 1** files without a prefix (e.g., `AKYO_0000A.csv`) and **269 Disc 2** files with a leading underscore (e.g., `_AKYO_0000A.csv`). Keep all filenames unchanged.

Each file has 3 columns:
```csv
ID,SPEAKER,TEXT
0,,"--Welcome, visitor from afar, to our world known as 
the Destiny Record."
1,,"......This is the valley of endings and rebirths, the 
place where many destinies assemble."
2,,"--Well then, tell me about your past..."
3,SPK_KIRIRIN,"Okayokayokay~! That's enough beating around the 
bush~♪"
```

- **`ID`**: Line number. **DO NOT MODIFY**.
- **`SPEAKER`**: Speaker ID (e.g., `SPK_KYOUSUKE`, `SPK_KIRINO`) or empty for narration. **DO NOT MODIFY**.
- **`TEXT`**: The dialogue line. **This is what you translate.**

> [!IMPORTANT]
> - Do not delete, add, or reorder rows.
> - `ID` values and row counts must match `template/scenarios/` exactly.
> - **Keyword Highlight Markup (`[...]` / `【...】`):** Words inside `[...]` (or `【...】` in CJK packs), such as `A [Siscaly tournament]?`, are highlighted in color using the original PSP style (cyan when unread, green when already read if read-text highlighting is enabled). Standard Godot BBCode tags (`[b]`, `[i]`, `[color=...]`, etc.) still work as normal formatting. Always keep the highlight brackets around the translated keyword.

### 4.2. Speakers (`speakers.csv`)
```csv
SPEAKER_ID,NAME
SPK_KYOUSUKE,Kyousuke
SPK_KIRINO,Kirino
SPK_KURONEKO,Kuroneko
```
- **`SPEAKER_ID`**: Internal character ID (e.g., `SPK_AYASE`). Leave as is.
- **`NAME`**: Character's display name in your language (e.g., `Кирино`, `Kirino`, `キリノ`).

### 4.3. User Interface (`ui.csv`)
```csv
KEY,TEXT
COMMON_YES,Yes
COMMON_NO,No
COMMON_CANCEL,Cancel
```
Translate the `TEXT` column for menus, settings, and buttons. Every key from `template/ui.csv` must be present without duplicates.

> [!IMPORTANT]
> Keep placeholders like `%s`, `%d`, `%02d` and `\n` line breaks intact in the same count, order, and type — the game fills numbers, names, and button prompts into them at runtime (for example, `SAVELOAD_PAGE_FORMAT` = `Page %d / %d`, `MENU_LANGUAGE` = `Language: %s`).

### 4.4. Scene Titles (`scene_titles.csv`)
```csv
SCENE_ID,TITLE
AASTARTPOINT,Start Point
AKYO_0000A,My Little Sister
AKYO_0010A,Bursting Into The Room
```
Translate `TITLE` (shown in the Story Flowmap and on save cards). Keep `SCENE_ID` unchanged.

### 4.5. System Notifications (`toasts.csv`)
```csv
TOAST_KEY,TEXT
BKIR_0109E:0,"""TwoShot Barrage"" is now available in options"
BKIR_0109E:1,"""TwoShot Hint"" is now available in options"
```
Translate `TEXT` (pop-up unlock and system notifications). Keep `TOAST_KEY` (`SCENE_ID:INDEX`) unchanged.

### 4.6. O.R.E. Topics (`ores.csv`)
```csv
ORE_ID,TITLE,DESCRIPTION
1,Siscaly Tournament,"A tournament gathering for every Siscaly player..."
```
Translate `TITLE` and `DESCRIPTION`. Keep `ORE_ID` unchanged.

### 4.7. OSIS Tsukkomi Choices (`osis.csv`)
```csv
KEY,STYLE,TEXT
TKA0020A,normal,This is just a misunderstanding!
TKA0020B,shout,I didn't see them!
```
Translate `TEXT`. Keep `KEY` unique and unchanged, and leave `STYLE` as `normal`, `shout`, or empty. (If a specific scene ever needs different wording for the same prompt, you can also add a `SCENE_ID:ASSET_KEY` row.)

### 4.8. BGM Titles (`bgm.csv`)
```csv
TRACK_ID,TITLE
00000_0,oRE No IMoUTo.
00001_1,GOOD MORNiNG
```
Translate `TITLE` (shown in the Music Room and BGM notifications). Keep `TRACK_ID` unchanged.

> [!CAUTION]
> Disc 1 and Disc 2 share 17 `TRACK_ID` values (for example, `00000_0` appears once in the Disc 1 section and again in the Disc 2 section). The game tells Disc 1 and Disc 2 tracks apart strictly by **row order** (first appearance = Disc 1, second appearance = Disc 2). Never sort, reorder, or remove duplicate IDs in `bgm.csv`.

### 4.9. Optional Choice Overrides (`choices.csv`)
Optional file (`SOURCE,TEXT`) for translating on-screen choice buttons that are not part of the scenario files (see [`locales/ru/choices.csv`](../locales/ru/choices.csv)). It is not included in `template/` and is not required.

## 5. CSV Rules & Encoding

- **Encoding:** Always save CSV and JSON files as **UTF-8 (without BOM)** with **LF (`\n`)** line endings.
  - *Tip:* Spreadsheet tools like LibreOffice Calc or Google Sheets handle quoting automatically, while Microsoft Excel's default "CSV" often adds a UTF-8 BOM. Choose "CSV UTF-8" or edit in VS Code, then verify with `tools/validate.py`.
- **Commas, Quotes & Newlines (CSV Rules):**
  - If a field contains commas (`,`), line breaks, or double quotes (`"`), wrap the entire field in `"..."`.
  - Double quotes inside a quoted field must be doubled (`""`).
  - Example: `"She said, ""Hello!"""`
- **Progress Calculation:** `tools/generate_catalog.py` measures completion across `scenarios/*.csv` using language-specific checks (for example, `ru` checks for Cyrillic and ignores untouched English fallback lines; `zh` / `zh_CN` flags leftover Japanese Kana; `en` accepts any non-Japanese line).

## 6. Testing Your Translation Locally

Requires **Python 3.11+** (no extra packages needed).

### 1. Validate Your Files
```bash
python3 tools/validate.py --locale <your_code>
```
If any files are missing, have encoding/BOM issues, invalid `manifest.json` fields, missing `ui.csv` keys, or mismatched scenario lines, the script points to the exact file and line number.

### 2. Build `.pck` File
Name the output file using the lowercase `locale` from `manifest.json` (for example, `dist/lang_zh_cn.pck` for `locales/zh` with `"locale": "zh_CN"`):
```bash
python3 tools/build_pck.py locales/<your_code> -o dist/lang_<locale_lower>.pck
```

### 3. Test in OreImouto Re:Port
Copy the generated `.pck` file into the game's `packs/` folder:
- **Linux:** `~/.local/share/godot/app_userdata/OreImouto Re-Port/packs/`
- **Windows:** `%APPDATA%\Godot\app_userdata\OreImouto Re-Port\packs\`
- **macOS:** `~/Library/Application Support/Godot/app_userdata/OreImouto Re-Port/packs/`

Launch the game, open **Settings → System → Language** (click **Rescan** if the game was already running), and select your language.

## 7. Submitting Your Translation

Once validated and tested:
1. Commit your changes:
   ```bash
   git add locales/<your_code>/
   git commit -m "Add/Update <Language> translation"
   ```
2. Push to your fork and open a **Pull Request**.
3. GitHub Actions automatically validates your files and runs a test `.pck` build on your PR.
4. Once merged, a new tagged release (`v*`) automatically builds the updated `.pck` files and updates the in-game catalog so players can download the update right from the game.
