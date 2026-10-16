#!/usr/bin/env python3
"""
skill_indexer.py
Skill Indexer & Validation Engine for skill-conductor.

Scans the skills directory, extracts metadata from SKILL.md files,
computes manifest hashes, and generates/validates references/skills_index.json.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Windows 控制台編碼相容性處理 (避免 cp950 編碼異常)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
    HAS_PYYAML = True
except ImportError:
    HAS_PYYAML = False


def get_skills_root() -> Path:
    """動態推算 skills 根目錄：本腳本位於 <skills_root>/skill-conductor/scripts/"""
    return Path(__file__).resolve().parent.parent.parent


def get_index_path() -> Path:
    """索引檔案存放位置：<skills_root>/skill-conductor/references/skills_index.json"""
    return Path(__file__).resolve().parent.parent / "references" / "skills_index.json"


def fallback_parse_frontmatter(content: str) -> Dict[str, Any]:
    """
    當環境未安裝 PyYAML 時的健壯後備 Frontmatter 解析器。
    精確處理 description: >、description: | 與單行/多行縮排欄位，
    絕不將描述欄位單純解析為 '>' 或 '|' 字元。
    """
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", content, re.DOTALL)
    if not match:
        return {}

    raw_yaml = match.group(1)
    lines = raw_yaml.splitlines()
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    multiline_buf: List[str] = []
    multiline_mode: Optional[str] = None  # '>' or '|'

    def flush_multiline():
        nonlocal current_key, multiline_buf, multiline_mode
        if current_key and multiline_buf:
            if multiline_mode == ">":
                # 折疊多行為單行空白相連
                val = " ".join(line.strip() for line in multiline_buf if line.strip())
            else:
                val = "\n".join(multiline_buf).rstrip()
            data[current_key] = val
        multiline_buf = []
        multiline_mode = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 檢測鍵值對行
        key_match = re.match(r"^([a-zA-Z0-9_\-]+)\s*:\s*(.*)$", line)
        if key_match:
            flush_multiline()
            key = key_match.group(1).strip()
            rest = key_match.group(2).strip()

            if rest in (">", ">-", "|", "|-"):
                current_key = key
                multiline_mode = ">" if rest.startswith(">") else "|"
                multiline_buf = []
            else:
                current_key = key
                val = rest.strip("\"'")
                data[key] = val
        else:
            # 延續上一行的多行縮排
            if current_key and (line.startswith("  ") or line.startswith("\t")):
                multiline_buf.append(line.strip())

    flush_multiline()
    return data


def parse_frontmatter(content: str) -> Dict[str, Any]:
    """優先使用 PyYAML，若無則降級使用 fallback 解析器"""
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", content, re.DOTALL)
    if not match:
        return {}

    frontmatter_text = match.group(1)
    if HAS_PYYAML:
        try:
            parsed = yaml.safe_load(frontmatter_text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    return fallback_parse_frontmatter(content)


def scan_skills(skills_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    掃描 skills 目錄下所有包含 SKILL.md 的資料夾。
    強制排除 skill-conductor 本身。
    遇到解析錯誤時記錄警告並跳過，不中斷整體索引。
    """
    skills_map: Dict[str, Dict[str, Any]] = {}

    if not skills_root.exists() or not skills_root.is_dir():
        print(f"❌ 錯誤：找不到 skills 根目錄：{skills_root}", file=sys.stderr)
        return skills_map

    for entry in sorted(skills_root.iterdir()):
        if not entry.is_dir():
            continue

        skill_dir_name = entry.name
        # 排除 skill-conductor 自己
        if skill_dir_name in ("skill-conductor", ".git"):
            continue

        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue

        try:
            content = skill_file.read_text(encoding="utf-8")
            mtime = round(skill_file.stat().st_mtime, 3)
            meta = parse_frontmatter(content)

            name = meta.get("name") or skill_dir_name
            raw_desc = meta.get("description") or ""
            # 清理折疊符號
            if isinstance(raw_desc, str):
                cleaned_desc = raw_desc.strip()
                if cleaned_desc in (">", "|", ">-", "|-"):
                    cleaned_desc = ""
            else:
                cleaned_desc = str(raw_desc)

            arg_hint = meta.get("argument-hint") or meta.get("argument_hint") or ""

            rel_path = str(skill_file.relative_to(skills_root)).replace("\\", "/")

            skills_map[name] = {
                "name": name,
                "description": cleaned_desc,
                "argument-hint": str(arg_hint),
                "path": rel_path,
                "mtime": mtime
            }
        except Exception as e:
            print(f"⚠️ 警告：解析 {skill_file} 失敗，已跳過：{e}", file=sys.stderr)

    return skills_map


def compute_manifest_hash(skills_map: Dict[str, Dict[str, Any]]) -> str:
    """依據排序後的 (path, mtime) 計算全域 SHA256 雜湊"""
    hasher = hashlib.sha256()
    for name in sorted(skills_map.keys()):
        item = skills_map[name]
        data_str = f"{item['path']}:{item['mtime']}"
        hasher.update(data_str.encode("utf-8"))
    return hasher.hexdigest()


def run_reindex(skills_root: Path, index_file: Path) -> int:
    """重建索引檔"""
    skills_map = scan_skills(skills_root)
    manifest_hash = compute_manifest_hash(skills_map)

    payload = {
        "version": "1.0.0",
        "manifest_hash": manifest_hash,
        "indexed_count": len(skills_map),
        "skills": skills_map
    }

    index_file.parent.mkdir(parents=True, exist_ok=True)
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"✅ 成功完成索引建置：共收錄 {len(skills_map)} 個技能至 {index_file}")
    print(f"🔑 Manifest SHA256: {manifest_hash}")
    return 0


def run_check(skills_root: Path, index_file: Path) -> int:
    """比對實體目錄狀態與現有索引檔的一致性"""
    if not index_file.is_file():
        print(f"❌ 錯誤：找不到索引檔 {index_file}，請先執行 --reindex！", file=sys.stderr)
        return 1

    try:
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    except Exception as e:
        print(f"❌ 錯誤：無法讀取或解析索引檔：{e}", file=sys.stderr)
        return 1

    indexed_skills: Dict[str, Dict[str, Any]] = index_data.get("skills", {})
    current_skills = scan_skills(skills_root)

    current_names = set(current_skills.keys())
    indexed_names = set(indexed_skills.keys())

    added = current_names - indexed_names
    deleted = indexed_names - current_names

    modified = []
    for name in (current_names & indexed_names):
        curr_mtime = current_skills[name].get("mtime", 0.0)
        idx_mtime = indexed_skills[name].get("mtime", 0.0)
        # 允許 0.001 秒浮點容差
        if abs(curr_mtime - idx_mtime) > 0.002:
            modified.append(name)

    is_mismatch = bool(added or deleted or modified)
    if is_mismatch:
        print("❌ 檢查失敗：技能庫現狀與索引檔不一致！", file=sys.stderr)
        if added:
            print(f"  [+] 新增的技能 ({len(added)}): {', '.join(sorted(added))}")
        if deleted:
            print(f"  [-] 已刪除的技能 ({len(deleted)}): {', '.join(sorted(deleted))}")
        if modified:
            print(f"  [*] 檔案變更的技能 ({len(modified)}): {', '.join(sorted(modified))}")
        return 1

    current_hash = compute_manifest_hash(current_skills)
    saved_hash = index_data.get("manifest_hash", "")
    if current_hash != saved_hash:
        print(f"❌ 檢查失敗：Manifest Hash 不相符！(Current: {current_hash}, Saved: {saved_hash})", file=sys.stderr)
        return 1

    print(f"✅ 檢查通過：索引完全一致！共 {len(current_skills)} 個技能已同步，無任何差異。")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Skill Indexer for skill-conductor")
    parser.add_argument("--reindex", action="store_true", help="強制重新掃描並建立索引")
    parser.add_argument("--check", action="store_true", help="比對現狀與索引檔一致性")
    args = parser.parse_args()

    skills_root = get_skills_root()
    index_file = get_index_path()

    if args.check:
        sys.exit(run_check(skills_root, index_file))
    else:
        # 預設行為（不帶參數或帶 --reindex）等同 --reindex
        sys.exit(run_reindex(skills_root, index_file))


if __name__ == "__main__":
    main()
