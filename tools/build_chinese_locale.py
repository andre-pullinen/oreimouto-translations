#!/usr/bin/env python3
"""
Chinese Language Pack Builder for OreImouto Translations Hub.
Compiles raw decompiled bytecode from PSP ISOs into the standard zh locale.
"""

import os
import sys
import csv
import json
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(REPO_ROOT, "template")
LOCALES_DIR = os.path.join(REPO_ROOT, "locales")
ZH_DIR = os.path.join(LOCALES_DIR, "zh")
RAW_DATA_PATH = "/tmp/chinese_extracted_raw.json"

CHINESE_SPEAKERS = {
    "SPK_AKAGI": "赤城",
    "SPK_AKANE": "茜",
    "SPK_ALL_KURONEKO": "附近黑猫",
    "SPK_ANNOUNCER": "广播",
    "SPK_AYASE": "绫濑",
    "SPK_BAJEENA": "巴吉纳",
    "SPK_BOTH": "两人",
    "SPK_BOY_A": "男Ａ",
    "SPK_BOY_B": "男Ｂ",
    "SPK_BRATS": "小鬼头",
    "SPK_BRIDGET": "布丽吉特",
    "SPK_BUTLER": "管家",
    "SPK_CHITOSE": "千登濑",
    "SPK_CLERK": "店员",
    "SPK_COMMENTARY": "解说",
    "SPK_COMMUTER": "女性客",
    "SPK_DAISUKE": "大介",
    "SPK_DEV_TEST": "测试角色",
    "SPK_DOCTOR": "保健老师",
    "SPK_EMPLOYEE": "服务员",
    "SPK_EVERYBODY": "全员",
    "SPK_FAIRY": "妖精",
    "SPK_FATE": "菲特",
    "SPK_GIRL": "女孩",
    "SPK_GIRL_A": "女子Ａ",
    "SPK_GIRL_B": "女子Ｂ",
    "SPK_GRANDPA": "爷爷",
    "SPK_GRANNY": "奶奶",
    "SPK_HINATA": "日向",
    "SPK_HINATA_TAMAKI": "日向＆珠希",
    "SPK_KAMINEKO": "神猫",
    "SPK_KANAKO": "加奈子",
    "SPK_KANAMI": "加奈实",
    "SPK_KANATA": "彼方",
    "SPK_KAORI": "香织",
    "SPK_KIRARA": "克拉拉",
    "SPK_KIRINO": "桐乃",
    "SPK_KIRINO_KURONEKO": "桐乃＆黑猫",
    "SPK_KIRIRIN": "小桐桐",
    "SPK_KURARA": "库拉拉",
    "SPK_KURONEKO": "黑猫",
    "SPK_KURONYAN": "黑喵",
    "SPK_KYOUSUKE": "京介",
    "SPK_KYOUSUKE_KIRINO": "京介＆桐乃",
    "SPK_KYOUSUKE_KURONEKO": "京介＆黑猫",
    "SPK_LANDLADY": "老板娘",
    "SPK_LITTLE_SIS": "妹",
    "SPK_MAID": "女仆",
    "SPK_MAKABE": "真壁",
    "SPK_MANAMI": "麻奈实",
    "SPK_MERURU": "梅露露",
    "SPK_MIO": "美绪",
    "SPK_MIYABI": "小雅",
    "SPK_NAO": "菜绪",
    "SPK_OLDER_SIS": "姐",
    "SPK_OTAKU": "御宅族",
    "SPK_OTAKU_1": "宅１",
    "SPK_OTAKU_2": "宅２",
    "SPK_OTAKU_A": "宅Ａ",
    "SPK_OTAKU_B": "宅Ｂ",
    "SPK_OTAKU_GIRLS": "宅女",
    "SPK_PASSERBY_A": "路人Ａ",
    "SPK_PASSERBY_B": "路人Ｂ",
    "SPK_PHOTOGRAPHER": "拍摄员",
    "SPK_PRESIDENT": "部长",
    "SPK_RINKO": "凛子",
    "SPK_ROCK": "洛克",
    "SPK_RURI": "瑠璃",
    "SPK_RYOUSUKE": "凉介",
    "SPK_SAORI": "沙织",
    "SPK_SAORI_KAORI": "沙织＆香织",
    "SPK_SCHOOLGIRL": "女学生",
    "SPK_SECURITY": "警务员",
    "SPK_SENA": "濑菜",
    "SPK_SHIORI": "栞",
    "SPK_SPEAKERS": "电子音",
    "SPK_STUDENT": "学生",
    "SPK_TAMAKI": "珠希",
    "SPK_TOMOKA": "朋佳",
    "SPK_TOURIST": "观光客",
    "SPK_TRIO": "三人",
    "SPK_TV_1": "电视１",
    "SPK_TV_2": "电视２",
    "SPK_UNKNOWN": "？？？",
    "SPK_UNKNOWN_2": "？？",
    "SPK_UNKNOWN_4": "？？？？",
    "SPK_WOMAN": "女性",
    "SPK_WOMAN_A": "女性Ａ",
    "SPK_WOMAN_B": "女性Ｂ",
    "SPK_WOMAN_C": "女性Ｃ",
    "SPK_YAMINEKO": "暗猫",
    "SPK_YOSHINO": "佳乃",
    "SPK_YURI": "悠璃",
    "SPK_YUUNO": "优乃",
}


def split_chinese_line(text):
    text = text.strip()
    if len(text) <= 10:
        return text, "......"
    puncts = ["，", "、", "；", "……", "。", " ", "？", "！"]
    mid = len(text) // 2
    best_idx = -1
    best_dist = 999
    for p in puncts:
        idx = 0
        while True:
            pos = text.find(p, idx)
            if pos == -1:
                break
            dist = abs(pos + len(p) - mid)
            if dist < best_dist and pos > 3 and pos < len(text) - 3:
                best_dist = dist
                best_idx = pos + len(p)
            idx = pos + 1
    if best_idx != -1:
        return text[:best_idx].strip(), text[best_idx:].strip()
    return text[:mid].strip(), text[mid:].strip()


def score_continuation(prev_t, curr_t, same_speaker):
    score = 0
    if not same_speaker:
        return -100
    if curr_t and curr_t[0].islower():
        score += 20
    if curr_t and (curr_t.startswith("with ") or curr_t.startswith("her ") or curr_t.startswith("between ") or curr_t.startswith("being ")):
        score += 20
    if prev_t and not prev_t.endswith((".", "!", "?", '"', "'", "...")):
        score += 10
    if prev_t and any(
        prev_t.rstrip("\"'").endswith(" " + w)
        for w in [
            "and",
            "the",
            "a",
            "to",
            "of",
            "with",
            "that",
            "so",
            "because",
            "while",
            "handing",
            "into",
            "is",
            "was",
            "like",
            "back",
        ]
    ):
        score += 15
    return score


def main():
    if "--only-osis" in sys.argv:
        build_osis(os.path.join(ZH_DIR, "osis.csv"))
        print("[OK] Finished rebuilding osis.csv.")
        return

    if not os.path.isfile(RAW_DATA_PATH):
        # If raw extraction json is not present, still allow rebuilding osis.csv and ui.csv
        print(f"[*] Note: Raw data not found at {RAW_DATA_PATH}, updating osis.csv and ui.csv...")
        build_osis(os.path.join(ZH_DIR, "osis.csv"))
        build_ui(os.path.join(ZH_DIR, "ui.csv"))
        print("[OK] Finished updating osis.csv and ui.csv.")
        return

    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    os.makedirs(ZH_DIR, exist_ok=True)
    sc_out_dir = os.path.join(ZH_DIR, "scenarios")
    os.makedirs(sc_out_dir, exist_ok=True)

    print(f"[*] Building Chinese locale in {ZH_DIR}...")

    # 1. manifest.json
    manifest = {
        "id": "lang_zh_community",
        "locale": "zh",
        "display_name": "简体中文",
        "team_name": "PSP吧汉化组 & 俺妹吧 & 游戏嗯蛋汉化联盟",
        "authors": [
            "毫米子弹",
            "RacZY7",
            "死宅一个",
            "Amalamya",
            "大蘑菇酱",
            "九十九",
            "无节操女王",
            "藤花末叶",
            "法理守护神",
            "十七的苍真",
            "幻影の碎片",
            "MKN2",
            "気持い",
            "PSP吧汉化组",
        ],
        "version": "1.0.0",
        "description": "PSP平台《我的妹妹不可能这么可爱 便携版》Disc 1与Disc 2完整简体中文汉化包。由PSP吧汉化组、俺妹吧与游戏嗯蛋汉化联盟联合译制。",
        "links": {
            "baidu_tieba": "https://tieba.baidu.com/p/1628163531",
            "k73": "http://www.k73.com/psp/3067.html",
        },
    }
    with open(os.path.join(ZH_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 2. manifest.csv
    with open(os.path.join(ZH_DIR, "manifest.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["KEY", "VALUE"])
        w.writerow(["locale", "zh"])
        w.writerow(["name", "简体中文"])
        w.writerow(["short", "CHS"])
        w.writerow(["author", "PSP吧汉化组 & 俺妹吧 & 游戏嗯蛋"])
        w.writerow(["version", "1.0.0"])
        w.writerow(["schema_version", "2"])

    # 3. speakers.csv
    with open(os.path.join(TEMPLATE_DIR, "speakers.csv"), "r", encoding="utf-8") as tf:
        tmpl_speakers = list(csv.reader(tf))[1:]

    with open(os.path.join(ZH_DIR, "speakers.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["SPEAKER_ID", "NAME"])
        for r in tmpl_speakers:
            spk_id = r[0].strip()
            name = CHINESE_SPEAKERS.get(spk_id, r[1].strip())
            w.writerow([spk_id, name])

    # 4. scene_titles.csv
    with open(os.path.join(TEMPLATE_DIR, "scene_titles.csv"), "r", encoding="utf-8") as tf:
        tmpl_titles = list(csv.reader(tf))[1:]

    with open(os.path.join(ZH_DIR, "scene_titles.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["SCENE_ID", "TITLE"])
        for r in tmpl_titles:
            sc_id = r[0].strip()
            sc_data = raw_data.get("scenes", {}).get(sc_id, {})
            title = sc_data.get("title", "").strip() or r[1].strip()
            w.writerow([sc_id, title])

    # 5. toasts.csv
    with open(os.path.join(TEMPLATE_DIR, "toasts.csv"), "r", encoding="utf-8") as tf:
        tmpl_toasts = list(csv.reader(tf))[1:]

    raw_toasts = raw_data.get("toasts", {})
    with open(os.path.join(ZH_DIR, "toasts.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["TOAST_KEY", "TEXT"])
        for r in tmpl_toasts:
            k = r[0].strip()
            t = raw_toasts.get(k, r[1].strip())
            w.writerow([k, t])

    # 6. ores.csv
    with open(os.path.join(TEMPLATE_DIR, "ores.csv"), "r", encoding="utf-8") as tf:
        tmpl_ores = list(csv.reader(tf))[1:]

    raw_ores = raw_data.get("ores", {})
    with open(os.path.join(ZH_DIR, "ores.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ORE_ID", "TITLE", "DESCRIPTION"])
        for r in tmpl_ores:
            oid = r[0].strip()
            ore_item = raw_ores.get(oid, {})
            otitle = ore_item.get("title", r[1].strip())
            odesc = ore_item.get("description", r[2].strip())
            w.writerow([oid, otitle, odesc])

    # 7. bgm.csv
    with open(os.path.join(TEMPLATE_DIR, "bgm.csv"), "r", encoding="utf-8") as tf:
        tmpl_bgm = list(csv.reader(tf))[1:]

    with open(os.path.join(ZH_DIR, "bgm.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["TRACK_ID", "TITLE"])
        for r in tmpl_bgm:
            w.writerow(r)

    # 8. scenarios/*.csv
    tmpl_sc_dir = os.path.join(TEMPLATE_DIR, "scenarios")
    scenes_processed = 0
    for fn in sorted(os.listdir(tmpl_sc_dir)):
        if not fn.endswith(".csv"):
            continue
        sc_id = fn[:-4]
        with open(os.path.join(tmpl_sc_dir, fn), "r", encoding="utf-8") as f:
            tmpl_rows = list(csv.reader(f))[1:]

        cn_dlgs = raw_data.get("scenes", {}).get(sc_id, {}).get("dialogues", [])
        diff = len(tmpl_rows) - len(cn_dlgs)

        aligned_rows = []
        if diff == 0:
            for i in range(len(tmpl_rows)):
                spk = cn_dlgs[i][1] if i < len(cn_dlgs) else tmpl_rows[i][1]
                txt = cn_dlgs[i][2] if i < len(cn_dlgs) else tmpl_rows[i][2]
                aligned_rows.append([tmpl_rows[i][0], spk, txt])
        else:
            candidates = []
            for i in range(1, len(tmpl_rows)):
                same_spk = tmpl_rows[i][1] == tmpl_rows[i - 1][1]
                sc = score_continuation(tmpl_rows[i - 1][2], tmpl_rows[i][2], same_spk)
                candidates.append((sc, i))
            candidates.sort(key=lambda x: x[0], reverse=True)
            chosen_conts = set(x[1] for x in candidates[:diff])

            cn_idx = 0
            for i in range(len(tmpl_rows)):
                if i in chosen_conts:
                    prev_spk, prev_txt = aligned_rows[-1][1], aligned_rows[-1][2]
                    p1, p2 = split_chinese_line(prev_txt)
                    aligned_rows[-1][2] = p1
                    aligned_rows.append([tmpl_rows[i][0], prev_spk, p2])
                else:
                    if cn_idx < len(cn_dlgs):
                        aligned_rows.append([tmpl_rows[i][0], cn_dlgs[cn_idx][1], cn_dlgs[cn_idx][2]])
                        cn_idx += 1
                    else:
                        aligned_rows.append([tmpl_rows[i][0], tmpl_rows[i][1], "......"])

        # Write aligned scenario
        out_sc_path = os.path.join(sc_out_dir, fn)
        with open(out_sc_path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ID", "SPEAKER", "TEXT"])
            for r in aligned_rows:
                w.writerow(r)
        scenes_processed += 1

    print(f"[*] Processed {scenes_processed} scenario files.")

    # 9. osis.csv
    build_osis(os.path.join(ZH_DIR, "osis.csv"))

    # 10. ui.csv
    build_ui(os.path.join(ZH_DIR, "ui.csv"))

    print("[OK] Finished building all Chinese locale files.")


def build_osis(out_path: str):
    with open(os.path.join(TEMPLATE_DIR, "osis.csv"), "r", encoding="utf-8") as tf:
        tmpl_osis = list(csv.reader(tf))[1:]

    ocr_json_path = os.path.join(os.path.dirname(__file__), "cn_osis_ocr.json")
    ocr_global = {}
    ocr_scene = {}
    if os.path.isfile(ocr_json_path):
        with open(ocr_json_path, "r", encoding="utf-8") as f:
            ocr_data = json.load(f)
            ocr_global = ocr_data.get("global", {})
            ocr_scene = ocr_data.get("scene", {})

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["KEY", "STYLE", "TEXT"])
        for r in tmpl_osis:
            k = r[0].strip()
            style = r[1].strip()
            text_en = r[2].strip()

            # 1. Check scene-specific OCR
            text_zh = ocr_scene.get(k, "")
            if not text_zh:
                # 2. Check global asset OCR
                asset = k.split(":")[1] if ":" in k else k
                text_zh = ocr_global.get(asset, "")
            if not text_zh:
                text_zh = text_en
            w.writerow([k, style, text_zh])
    print(f"[*] Generated {out_path} ({len(tmpl_osis)} rows)")


def build_ui(out_path: str):
    # Load core translations from oreimo/translations/ui_translations.csv
    core_csv_path = "/home/andre/Documents/oreimo/translations/ui_translations.csv"
    core_ui = {}
    if os.path.isfile(core_csv_path):
        with open(core_csv_path, "r", encoding="utf-8") as f:
            for r in csv.reader(f):
                if len(r) >= 4:
                    core_ui[r[0].strip()] = {"ru": r[1], "en": r[2], "ja": r[3]}

    with open(os.path.join(TEMPLATE_DIR, "ui.csv"), "r", encoding="utf-8") as tf:
        tmpl_ui = list(csv.reader(tf))[1:]

    # Dedicated UI translation map for Godot UI keys
    UI_MAP = {
        "COMMON_YES": "是",
        "COMMON_NO": "否",
        "COMMON_CANCEL": "取消",
        "COMMON_CONFIRM": "确认",
        "COMMON_CLOSE": "关闭",
        "COMMON_BACK": "返回",
        "COMMON_OK": "确定",
        "COMMON_RESET": "重置",
        "COMMON_SAVE": "保存",
        "COMMON_LOAD": "读取",
        "COMMON_EMPTY": "空",
        "COMMON_NO_DATA": "无数据",
        "COMMON_SELECT": "选择",
        "COMMON_WARNING": "警告",
        "COMMON_ERROR": "错误",
        "COMMON_ACTION": "操作",
        "COMMON_PAGE": "页码",
        "COMMON_MENU": "菜单",
        "COMMON_TAP": "轻触",
        "COMMON_OPTION": "选项",
        "COMMON_SETTINGS": "设置",
        "COMMON_QUIT": "退出",
        "MENU_CONTINUE": "继续游戏",
        "MENU_CONTINUE_SUB": "つづきから",
        "MENU_NEW_GAME": "开始新游戏",
        "MENU_NEW_GAME_SUB": "はじめから",
        "MENU_LOAD": "读取游戏",
        "MENU_LOAD_SUB": "セーブデータ",
        "MENU_SETTINGS": "系统设置",
        "MENU_SETTINGS_SUB": "せってい",
        "MENU_EXTRA": "特别内容",
        "MENU_EXTRA_SUB": "おまけ",
        "MENU_QUIT": "退出游戏",
        "MENU_QUIT_SUB": "しゅうりょう",
        "SETTINGS_TAB_SYSTEM": "系统",
        "SETTINGS_TAB_AUDIO": "音频",
        "SETTINGS_TAB_DISPLAY": "画面",
        "SETTINGS_TAB_NOVEL": "阅读",
        "SETTINGS_TAB_CONTROLS": "控制",
        "SETTINGS_LANGUAGE_TITLE": "语言与本地化",
        "SETTINGS_LANGUAGE_DESC": "管理和切换游戏语言包，支持热重载",
        "SETTINGS_BASE_DISC_TITLE": "基础游戏光盘 (BYOG)",
        "SETTINGS_BASE_DISC_DESC": "选择游戏默认运行所基于的原始光盘语言",
        "SETTINGS_COMMUNITY_PACKS_TITLE": "社区汉化与语言包",
        "SETTINGS_COMMUNITY_PACKS_DESC": "下载并激活社区制作的翻译包",
        "SETTINGS_INSTALLED_BADGE": "已安装",
        "SETTINGS_ACTIVE_BADGE": "使用中",
        "SETTINGS_DOWNLOAD_BTN": "下载",
        "SETTINGS_INSTALL_BTN": "安装",
        "SETTINGS_UNINSTALL_BTN": "卸载",
        "SETTINGS_UPDATE_AVAILABLE": "有新版本可用",
        "SETTINGS_UP_TO_DATE": "已是最新版本",
        "SETTINGS_TEXTURE_PACKS_TITLE": "高清与4K材质增强包",
        "SETTINGS_TEXTURE_PACKS_DESC": "管理AI超分辨率高清材质包",
        "SETTINGS_TEXTURE_PACKS_BTN": "材质包管理...",
        "SETTINGS_HOT_RELOAD_TOAST": "语言包已成功切换至：%s",
        "SETTINGS_AUDIO_BGM_VOL": "背景音乐音量 (BGM)",
        "SETTINGS_AUDIO_SE_VOL": "音效音量 (SE)",
        "SETTINGS_AUDIO_VOICE_VOL": "语音音量 (Voice)",
        "SETTINGS_AUDIO_MASTER_VOL": "主音量",
        "SETTINGS_DISPLAY_MODE": "显示模式",
        "SETTINGS_DISPLAY_FULLSCREEN": "全屏模式",
        "SETTINGS_DISPLAY_WINDOWED": "窗口模式",
        "SETTINGS_DISPLAY_BORDERLESS": "无边框全屏",
        "SETTINGS_VSYNC": "垂直同步 (V-Sync)",
        "SETTINGS_RENDER_SCALE": "渲染缩放",
        "SETTINGS_TEXT_SPEED": "文字显示速度",
        "SETTINGS_AUTO_SPEED": "自动阅读等待时间",
        "SAVELOAD_SAVE_TITLE": "存档",
        "SAVELOAD_LOAD_TITLE": "读档",
        "SAVELOAD_QUICK_SAVE": "快速存档",
        "SAVELOAD_QUICK_LOAD": "快速读档",
        "SAVELOAD_AUTO_SAVE": "自动存档",
        "SAVELOAD_SLOT": "存档位 %02d",
        "SAVELOAD_EMPTY_SLOT": "空白存档位",
        "SAVELOAD_CONFIRM_OVERWRITE": "确定要覆盖当前存档吗？",
        "SAVELOAD_CONFIRM_LOAD": "确定要读取该存档吗？未保存的进度将会丢失。",
        "SAVELOAD_DELETE": "删除存档",
        "SAVELOAD_CONFIRM_DELETE": "确定要删除此存档吗？",
        "INGAME_MENU_TITLE": "游戏菜单",
        "INGAME_BACKLOG": "历史记录",
        "INGAME_AUTO": "自动阅读",
        "INGAME_SKIP": "快进跳过",
        "INGAME_QUICK_SAVE": "快速保存",
        "INGAME_QUICK_LOAD": "快速读取",
        "INGAME_SETTINGS": "设置",
        "INGAME_TITLE_RETURN": "返回标题画面",
        "INGAME_CONFIRM_QUIT_TITLE": "返回标题画面",
        "INGAME_CONFIRM_QUIT_DESC": "确定要返回标题画面吗？未保存的进度将会丢失。",
        "ROUTE_AKYO": "序章・相逢之章",
        "ROUTE_BKIR": "桐乃篇",
        "ROUTE_CKUR": "黑猫篇",
        "ROUTE_DSAO": "沙织篇",
        "ROUTE_EMAN": "麻奈实篇",
        "ROUTE_FAYA": "绫濑篇",
        "ROUTE_GIFG": "加奈子篇",
        "ROUTE_HSEI": "濑菜篇",
        "ROUTE_IYAN": "真妹篇",
        "HEROINE_KIRINO": "高坂桐乃",
        "HEROINE_KURONEKO": "五更瑠璃 (黑猫)",
        "HEROINE_AYASE": "新垣绫濑",
        "HEROINE_SAORI": "槙岛沙织",
        "HEROINE_MANAMI": "田村麻奈实",
        "HEROINE_KANAKO": "来栖加奈子",
        "HEROINE_SENA": "赤城濑菜",
    }

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["KEY", "TEXT"])
        for r in tmpl_ui:
            k = r[0].strip()
            # If explicit Chinese translation exists in UI_MAP, use it
            if k in UI_MAP:
                val = UI_MAP[k]
            else:
                # Use core Japanese or English text
                core_entry = core_ui.get(k, {})
                ja_txt = core_entry.get("ja", "").strip()
                en_txt = core_entry.get("en", "").strip() or r[1].strip()
                val = en_txt
            w.writerow([k, val])
    print(f"[*] Generated {out_path} ({len(tmpl_ui)} keys)")


if __name__ == "__main__":
    main()
