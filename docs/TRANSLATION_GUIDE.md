# OreImouto Re:Port — Translation Guide

Welcome to the **OreImouto Re:Port** community translation guide! This document explains how translations are structured, how to add a new language, and how to test your changes locally.

## 1. Overview & Architecture

OreImouto Re:Port uses a zero-dependency, table-based translation format. All game text (dialogues, choices, character names, UI strings) is stored in UTF-8 CSV files.

Each language is compiled into a standalone binary package (`lang_<locale>.pck`) that overlays the game's virtual file system (VFS) at runtime. The in-game client automatically checks for translation updates and downloads new or updated packs seamlessly.

## 2. Directory Structure of a Language Pack

Each locale lives inside `locales/<locale_code>/`:

```
locales/<locale>/
├── manifest.json       # Metadata displayed in in-game settings & UI
├── speakers.csv        # Canonical Speaker ID -> Translated Display Name
├── scene_titles.csv    # SCENE_ID -> Translated Chapter/Scene title
├── toasts.csv          # TOAST_KEY -> Translated system notification
├── ores.csv            # ORE_ID -> Title & description of O.R.E. topics
├── osis.csv            # KEY, STYLE -> Tsukkomi exclamation choices
├── bgm.csv             # TRACK_ID -> Soundtrack title
├── ui.csv              # KEY -> In-game user interface strings
└── scenarios/          # 569 scenario dialogue files (ID, SPEAKER, TEXT)
    ├── _AKYO_0000A.csv
    ├── _BKIR_0000A.csv
    └── ...
```

## 3. Starting a New Language Translation

1. **Fork & Clone** this repository.
2. Choose your 2-letter ISO 639-1 language code (e.g., `es` for Spanish, `fr` for French, `de` for German, `pt` for Portuguese, `zh` for Chinese, `ko` for Korean).
3. Copy the master template:
   ```bash
   cp -r template locales/<your_code>
   ```
4. Update `manifest.json`:
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

   **Manifest Fields Specification:**
   - **`$schema`**: Points to the official JSON schema for validation and autocompletion in VS Code.
   - **`id`**: Unique identifier for the package (e.g. `lang_es`, `lang_ru`).
   - **`locale`**: ISO 639-1 / BCP 47 language code (`es`, `ru`, `en`, `zh_CN`).
   - **`name`**: Native display name of the language (e.g. `Español`, `Русский`, `简体中文`).
   - **`short`**: 3-letter uppercase badge label shown in the in-game UI (e.g. `ESP`, `RUS`, `ENG`).
   - **`version`**: Semantic version string (e.g. `1.0.0`).
   - **`description`**: Summary of the translation scope.
   - **`team`**: Name of the translation team or lead.
   - **`translators`**: List of individual contributors and translators.
   - **`progress`**: *(Optional)* Percentage of translated lines (0.0 - 100.0).
   - **`tags`**: *(Optional)* Dictionary mapping status tags (`partial`, `beta`, `wip`, `ai`) to Markdown explanation tooltips (or an empty object `{}` when complete).
   - **`fonts`**: *(Optional)* Mapping of custom font roles (`ui`, `dialogue`, `speaker`, `accent`, `fallback`).
   - **`links`**: *(Optional)* Map of external project links (`website`, `discord`, `vk`, `romhacking`).

## 4. Translating Files

### 4.1. Scenarios (`scenarios/*.csv`)
Each file has 3 columns:
```csv
ID,SPEAKER,TEXT
0,,"--Welcome, visitor from afar..."
1,,"......This is the valley of endings and rebirths..."
2,,"--Well then, tell me about your past..."
3,SPK_KIRIRIN,"Okayokayokay~! That's enough beating around the bush~♪"
```

- **`ID`**: The sequential dialogue number. **DO NOT MODIFY**.
- **`SPEAKER`**: Canonical speaker ID (e.g., `SPK_KYOUSUKE`, `SPK_KIRINO`) or empty for narrator. **DO NOT MODIFY**.
- **`TEXT`**: The translated dialogue. **This is what you translate.**

> [!IMPORTANT]
> - Do not delete or reorder rows.
> - Dialogue IDs must stay strictly identical to `template/scenarios/`.

### 4.2. Speakers (`speakers.csv`)
```csv
SPEAKER_ID,NAME
SPK_KYOUSUKE,Kyousuke
SPK_KIRINO,Kirino
SPK_KURONEKO,Kuroneko
...
```
- **`SPEAKER_ID`**: Canonical invariant character ID (e.g., `SPK_AYASE`). **DO NOT MODIFY**.
- **`NAME`**: Character's name in your language (e.g. `Кирино`, `Kirino`, `キリノ`).

### 4.3. User Interface (`ui.csv`)
```csv
KEY,TEXT
COMMON_YES,Yes
COMMON_NO,No
COMMON_CANCEL,Cancel
...
```
Translate the `TEXT` column for menus, settings, and buttons.

### 4.4. O.R.E. Topics (`ores.csv`)
```csv
ORE_ID,TITLE,DESCRIPTION
1,Siscaly Tournament,"A tournament gathering for every Siscaly player..."
```
Translate `TITLE` and `DESCRIPTION`. Keep `ORE_ID` unchanged.

### 4.5. OSIS Tsukkomi Choices (`osis.csv`)
```csv
KEY,STYLE,TEXT
AKYO_0020T:TKA0020A,normal,This is just a misunderstanding!
AKYO_0020T:TKA0020B,shout,I didn't see them!
```
Translate `TEXT`. Keep `KEY` and `STYLE` unchanged.

## 5. CSV Rules & Encoding

- **Encoding:** Always save as standard **UTF-8 (without BOM)**.
- **RFC 4180 Escaping:**
  - If a text contains commas (`,`), newlines (`\n`), or double quotes (`"`), wrap the whole field in `"..."`.
  - Escaped double quotes inside text must be doubled (`""`).
  - Example: `"She said, ""Hello!"""`

## 6. Testing Your Translation Locally

You can build and test your translation directly in the game without installing any compilers:

### 1. Validate Your Files
```bash
python3 tools/validate.py --locale <your_code>
```
If there are missing files, syntax errors, or unaligned dialogue lines, the tool will pinpoint the exact file and line number.

### 2. Build `.pck` File
```bash
python3 tools/build_pck.py locales/<your_code> -o dist/lang_<your_code>.pck
```

### 3. Test in OreImouto Re:Port
Copy the generated `.pck` file into the game's `packs/` folder:
- **Linux:** `~/.local/share/godot/app_userdata/OreImouto Re-Port/packs/`
- **Windows:** `%APPDATA%\Godot\app_userdata\OreImouto Re-Port\packs\`

Launch the game, open **Settings $\to$ Language**, and select your language!

## 7. Submitting Your Translation

Once validated and tested:
1. Commit your changes:
   ```bash
   git add locales/<your_code>/
   git commit -m "Add/Update <Language> translation"
   ```
2. Push to your fork and submit a **Pull Request**.
3. Automated GitHub Actions will validate your files.
4. Once merged, GitHub Actions will compile the binary package and deploy it for all players worldwide!
