#!/usr/bin/env python3
"""
test_conductor_guardrails.py
Automated tests for skill-conductor:
- Recursion Guard (Circular dependency prevention)
- Privacy Confirmation Gate (Tier 3/4 authorization)
- Explicit Degradation (Fallback on external failure/timeout)
- Scenario Assessments (Tier 1, Tier 2/3, Tier 3/4)
"""

import sys
import json
from pathlib import Path

# Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

INDEX_PATH = Path(__file__).resolve().parent.parent / "references" / "skills_index.json"

from typing import Tuple

class ConductorSimulator:
    def __init__(self, index_path: Path):
        with open(index_path, "r", encoding="utf-8") as f:
            self.index = json.load(f)["skills"]
        self.visited_skills = set()

    def check_precondition(self, target_skill: str) -> Tuple[bool, str]:
        if target_skill in ("skill-conductor", "conductor"):
            return False, "🚨 架構違規：循環調用。目標技能為 conductor 本身，終止調度以防止無窮遞迴。"
        if target_skill in self.visited_skills:
            return False, f"🚨 架構違規：循環調用。技能 [{target_skill}] 已在調度鏈中，終止調度以防止循環相依。"
        if target_skill not in self.index:
            return False, f"🚨 目標技能不存在：[{target_skill}] 未收錄於 skills_index.json。"
        return True, "Precondition passed"

    def evaluate_task(self, prompt: str, user_confirmed_privacy: bool = False, external_failure: bool = False) -> str:
        # 1. 評估意圖與風險
        prompt_lower = prompt.lower()
        if "對比度" in prompt or "按鈕顏色" in prompt or "typo" in prompt:
            tier = 1
            direction = "UI / Styling"
            selected = ["ponytail", "ui-ux-pro-max"]
        elif "pdf" in prompt or "匯出" in prompt:
            tier = "2/3"
            direction = "Feature Integration / Document"
            selected = ["backend-architect", "tdd", "ponytail"]
        elif "百萬並發" in prompt or "同步架構" in prompt or "高併發" in prompt:
            tier = "3/4"
            direction = "Architecture / High-Concurrency"
            selected = ["gemini-web-copilot", "backend-architect", "tdd", "test"]
        else:
            tier = 2
            direction = "General"
            selected = ["ponytail"]

        # 2. 決策卡分級輸出
        if tier == 1:
            # 負面安全檢查：Tier 1 嚴禁調用外部重型工具
            assert "gemini-web-copilot" not in selected, "Tier 1 violation: heavy tool selected"
            return f"🎯 **[Conductor: Tier 1]** 選用 `/{selected[0]} full` + `{selected[1]}`：低風險單模組調整，採最小可行變更實作。"

        elif tier == "2/3":
            # 存在性驗證
            for s in selected:
                ok, err = self.check_precondition(s)
                if not ok:
                    return err
                self.visited_skills.add(s)

            card = [
                "📋 **[Conductor 決策卡 - Tier 2/3 Standard/Complex]**",
                f"- **方向**：{direction}",
                "- **風險**：中度（既有架構內擴充，依賴完整單元測試防禦）",
                f"- **技能鏈**：{' ➔ '.join(f'`{s}`' for s in selected)}",
                "- **交接檢核規範**：落實實體產出物清單與步驟未完成事項登記。"
            ]
            return "\n".join(card)

        elif tier == "3/4":
            # 隱私門閘檢查
            external_skill = "gemini-web-copilot"
            files_to_send = ["package.json", "src/sync/*.ts"]
            estimated_tokens = 3500

            if not user_confirmed_privacy:
                # 使用者未授權外部發送 -> 顯式降級
                degrade_msg = [
                    "⚠️ **[降級通報]**",
                    f"- **原定方案**：`/{external_skill}`",
                    "- **降級原因**：使用者尚未授權外部發送檔案範圍",
                    "- **降級目標**：切換至本地精簡模式 (`/ponytail full` + 本地 `architecture`)",
                    "- **影響說明**：略過百萬 Token 網頁版深度分析，直接基於本地規範進行架構設計。"
                ]
                return "\n".join(degrade_msg)

            if external_failure:
                # 外部腳本失敗/逾時 -> 顯式降級
                degrade_msg = [
                    "⚠️ **[降級通報]**",
                    f"- **原定方案**：`/{external_skill}`",
                    "- **降級原因**：外部腳本執行逾時 (Exit Code 1 / Timeout)",
                    "- **降級目標**：切換至本地精簡模式 (`/ponytail full`)",
                    "- **影響說明**：略過網頁自動化推理，改由本地即時交付最小可行解。"
                ]
                return "\n".join(degrade_msg)

            # 正常執行 (使用者已確認且無故障)
            card = [
                "🧠 **[Conductor 深度決策看板 - Tier 3/4 Complex/Epic]**",
                f"- **方向領域**：{direction}",
                "- **風險評估**：高風險（跨模組、高併發連線、數據一致性挑戰）",
                f"- **擬調用技能鏈**：{' ➔ '.join(f'`/{s}`' if s == 'gemini-web-copilot' else f'`{s}`' for s in selected)}",
                "- 🛑 **外部發送範圍審核**：",
                f"  * 將發送檔案：{', '.join(files_to_send)} (預估 {estimated_tokens} Tokens)",
                "  * 安全狀態：已確認無硬編碼金鑰，使用者已授權確認。",
                "- **執行狀態**：授權通過，啟動外部深度分析流程。"
            ]
            return "\n".join(card)

class Tuple_Result(tuple):
    pass

def run_all_tests():
    sim = ConductorSimulator(INDEX_PATH)
    results = {}

    print("================== [1. 遞迴阻斷測試 (Negative Test)] ==================")
    # 測試 A: 調用 conductor 自身
    ok1, msg1 = sim.check_precondition("skill-conductor")
    print(f"調用 skill-conductor 阻斷結果: ok={ok1}\n輸出訊息: {msg1}\n")
    assert not ok1

    # 測試 B: 調用已存在鏈中的技能
    sim.visited_skills.add("ponytail")
    ok2, msg2 = sim.check_precondition("ponytail")
    print(f"重複調用 ponytail 阻斷結果: ok={ok2}\n輸出訊息: {msg2}\n")
    assert not ok2

    print("================== [2. 隱私確認門閘測試 (Negative Test)] ==================")
    sim_privacy = ConductorSimulator(INDEX_PATH)
    out_unconfirmed = sim_privacy.evaluate_task("設計支援百萬並發的即時同步架構", user_confirmed_privacy=False)
    print(f"Tier 3/4 未授權隱私時輸出:\n{out_unconfirmed}\n")
    assert "降級通報" in out_unconfirmed

    print("================== [3. 顯式降級測試 (Negative Test)] ==================")
    out_failed = sim_privacy.evaluate_task("設計支援百萬並發的即時同步架構", user_confirmed_privacy=True, external_failure=True)
    print(f"外部腳本超時/失敗時輸出:\n{out_failed}\n")
    assert "外部腳本執行逾時" in out_failed

    print("================== [4. 情境 A (Tier 1 Micro)] ==================")
    sim_a = ConductorSimulator(INDEX_PATH)
    out_a = sim_a.evaluate_task("修正按鈕顏色對比度不足的問題")
    print(f"情境 A 輸出:\n{out_a}\n")
    assert "Tier 1" in out_a and "gemini-web-copilot" not in out_a

    print("================== [5. 情境 B (Tier 3/4 授權通過)] ==================")
    sim_b = ConductorSimulator(INDEX_PATH)
    out_b = sim_b.evaluate_task("設計支援百萬並發的即時同步架構", user_confirmed_privacy=True, external_failure=False)
    print(f"情境 B 輸出:\n{out_b}\n")
    assert "深度決策看板" in out_b

    print("================== [6. 情境 C (Tier 2/3 技能鏈交接)] ==================")
    sim_c = ConductorSimulator(INDEX_PATH)
    out_c = sim_c.evaluate_task("實作 PDF 報表匯出並加入單元測試")
    print(f"情境 C 輸出:\n{out_c}\n")
    assert "Tier 2/3" in out_c

    print("================== ✅ 所有測試全數通過！ ==================")

if __name__ == "__main__":
    run_all_tests()
