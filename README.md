# OreImouto Re:Port — Translations Hub

[![Validate Translations](https://github.com/andre-pullinen/oreimouto-translations/actions/workflows/validate.yml/badge.svg)](https://github.com/andre-pullinen/oreimouto-translations/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Engine: Godot 4.7+](https://img.shields.io/badge/Godot-4.7%2B-478cbf?logo=godotengine&logoColor=white)](https://godotengine.org)

Official community translation repository and package hub for **OreImouto Re:Port** (*Ore no Imouto ga Konna ni Kawaii Wake ga Nai Portable* PC port).

This repository contains translation source files (scenarios, character names, O.R.E. topics, OSIS tsukkomi choices, system UI) and automated zero-dependency build tooling to compile translation packs into binary `.pck` files.

---

## Available Translations

| Language | Locale | Progress | Translated Lines | Status | Download |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **English** | `en` | **97.5%** | 36,449 / 37,383 | Complete | [lang_en.pck](https://github.com/andre-pullinen/oreimouto-translations/releases/latest/download/lang_en.pck) |
| **Русский** (Russian) | `ru` | **83.6%** | 31,244 / 37,383 | Main Routes | [lang_ru.pck](https://github.com/andre-pullinen/oreimouto-translations/releases/latest/download/lang_ru.pck) |

> [!NOTE]
> Translations can be installed directly through the in-game **Translation Hub** in OreImouto Re:Port or downloaded manually.

---

## For Players: Manual Installation

1. Download the `.pck` file for your desired language from the [Releases](https://github.com/andre-pullinen/oreimouto-translations/releases) page.
2. Place the downloaded `.pck` file into the game's `packs/` folder:
   - **Linux:** `~/.local/share/godot/app_userdata/OreImouto Re-Port/packs/`
   - **Windows:** `%APPDATA%\Godot\app_userdata\OreImouto Re-Port\packs\`
3. Launch the game and select your language in **Settings $\to$ Language**.

---

## For Translators: Contributing

Interested in contributing to an existing translation or adding a new language? We welcome community contributions!

Please refer to the comprehensive guide:
👉 **[Translation Guide](docs/TRANSLATION_GUIDE.md)**

### Quick Start
1. Fork and clone this repository:
   ```bash
   git clone https://github.com/andre-pullinen/oreimouto-translations.git
   cd oreimouto-translations
   ```
2. Copy `template/` to your target language folder:
   ```bash
   cp -r template locales/<your_language_code>
   ```
3. Edit the CSV files in `locales/<your_language_code>/` (using UTF-8 without BOM).
4. Validate your changes:
   ```bash
   python3 tools/validate.py --locale <your_language_code>
   ```
5. Test your build locally in-game:
   ```bash
   python3 tools/build_pck.py locales/<your_language_code> -o dist/lang_<your_language_code>.pck
   ```
6. Submit a **Pull Request**!

---

## Repository Structure

```
oreimouto-translations/
├── .github/workflows/
│   ├── validate.yml        # Automated CI validator for PRs
│   └── release.yml         # Automated builder & release publisher
├── docs/
│   └── TRANSLATION_GUIDE.md # Detailed translator instructions
├── locales/
│   ├── en/                 # English translation sources (577 files)
│   └── ru/                 # Russian translation sources (577 files)
├── template/               # Master translation template with canonical IDs
├── tools/
│   ├── build_pck.py        # Pure-Python Godot 4.x PCK builder (zero dependencies)
│   ├── validate.py         # CSV & canonical speaker ID validator
│   └── generate_catalog.py # Translation progress & catalog.json generator
├── catalog.json            # Machine-readable translation index for in-game client
└── README.md
```

---

## Canonical Speaker IDs

To ensure 100% consistent character names and audio synchronization across all translations, OreImouto Re:Port uses an invariant **Canonical Speaker ID** system (`SPK_*`).

Translators only translate the `NAME` column in `speakers.csv` and keep all `SPEAKER_ID` fields intact. This guarantees cross-language compatibility, voice line binding, and save file portability.

---

## Legal & Original Game Assets Notice

OreImouto Re:Port follows a strict Bring-Your-Own-Game (BYOG) model. This repository contains only community-contributed text translations and open-source tooling. It does **not** contain any proprietary game assets, audio voice files, backgrounds, copyrighted scripts, or binary assets from Bandai Namco Games or ASCII Media Works.

---

## License

All translation tools and community translation files in this repository are distributed under the [MIT License](LICENSE).
Original game copyright belongs to Bandai Namco Games / ASCII Media Works / Tsukasa Fushimi.
