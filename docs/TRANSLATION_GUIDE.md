# OreImouto Re:Port — Translation Guide

Welcome to the community translation hub for **OreImouto Re:Port** (*Ore no Imouto ga Konna ni Kawaii Wake ga Nai Portable* PC port).

This repository contains community translation source files and tools to compile, validate, and package translations into binary `.pck` files for the game.

---

## 1. How Translations Work

OreImouto Re:Port uses a multi-layered Virtual File System (VFS).
Language packs are mounted dynamically at runtime as virtual overlays:

```
user://packs/lang_<locale>.pck -> res://assets/data/lang/<locale>/...
```

At runtime, dialogue texts, character names, UI strings, O.R.E. titles, OSIS tsukkomi choices, and toasts are resolved dynamically from the active language pack overlay.

---

## 2. Directory Structure of a Language Pack

Each locale lives inside `locales/<locale_code>/`:

```
locales/<locale>/
├── manifest.json       # Metadata displayed in in-game translation hub & UI
├── manifest.csv        # Metadata bundled inside the binary PCK
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

---

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
     "id": "lang_es_community",
     "locale": "es",
     "display_name": "Español",
     "team_name": "Spanish Translation Team",
     "authors": [
       "Translator 1",
       "Translator 2"
     ],
     "version": "1.0.0",
     "description": "Traducción al español de Ore no Imouto Portable para PC."
   }
   ```
5. Update `manifest.csv`:
   ```csv
   KEY,VALUE
   locale,es
   name,Español
   short,ESP
   author,Spanish Translation Team
   version,1.0.0
   schema_version,2
   ```

---

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

---

## 5. CSV Rules & Encoding

- **Encoding:** Always save as standard **UTF-8 (without BOM)**.
- **RFC 4180 Escaping:**
  - If a text contains commas (`,`), newlines (`\n`), or double quotes (`"`), wrap the whole field in `"..."`.
  - Escaped double quotes inside text must be doubled (`""`).
  - Example: `"She said, ""Hello!"""`

---

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

---

## 7. Submitting Your Translation

Once validated and tested:
1. Commit your changes:
   ```bash
   git add locales/<your_code>/
   git commit -m "Add/Update <Language> translation"
   ```
2. Push to your fork and submit a **Pull Request**.
3. Automated GitHub Actions will validate your files.
4. Once merged, GitHub Actions will compile the binary package and deploy it to the Translation Hub for all players worldwide!
