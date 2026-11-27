# qa-intel 使用說明（最小版）

安裝見 [README](README.md#安裝)。更多情境（輸入組合、降級模式、各種來源）見 [docs/scenarios.html](docs/scenarios.html)，用瀏覽器開啟。

## 三個指令

| 指令 | 最小輸入 | 產出 |
|------|---------|------|
| `/repo-scout` | 本機 repo 路徑；模式選 Quick（3k–8k token）或 Comprehensive | `~/.qa-intel/knowledge/repos/<repo>.md` |
| `/risk-analyzer` | PR URL 或 branch；有 ClickUp Task ID 則多一份 AC 覆蓋分析 | 風險報告（🔴🟡🟢）、建議測試重點、部署檢查清單 |
| `/gen-test-cases` | ClickUp Task ID，或直接貼需求；再選 Development / Verification | 手動測試案例，確認後寫成 ClickUp Doc 或本機 Markdown |

建議順序：新 repo 先 `/repo-scout`；開發中或 merge 前 `/risk-analyzer`；測試前 `/gen-test-cases`。
`/risk-analyzer` 的「建議測試重點」目前需要你手動帶入 `/gen-test-cases`（尚未自動銜接）。

## 先決條件

| 情境 | 需要 |
|------|------|
| 讀取 ClickUp 票卡 | ClickUp MCP，或 `CLICKUP_TOKEN` / `CLICKUP_WORKSPACE_ID` |
| 分析 private repo 的 PR | `gh` 已登入，並提供本機 repo 路徑 |
| 沒有票卡 | 直接貼需求，輸出到本機檔案即可 |

## 常見狀況

- **risk-analyzer 說找不到知識庫**：先跑 `/repo-scout`，或選擇「仍要繼續」（品質會降低）。知識庫路徑可用環境變數 `QA_INTEL_HOME` 改變。
- **舊版知識庫在別的位置**：手動搬到 `~/.qa-intel/knowledge/repos/`。
- **ClickUp 寫入失敗**：gen-test-cases 會降級為純文字留言；也可改為只輸出本機 Markdown。

## 尚未支援

Jira / Linear、`project.md` 專案配置、自訂模板、跨 repo 同時分析。
