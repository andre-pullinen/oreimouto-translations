#!/usr/bin/env python3
"""
Godot PCK v4 Builder for OreImouto Language Packs.
Pure-Python, zero external dependencies. Produces 100% valid Godot 4.3+ PCK packages.
Matches Godot engine PckPacker binary specification.
"""

import argparse
import hashlib
import json
import os
import struct
import sys
from typing import List, Tuple

PACK_HEADER_MAGIC = 0x43504447  # 'GDPC'
PACK_FORMAT_VERSION = 4
PACK_REL_FILEBASE = 2
PCK_ALIGNMENT = 32


def get_pad(alignment: int, pos: int) -> int:
    rem = pos % alignment
    return 0 if rem == 0 else alignment - rem


def build_pck(source_dir: str, output_pck_path: str, locale: str = None) -> Tuple[bool, str, int, str]:
    """
    Packs a locale directory into a Godot PCK format 4 file.
    All files are mounted under res://assets/data/lang/<locale>/...
    Returns (success, message, file_count, sha256_hash).
    """
    if not os.path.isdir(source_dir):
        return False, f"Source directory not found: {source_dir}", 0, ""

    # Detect locale from manifest.json or folder name
    if not locale:
        manifest_json_path = os.path.join(source_dir, "manifest.json")
        if os.path.isfile(manifest_json_path):
            try:
                with open(manifest_json_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                    locale = manifest.get("locale")
            except Exception:
                pass
        if not locale:
            locale = os.path.basename(os.path.normpath(source_dir)).lower()

    locale = locale.strip().lower()
    if not locale:
        return False, "Could not determine locale code", 0, ""

    # Gather files
    files_to_pack: List[Tuple[str, str]] = []  # (vfs_path, disk_path)
    for root, _, files in os.walk(source_dir):
        for file in sorted(files):
            if file.startswith("."):
                continue
            disk_path = os.path.join(root, file)
            rel_path = os.path.relpath(disk_path, source_dir).replace("\\", "/")
            vfs_path = f"res://assets/data/lang/{locale}/{rel_path}"
            files_to_pack.append((vfs_path, disk_path))

    if not files_to_pack:
        return False, f"No files found to pack in {source_dir}", 0, ""

    # Sort entries by VFS path for determinism
    files_to_pack.sort(key=lambda x: x[0])

    # Read all file contents and compute MD5
    file_records: List[Tuple[str, bytes, bytes]] = []  # (vfs_path, content, md5)
    for vfs_path, disk_path in files_to_pack:
        with open(disk_path, "rb") as f:
            content = f.read()
        md5_digest = hashlib.md5(content).digest()
        file_records.append((vfs_path, content, md5_digest))

    os.makedirs(os.path.dirname(os.path.abspath(output_pck_path)), exist_ok=True)

    with open(output_pck_path, "wb") as f:
        # 1. Header (104 bytes)
        # magic (4), fmt (4), maj (4), min (4), pat (4), flags (4), file_base (8), dir_offset (8), reserved (64)
        file_base = 128  # 104 aligned to 32 bytes = 128
        dir_offset_pos = 32

        hdr = struct.pack(
            "<IIIIIIQQ64s",
            PACK_HEADER_MAGIC,
            PACK_FORMAT_VERSION,
            4,  # major
            7,  # minor
            2,  # patch
            PACK_REL_FILEBASE,
            file_base,
            0,  # dir_offset placeholder (updated at end)
            b"\x00" * 64,
        )
        f.write(hdr)
        # Pad to file_base (128 bytes)
        hdr_pad = file_base - len(hdr)
        if hdr_pad > 0:
            f.write(b"\x00" * hdr_pad)

        # 2. Write file payloads
        entries_meta = []  # (vfs_path, rel_ofs, size, md5)
        for vfs_path, content, md5_digest in file_records:
            cur_pos = f.tell()
            rel_ofs = cur_pos - file_base
            f.write(content)
            entries_meta.append((vfs_path, rel_ofs, len(content), md5_digest))
            # Align next file to 32 bytes
            pad = get_pad(PCK_ALIGNMENT, f.tell())
            if pad > 0:
                f.write(b"\x00" * pad)

        # 3. Directory
        dir_offset = f.tell()
        dir_buf = bytearray()
        dir_buf.extend(struct.pack("<I", len(entries_meta)))

        for vfs_path, rel_ofs, size, md5_digest in entries_meta:
            path_bytes = vfs_path.encode("utf-8")
            s_len = len(path_bytes)
            pad_str = get_pad(4, s_len)
            total_str_len = s_len + pad_str

            dir_buf.extend(struct.pack("<I", total_str_len))
            dir_buf.extend(path_bytes)
            if pad_str > 0:
                dir_buf.extend(b"\x00" * pad_str)

            dir_buf.extend(struct.pack("<QQ16sI", rel_ofs, size, md5_digest, 0))

        f.write(dir_buf)

        # 4. Update dir_offset in header
        f.seek(dir_offset_pos)
        f.write(struct.pack("<Q", dir_offset))

    # Calculate SHA-256 of the generated PCK
    sha256 = hashlib.sha256()
    with open(output_pck_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    sha256_hex = sha256.hexdigest()

    return True, f"Successfully built {output_pck_path}", len(file_records), sha256_hex


def main():
    parser = argparse.ArgumentParser(description="Godot 4.x PCK Builder for OreImouto Translations")
    parser.add_argument("source_dir", help="Path to locale directory (e.g. locales/ru)")
    parser.add_argument("-o", "--output", help="Output PCK file path (default: dist/lang_<locale>.pck)")
    parser.add_argument("--locale", help="Override locale code (e.g. 'ru', 'en')")
    args = parser.parse_args()

    out = args.output
    if not out:
        loc = args.locale or os.path.basename(os.path.normpath(args.source_dir)).lower()
        out = os.path.join("dist", f"lang_{loc}.pck")

    success, msg, count, sha = build_pck(args.source_dir, out, args.locale)
    if success:
        pck_size = os.path.getsize(out)
        print(f"[OK] {msg}")
        print(f"     Files:    {count}")
        print(f"     Size:     {pck_size:,} bytes")
        print(f"     SHA-256:  {sha}")
        sys.exit(0)
    else:
        print(f"[ERROR] {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
