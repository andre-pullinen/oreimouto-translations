# OreImouto Re:Port — Translations Hub

[![Validate Translations](https://github.com/andre-pullinen/oreimouto-translations/actions/workflows/validate.yml/badge.svg)](https://github.com/andre-pullinen/oreimouto-translations/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Engine: Godot 4.7+](https://img.shields.io/badge/Godot-4.7%2B-478cbf?logo=godotengine&logoColor=white)](https://godotengine.org)

Community translation repository and package hub for **OreImouto Re:Port** (*Ore no Imouto ga Konna ni Kawaii Wake ga Nai Portable* PC port).

This repository contains the translation text files (scenarios, character names, scene titles, system notifications, O.R.E. topics, OSIS tsukkomi choices, BGM titles, system UI, and optional locale fonts) along with simple Python scripts to validate your edits and pack them into `.pck` files for the game.

## Available Translations

| Language | Locale | Translators | Progress | Translated Lines | Status | Download |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **English** | `en` | [Rinjinbu Translations](https://rinjinbutranslations.blogspot.com/) | **100%** | 37,383 / 37,383 | Complete | [lang_en.pck](https://github.com/andre-pullinen/oreimouto-translations/releases/latest/download/lang_en.pck) |
| **日本語** (Japanese) | `ja` | AI | **UI Only** | - | AI, Partial (Scenario text requires JP UMD ISO) | [lang_ja.pck](https://github.com/andre-pullinen/oreimouto-translations/releases/latest/download/lang_ja.pck) |
| **Русский** (Russian) | `ru` | [Elevation](https://vk.com/elevationnovel) | **84.5%** | 31,601 / 37,383 | Main Routes | [lang_ru.pck](https://github.com/andre-pullinen/oreimouto-translations/releases/latest/download/lang_ru.pck) |
| **简体中文** (Chinese) | `zh_CN` | [PSP吧汉化组 & 俺妹吧 & 游戏嗯蛋汉化联盟](https://tieba.baidu.com/p/1628163531) | **100%** | 37,383 / 37,383 | Beta | [lang_zh_cn.pck](https://github.com/andre-pullinen/oreimouto-translations/releases/latest/download/lang_zh_cn.pck) |

> [!NOTE]
> Translations can be downloaded and updated automatically in-game via **Settings → System → Language**, or installed manually as described below.

## Manual Installation

1. Download the `.pck` file for your desired language from the [Releases](https://github.com/andre-pullinen/oreimouto-translations/releases) page. Keep the `lang_<locale>.pck` lowercase filename (for example, `lang_ru.pck` or `lang_zh_cn.pck`).
2. Place the downloaded `.pck` file into the game's `packs/` folder:
   - **Linux:** `~/.local/share/godot/app_userdata/OreImouto Re-Port/packs/`
   - **Windows:** `%APPDATA%\Godot\app_userdata\OreImouto Re-Port\packs\`
   - **macOS:** `~/Library/Application Support/Godot/app_userdata/OreImouto Re-Port/packs/`
3. Launch the game, open **Settings → System → Language** (click **Rescan** if the game is already running), and select your language.

## Contributing

Interested in contributing to an existing translation, fixing typos, or adding a new language? Contributions and pull requests are always welcome!

Please refer to the comprehensive guide: **[Translation Guide](docs/TRANSLATION_GUIDE.md)**

### Quick Start
Requires **Python 3.11+** (no extra packages needed).

1. Fork and clone this repository:
   ```bash
   git clone https://github.com/andre-pullinen/oreimouto-translations.git
   cd oreimouto-translations
   ```
2. Copy `template/` to your target language folder:
   ```bash
   cp -r template locales/<your_code>
   ```
3. Fill in your language's details in `locales/<your_code>/manifest.json` (name, short code, team, translators) and make sure `locale` matches your folder name.
4. Edit the CSV files in `locales/<your_code>/` (saved as **UTF-8 without BOM**).
5. Validate your changes:
   ```bash
   python3 tools/validate.py --locale <your_code>
   ```
6. Build and test your `.pck` locally in-game (the output filename should match the lowercase `locale` in `manifest.json`, e.g., `dist/lang_zh_cn.pck` for `"locale": "zh_CN"`):
   ```bash
   python3 tools/build_pck.py locales/<your_code> -o dist/lang_<locale_lower>.pck
   ```
7. Submit a **Pull Request**!

## Repository Structure

```
oreimouto-translations/
├── .github/workflows/
│   ├── validate.yml            # Automated CI validator & test PCK build for PRs
│   └── release.yml             # Automated builder, catalog & GitHub Release publisher
├── docs/
│   └── TRANSLATION_GUIDE.md    # Detailed translator & format instructions
├── locales/
│   ├── en/                     # English translation (manifest.json, 7 root CSVs, 569 scenarios)
│   ├── ja/                     # Japanese UI-only pack (manifest.json + ui.csv)
│   ├── ru/                     # Russian translation (full pack + optional choices.csv)
│   └── zh/                     # Simplified Chinese translation (full pack + bundled fonts/)
├── schema/
│   └── manifest.schema.json    # JSON Schema for manifest.json
├── template/                   # Master English template (copy this to start a new language)
├── tools/
│   ├── build_pck.py            # Packs a language folder into a .pck file for the game
│   ├── validate.py             # Checks formatting, encoding, manifest fields, and line alignment
│   └── generate_catalog.py     # Calculates translation progress and updates catalog.json
├── catalog.json                # Package index used by the in-game language downloader
├── LICENSE                     # MIT License
└── README.md
```

## Legal & Original Game Assets Notice

OreImouto Re:Port follows a strict Bring-Your-Own-Game (BYOG) model. This repository contains only community-contributed text translations, open-source tooling, and open-licensed fonts. It does **not** contain any proprietary game assets, audio voice files, backgrounds, copyrighted scripts, or binary assets from **© Tsukasa Fushimi / ASCII MEDIA WORKS / OIP** or **© BANDAI NAMCO Entertainment Inc.**

## License

- All translation tools and community translation files in this repository are distributed under the [MIT License](LICENSE).
- Bundled third-party fonts (such as `locales/zh/fonts/NotoSansSC-Medium.otf`) remain governed by their respective licenses (see [SIL Open Font License 1.1](locales/zh/fonts/OFL.txt)).
- Original game copyright belongs to **© Tsukasa Fushimi / ASCII MEDIA WORKS / OIP** and **© BANDAI NAMCO Entertainment Inc.**
