# gen-test-cases 未來擴充計畫

記錄目前實作後觀察到的可擴充方向，供後續迭代參考。

---

## 一、情境模板擴充

目前支援：新增整合項目（服務商 / 幣種 / 平台）、其他（一般功能）。

| 情境 | 說明 | 狀態 |
|------|------|------|
| 新增整合項目 | 涵蓋核心功能、資產操作、兌換、Regression、發佈前確認 | ✅ 已實作 |
| 新增 API endpoint | 後端 API 固定 checklist（auth、pagination、error code） | 💡 待規劃 |
| UI 改版 | 前端 UI 異動驗證（RWD、Dark mode、截圖比對） | 💡 待規劃 |

---

## 二、Phase 2 資料來源擴充

| 來源 | 說明 | 狀態 |
|------|------|------|
| ClickUp Task | 讀取 description、留言、sub-tasks、dependencies | ✅ 已實作 |
| GitHub Repo / Local Path | 依 keywords 定向讀取 source code | ✅ 已實作 |
| Slack Thread | 萃取需求決策、邊界討論、排除情境 | ✅ 已實作 |
| GitHub PR diff | 讀取 changed files、新邏輯分支 | ✅ 已實作 |
| ai-plans | 萃取 Scope、Testing strategy、Risks | ✅ 已實作 |
| Figma MCP | 目前只提示使用者設定，尚未納入正式流程 | 🚧 待整合 |

---

## 三、Phase 3 輸出品質

| 項目 | 說明 | 狀態 |
|------|------|------|
| Case ID 自動防重複 | 跨多次 session 產出時，Case ID 可能衝突，需防重機制 | 💡 待規劃 |
| AC 覆蓋率分析 | 產完後自動列出哪些 AC 沒有對應測試案例 | 💡 待規劃 |
| Dev → Verification diff | 同一功能先後跑兩個 phase 時，自動比對兩份文件並標出 Verification phase 新增的 Boundary / Negative Cases，方便 QA 快速掌握擴充範圍 | 💡 待規劃 |
| 輸出精簡模式 | AI 傾向產出完整案例，但實際使用時往往案例過多、難以取捨。可支援「精簡模式」：先展示「預計產出 N 個 Happy Path / M 個 Negative，涵蓋風險點 X、Y、Z」摘要，由使用者確認數量與重點後再展開完整案例，或直接指定每類最多 N 個 | 💡 待規劃 |
| 案例優先級過濾 | 產出完成後，提供「只看 High Priority」的精簡檢視，讓 RD 在時間有限時快速確認關鍵路徑，完整版留給 QA 驗收用 | 💡 待規劃 |

---

## 四、自動化測試程式碼產出

目前 gen-test-cases 明確排除 test code 產出，但手動測試案例的結構（輸入、操作、預期結果）與自動化測試的邏輯高度對應，具備延伸空間。


### 各類型機會評估

| 類型 | 機會 | 前置條件 | 說明 |
|------|------|---------|------|
| Integration Test | 高 | 需讀既有 test 結構作 reference | 手動案例已是 API 測試的自然語言版本，轉換路徑最短 |
| Unit Test | 中高 | 需理解函式內部邏輯 | Phase 2b 已讀 source code，可取得輸入輸出資訊 |
| E2E Test | 中 | 需 selector、環境設定等額外資訊 | 門檻較高，需專案有既有 E2E test 作 reference |

### 狀態

| 項目 | 狀態 |
|------|------|
| Integration Test 產出 | 💡 待規劃 |
| E2E Test 產出 | 💡 待規劃 |

---

## 五、Phase 1 輸入自動化

目前 Phase 1 完全依賴使用者手動填入（PR URL、Task ID、repo path 等），以下是可減少手動輸入的方向：

| 項目 | 說明 | 實作方式 | 狀態 |
|------|------|---------|------|
| 自動偵測當前 branch 的 PR | 使用者不需要提供 PR URL，skill 直接執行 `gh pr view --json number,url,title` 取得當前 branch 的 PR | `gh` CLI（需已登入） | 💡 待規劃 |
| 從 branch 名稱萃取 Task ID | 常見命名慣例如 `feat/abc123-feature-name`，可自動解析末段英數字串作為 ClickUp Task ID 候選，詢問使用者確認後直接帶入 Phase 2a | `git branch --show-current` + regex | 💡 待規劃 |
| 自動偵測 local repo 路徑 | 以 `git rev-parse --show-toplevel` 取得 repo 根目錄，作為 Phase 2b Local Source Code Path 的預設值，省去使用者手動貼路徑 | `git` CLI | 💡 待規劃 |
| 自動偵測 ai-plans 路徑 | repo 根目錄下若存在 `ai-plans/`、`docs/plans/`、`.claude/plans/` 等常見位置，自動列出可用 plan 檔案供選擇 | `find` / `ls` | 💡 待規劃 |

---

## 六、Phase 4 輸出目標擴充

| 目標 | 說明 | 狀態 |
|------|------|------|
| ClickUp Doc | 建立 Doc 並在原 Task 留連結留言 | ✅ 已實作 |
| 本機 Markdown | 寫入指定路徑 | ✅ 已實作 |
| Task Comment | 直接將內容貼至原 Task 的留言，不另開 Doc，減少點擊層數；表格式需降級為條列式以確保渲染正常 | 💡 待規劃 |
| Task Description | 將測試案例附加至原 Task 的 description 末尾；需注意不覆蓋既有 AC／需求內容 | 💡 待規劃 |
