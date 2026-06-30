---
name: gen-test-cases
description: 從票卡（ClickUp / Jira / Linear）或需求描述，分析功能並產出結構化手動測試案例清單，支援 Development phase（開發中，輕量）與 Verification phase（測試/驗收，完整）兩種模式。輸出為 Markdown 或回寫至 Scrum Tool。當使用者說「幫我產生測試案例」、「列出測試項目」、「這個功能怎麼測」、「分析測試點」、「gen test cases」、「建立測試計畫」，或提供 Task ID 並要求建立測試計畫時觸發。尚未適用於撰寫測試程式碼。
---

# gen-test-cases

分析需求並產出**手動測試案例**，覆蓋正常流程、邊界條件與負面案例。

---

## 情境模板參考

| 檔案 | 適用情境 |
|------|---------|
| `templates/test-case-spec.md` | 表格式，含 Case ID / 前置條件 / 步驟 / 預期結果（預設） |
| `templates/general-reference.md` | 條列式，適合快速瀏覽或貼入留言 |
| `templates/new-provider-reference.md` | 新增整合項目（服務商、幣種、協議、平台）的通用起點 |

---

## Phase 1 — 收集輸入

詢問使用者以下資訊，**全部確認後**才進入 Phase 2：

### 1a. 需求來源（必選其一）

**選項 A：ClickUp Task ID / URL**
- 解析 Task ID（URL 末段的英數字串，例如 `aj4fu06`）
- 輸出文件將以留言方式回寫至該 Task
- 選填：**是否同時輸出至本機路徑？** 若是，詢問輸出路徑（例如 `docs/test-cases/feature-name.md`）

**選項 B：直接描述需求**
- 請使用者貼上需求文字或功能描述
- 額外詢問：**文件輸出路徑**（例如 `docs/test-cases/feature-name.md`）

### 1b. 補充上下文（選填）

可透過以下五種方式給予補充，可混用，每種都可提供多個：

1. **GitHub Repo URL** — Phase 2b 將以 `WebFetch` 讀取 README 與相關 source code
2. **Local Source Code Path** — Phase 2b 將以 `Read` / `Bash` 讀取本機路徑下的 source code
3. **Slack 對話內容** — 請使用者直接複製貼上相關的 Slack 討論內容，Phase 2c 將從中萃取需求決策、邊界條件討論與具體範例
4. **GitHub PR URL** — Phase 2d 將讀取 PR diff，了解實際程式碼變更的檔案與範圍（例如 `github.com/org/repo/pull/123`）
5. **GitHub Branch URL 或 Local ai-plans Path** — Phase 2e 將讀取指定 branch 或本機路徑下的 ai-plans 資料夾，萃取設計決策、範圍與風險（例如 `github.com/org/repo/tree/feature-branch` 或 `/Users/.../repo/ai-plans`）

若使用者提供 GitHub Repo URL、Local Source Code Path 或 GitHub Branch URL，**當場詢問對應的關鍵字（keywords）**，作為 Phase 2 定向閱讀的依據。每個 path/URL 可分別對應不同 keywords。Slack 對話內容與 GitHub PR URL 不需要 keywords（前者直接讀貼入的文字；後者直接讀 diff）。

若使用者不提供補充上下文，繼續以票卡/需求描述為主要依據。

### 1b-2. 測試案例呈現格式（選填，預設表格式）

詢問使用者希望以哪種格式呈現測試案例。若使用者未指定，預設使用表格式。

**條列式**
- 參考 `templates/general-reference.md`
- 以功能名稱作為區塊標題，每個案例逐行列出
- 適合快速瀏覽、口頭確認、貼入 ClickUp 留言

**表格式**（預設）
- 參考 `templates/test-case-spec.md`
- 每個案例含 Case ID、前置條件、測試步驟、預期結果、優先級、受眾
- 適合正式測試文件、需要追蹤執行結果的情境

Phase 3 與 Phase 4 的輸出格式依此選擇執行，不再切換。

### 1c. 測試階段（必選）

詢問使用者目前處於哪個開發階段，決定測試案例的深度與受眾：

**Development phase**
- 受眾：RD
- 目的：確保核心功能可用、重要流程不壞，不追求完整覆蓋
- 產出：Happy Path（核心路徑）+ 關鍵負面案例（會直接打壞主流程的情境）
- 不產出：Boundary Cases、細節 Negative Cases（留待Verification phase補充）

**Verification phase**
- 受眾：QA / All
- 目的：完整覆蓋所有有意義的情境，找出邊界與特殊情境
- 產出：完整三層案例（Happy Path + Boundary + Negative）

---

## Phase 2 — 分析需求

### 2a. 讀取知識庫（自動）

1. 尋找 qa-intel 安裝目錄下的 `knowledge/repos/`（與 `plugin.json` 同層）
2. 列出該目錄下所有 `.md` 檔案
3. 依 Task 標題或使用者描述的功能名稱，判斷最相關的知識檔案
4. 若找到對應檔案，讀取其「核心模組」、「API / 介面」、「已知風險模組」欄位
5. 若 `knowledge/repos/` 不存在或無相關檔案：靜默跳過（不詢問使用者）

知識庫資訊將在 Phase 3 產出測試案例時作為補充背景：
- 識別受影響的模組
- 補充「已知風險模組」對應的測試重點
- 在測試策略摘要中標注「知識庫來源」

### 2b. 讀取需求

**若來源為 ClickUp Task：**
1. 呼叫 `clickup_get_task` 取得完整資訊（title、description、acceptance criteria）
2. 萃取以下項目作為測試設計依據：
   - 功能摘要（這個功能在做什麼）
   - 主要操作流程
   - 限制條件與業務規則
   - 已明確描述的錯誤情境
3. **若 description 含有圖片（ClickUp CDN URL），依序嘗試：**
   1. 使用 `WebFetch` 嘗試直接存取圖片 URL；成功則繼續，失敗則進入下一步
   2. 執行 `echo $CLICKUP_TOKEN` 確認環境變數是否已設定：
      - **已設定**：使用 `curl -s -H "Authorization: $CLICKUP_TOKEN" "<url>" -o /tmp/clickup-img.png` 下載至本機，再用 `Read` 讀取。**不要請使用者在對話中貼出 token 值**
      - **未設定**：告知使用者在 shell profile（`~/.zshrc` 或 `~/.bashrc`）加入以下設定，完成後重新開啟 terminal 再試：
        ```
        export CLICKUP_TOKEN=pk_xxxxx   # 從 ClickUp → Settings → Apps → API Token 取得
        ```
   3. 若 `$CLICKUP_TOKEN` 無法取得，請使用者將圖片儲存至本機並告知路徑，使用 `Read` 讀取（Claude 支援 PNG / JPG 等格式）
   4. 若為 Figma Wireframe，請使用者提供 Figma 專案或 Frame 連結，透過 **Figma MCP**（若已設定）讀取 frame 內容；未設定則請使用者改以截圖提供，或參考 [Figma MCP](https://www.figma.com/developers/mcp) 進行設定
4. 呼叫 `clickup_get_task_comments` 讀取所有留言，萃取：
   - 需求補充說明、AC 追加、設計決策
   - 被明確討論或排除的情境
5. 若留言中有 thread，呼叫 `clickup_get_threaded_comments` 讀取完整討論串
6. 若任務包含 sub-tasks（task 回傳中有 subtask IDs），逐一呼叫 `clickup_get_task` 讀取每個 sub-task，了解子功能範圍；並對每個 sub-task 呼叫 `clickup_get_task_comments` 讀取留言，若留言中有 thread 則呼叫 `clickup_get_threaded_comments` 讀取完整討論串（萃取邏輯同 Step 4–5）
7. 若任務包含 related tasks 或 dependencies（task 回傳的 links / dependencies 欄位），讀取關聯任務標題與描述，了解前後依賴關係

**若來源為直接描述：**
直接使用使用者提供的需求文字。

### 2b. 補充原始碼上下文（若有提供 GitHub Repo 或 Local Path）

**去重原則：** 若某個 GitHub Repo URL 與某個 Local Source Code Path 明顯對應同一個 repo（repo 名稱相同），**優先使用 Local Path，跳過該 GitHub URL**，避免重複讀取相同內容。

依 Phase 1 收集的 keywords 定向閱讀，避免無方向地掃描大量檔案。

**GitHub Repo URL（無對應 Local Path 時）：**
- 使用 `WebFetch` 讀取 README 了解系統架構
- 根據 keywords 讀取對應目錄或檔案

**Local Source Code Path：**
- 使用 `Read` 或 `Bash`（grep、find）根據 keywords 定位相關檔案

整合原始碼資訊，補充票卡/需求描述中未明確說明的系統行為。

### 2c. 讀取 Slack 對話內容（若有提供）

使用者已在 Phase 1b 直接貼入 Slack 討論內容，逐則閱讀，萃取以下內容作為測試設計補充依據：
- 需求決策（「我們決定 X 的行為是…」）
- 討論過的邊界條件或特殊情境
- 具體範例（sample data、截圖說明、使用者提到的特定 case）
- 被排除的情境（「這個 case 我們先不處理」）

### 2d. 讀取 GitHub PR diff（若有提供 GitHub PR URL）

**判斷讀取方式：**

**若使用者同時提供了 Local Source Code Path（與 PR 對應的 repo）：**
- 解析 PR URL 取得 PR number（URL 末段數字）
- 在本機 repo 路徑下執行 `gh pr diff <PR#>` 取得完整 diff
- 補充執行 `gh pr view <PR#> --json title,body,files` 取得 PR description 與 changed files 清單

**若只有 GitHub PR URL（無 local repo）：**
- 使用 `WebFetch` 讀取 `github.com/{owner}/{repo}/pull/{PR#}/files` 取得 changed files 清單
- 使用 `WebFetch` 讀取 PR description（`github.com/{owner}/{repo}/pull/{PR#}`）
- 注意：**private repo 無法透過 WebFetch 讀取**，遇到此情況告知使用者改提供 local repo path

**從 PR diff 萃取以下測試重點：**
- 改動的檔案與模組（定位測試範圍）
- 新增的 API endpoint 或參數（需對應的 Happy Path 案例）
- 新增的邏輯分支或條件判斷（對應需要測的邊界 / 負面案例）
- 刪除或修改的行為（可能影響現有測試的迴歸點）

### 2e. 讀取 ai-plans（若有提供 GitHub Branch URL 或 Local ai-plans Path）

**若提供 GitHub Branch URL：**
- 解析 URL 格式：`github.com/{owner}/{repo}/tree/{branch}`
- 嘗試讀取 ai-plans 資料夾（常見位置：`ai-plans/`、`docs/plans/`、`.claude/plans/`）
- 將 URL 轉換為 raw 格式後以 `WebFetch` 讀取：`raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}`
- 注意：**private repo 無法透過 WebFetch 讀取**，遇到此情況告知使用者改提供 local path

**若提供 Local ai-plans Path：**
- 使用 `Bash`（find、ls）列出資料夾內的 plan 檔案
- 依任務關聯性（task ID、功能名稱）選取最相關的 plan 檔案，以 `Read` 讀取

**從 ai-plans 萃取以下測試重點：**
- **Scope（In / Out）** → 確認哪些在範圍內、哪些明確排除（不測項目直接對應）
- **Testing strategy（Section 8）** → RD 自己預定的測試方向，可直接引用進測試策略摘要
- **Risks & open questions** → 不確定的地方 = 最需要測試、最容易出錯的地方
- **PR Breakdown** → 了解每個 PR 的 focused goal，對應到該測試的改動範圍
- **Done criteria** → 驗收的最低標準，可直接轉換為 Happy Path 的通過條件

### 2f. 情境判斷

根據 Task 標題與 description，判斷屬於以下哪種情境：

- **新增整合項目**：標題或描述含「新增支援」、「add integration」、「新增服務商」、「add provider」等關鍵字 → 套用 `templates/new-provider-reference.md`（條列式，不受 Phase 1b-2 影響）
- **其他**：不符合上述關鍵字 → 依 Phase 1b-2 選擇（預設表格式 `templates/test-case-spec.md`）

判斷完成後，**明確告知使用者判斷結果**：

> 本次判斷情境為「{情境}」，將套用「{模板檔名}」格式輸出。如有不符，請在此告知，我將調整後再繼續。

- 若使用者確認或無異議 → 進入 2g
- 若使用者糾正情境 → 更新情境後再次告知，確認後才繼續

### 2g. 確認資訊完整性

若分析後發現關鍵資訊不足（例如：不清楚主要操作對象、缺少關鍵限制條件），**停下來詢問使用者補充**，不要自行假設後繼續。

---

## Phase 3 — 生成手動測試案例

**若情境為「新增整合項目」：**

直接套用 `templates/new-provider-reference.md`，**跳過 3a–3d 所有步驟**，直接進入 3e 使用者確認。格式固定為條列式，不受 Phase 1b-2 選擇影響。

**若情境為「其他」：**

依 Phase 1b-2 使用者選擇的格式產出：
- **表格式**（預設，使用者未指定時採用）→ 參考 `templates/test-case-spec.md`，以 Markdown Table 呈現，依序執行 3a–3e
- **條列式**（使用者明確選擇時）→ 參考 `templates/general-reference.md`，以功能區塊 + 編號清單呈現，跳過 3a 策略摘要，直接從 3b 開始產出後進入 3e

**表格式輸出格式規定（嚴格遵守，僅適用選項 B）：**
- 測試案例**必須使用 Markdown Table 格式**，欄位順序如下：

  | Case ID | 測試標題 | 前置條件 | 測試步驟 | 預期結果 | 優先級 | 受眾 | 測試結果 |

- **禁止使用**條列（`Case ID: xxx`）、分隔線（`────`）等非 Table 格式輸出案例
- 每格內容若有多點，使用 `<br>` 換行（Markdown Table 不支援真正換行）；**數字清單也必須用 `<br>` 分隔，禁止使用 `\n` 或真正換行**
  - 正確：`1. 登入帳號<br>2. 點擊按鈕<br>3. 確認結果`
  - 錯誤：`1. 登入帳號 2. 點擊按鈕 3. 確認結果`（全擠在同一行）
- 在 chat 中展示（Phase 3e）與最終寫入 ClickUp Doc / 本機檔案（Phase 4）都使用相同的 Table 格式
- **「測試結果」欄位**預設留空，執行測試後由測試人員手動填入，使用以下 HTML 格式：
  - PASS(綠底白字)
  - FAILED(紅底白字)
  - SKIP(黃底黑字)
  - BLOCKED(灰底白字)

### 3a. 測試策略摘要（草稿確認）

基於 Phase 2 的分析，先產出策略摘要初稿並展示給使用者確認，再進入案例產出。

**步驟：**

1. 依 Phase 2 所得資訊，填寫以下摘要初稿：
   - **測試範圍**：明確說明這次測哪些 API / 功能 / 流程
   - **不測項目**：明確排除哪些情境及原因（例如：信任邊界外的第三方服務、已由其他測試覆蓋的路徑）
   - **風險重點**：哪些欄位 / 流程最容易出錯，應優先確認
   - **測試資料**：需要什麼前置條件或測試帳號（例如：需已存在的帳號、特定 DB 狀態）
   - **環境依賴**：測試需要的環境條件（例如：dev, test, prod env / 特定平台）
   - **優先級邏輯**：說明 High / Medium / Low 的判斷依據

   若某項目不適用，可省略，但「不測項目」若有明確排除原因，務必列出。

2. 展示初稿後，詢問使用者：

   > 以上是測試策略摘要初稿，是否有需要調整？
   > 若無問題請回覆確認，即繼續產出測試案例；
   > 若需修改，可直接複製上方摘要編輯後送出。

3. **若使用者確認** → 進入 3b
   **若使用者送回修改版** → 以修改版取代初稿，再次展示並詢問確認；確認後才進入 3b

### 3b. 正常流程（Happy Path）

Development phase與Verification phase都需要產出，但深度不同：

**Development phase**：只產出核心路徑（1–3 個），聚焦「功能是否基本可用」
- 最常見的主要操作路徑
- 必要的輸入組合（必填欄位齊全的情境）

**Verification phase**：產出完整正常流程案例
- 基本使用情境（最常見的操作路徑）
- 各種合法的輸入組合（optional fields 有/無）
- 功能完成後可觀察到的預期結果

### 3c. 邊界條件（Boundary Cases）

**僅Verification phase產出，Development phase跳過此節。**

根據功能特性，考量：
- 數值邊界（最大值、最小值、零值）
- 字串邊界（空字串、最大長度、特殊字元）
- 時間邊界（過去、現在、未來；時區差異）
- 資料量邊界（空列表、單筆、大量資料）
- 狀態邊界（資源的各種狀態轉換）

### 3d. 負面案例（Negative Cases）

Development phase與Verification phase都需要產出，但範圍不同：

**Development phase**：只產出會直接打壞主流程的關鍵情境
- 缺少必填欄位
- 未授權操作（未登入、權限不足）

**Verification phase**：產出完整負面案例
- 缺少必填欄位
- 格式/類型錯誤的輸入
- 未授權操作（未登入、權限不足）
- 資源不存在
- 重複操作（若適用，例如重複建立）
- 併發衝突（若適用）

每個案例的必填欄位請參考範本，**case_id 格式**：`<feature-slug>-<類型index>-<案例index>`，例如 `get-ownership-0-0`（正常流程第 1 個案例）。

### 3d-補. Verification phase待補清單（Development phase專用）

**僅Development phase需要執行此步驟，Verification phase跳過。**

Development phase案例產出完成後，在文件末尾附上以下待補清單，標記本次刻意跳過的測試類型，供後續Verification phase補充時參考：

- **Boundary Cases 待補**：根據此功能，列出應在Verification phase補充的邊界條件類型（例如：數值上限、空字串、狀態邊界）
- **Negative Cases 待補**：列出跳過的細節負面案例類型（例如：格式錯誤的輸入、資源不存在、重複操作）

**若使用者同時要求 Development phase 與 Verification phase：**

直接省略「Verification Phase 待補清單」章節，不需要輸出。因為 Verification phase 本身即為完整覆蓋，待補清單已無意義。

### 3d-補2. 其他測試案例固定區塊（非新增整合項目時）

**若情境為「其他」，輸出文件開頭固定加上裝置與範圍資訊，文末固定附上其他測試案例區塊：**

文件開頭：
```
**測試裝置**：{適用平台，例如 iOS / Android / Web}
**測試範圍**：{適用版本，例如 App v1.0+}
```

文件末尾：
```
其他測試案例
1. 確認是否需要驗證資料狀態
2. 確認是否需要驗證業務邏輯/計算規則
3. 確認本版釋出前後端是否需要部署
```

「其他測試案例」區塊不帶 Case ID，固定放在整份文件的最後。

**測試裝置與測試範圍的填寫規則：**
根據 AC 與 PR 改動範圍判斷：
- **測試裝置**：若改動僅影響單一平台（例如 iOS-only、Android-only 元件），只列該平台；否則列全部適用平台
- **測試範圍**：根據功能改動影響的版本或環境決定；若 AC 明確限定特定版本，只列受影響的版本

### 3e. 使用者確認

產出完成後，**將所有測試案例展示給使用者**，詢問：

> 以上是產出的手動測試案例，是否需要調整？確認後將進行輸出。

- 若使用者要求修改，更新對應案例後再次確認
- 確認無誤後，才進入 Phase 4 輸出

---

## Phase 4 — 輸出文件

### 4a. 若來源為 ClickUp Task

優先使用 **ClickUp Doc** 輸出，以支援 Markdown 渲染。

**方式一：ClickUp MCP（優先）**

依以下順序嘗試，成功即停止，失敗才往下一步：

**Step 1：官方 `claude.ai ClickUp` MCP（`mcp__claude_ai_ClickUp__`）**

直接嘗試呼叫 `mcp__claude_ai_ClickUp__clickup_create_document`：
- 成功 → 繼續用同一 MCP 執行 Step 2–4
- 工具不存在或回傳不支援錯誤 → 進入 Step 2

**Step 2：第三方 ClickUp MCP（`mcp__clickup__`，`@taazkareem/clickup-mcp-server`）**

嘗試呼叫 `mcp__clickup__create_document`：
- 成功 → 繼續用同一 MCP 執行 Step 2–4
- 回傳 premium lock 或工具不存在 → 降級至方式二

**Step 3（MCP 成功後的共同流程）**

1. 呼叫 `clickup_create_document`，標題為 `手動測試案例 — {Task 標題}`
2. 呼叫 `clickup_create_document_page`，將 Markdown 內容寫入第一頁，帶上 `content_format: "text/md"`
3. 取得 Doc 連結後，呼叫 `clickup_create_task_comment` 在原 Task 留言：
   ```
   手動測試案例已產出，請見 Doc：{Doc 連結}
   ```
4. **若 Doc 建立失敗**，降級為純文字留言：不使用 `#`、`**`、`|` 等 Markdown 語法，改用縮排與分隔線呈現，並告知使用者 Doc 建立失敗、改以留言輸出
5. 告知使用者輸出結果（Doc 連結或留言連結）

**方式二：ClickUp REST API（MCP 完全不可用時的備用）**

若 MCP 工具無法呼叫，改以 `$CLICKUP_TOKEN` 透過 REST API 執行：

1. 執行 `echo $CLICKUP_TOKEN` 與 `echo $CLICKUP_WORKSPACE_ID` 確認環境變數是否已設定：
   - **`$CLICKUP_TOKEN` 未設定**：
     1. 告知使用者前往 ClickUp → Settings → Apps → API Token 取得 token
     2. 請使用者在 shell profile（`~/.zshrc` 或 `~/.bashrc`）加入以下設定後，重新開啟 terminal 再告知你：
        ```
        export CLICKUP_TOKEN=pk_xxxxx
        ```
     3. 使用者回報設定完成後，執行 `curl -s -H "Authorization: $CLICKUP_TOKEN" "https://api.clickup.com/api/v2/team"` 取得 workspace ID（`teams[0].id`），並告知使用者將以下設定補入 shell profile：
        ```
        export CLICKUP_WORKSPACE_ID=xxxxxxxx   # 填入上方 API 回傳的 teams[0].id
        ```
     4. 請使用者執行 `source ~/.zshrc` 或 `source ~/.bashrc` 後繼續
   - **`$CLICKUP_TOKEN` 已設定但 `$CLICKUP_WORKSPACE_ID` 未設定**：
     1. 執行 `curl -s -H "Authorization: $CLICKUP_TOKEN" "https://api.clickup.com/api/v2/team"` 取得 workspace ID
     2. 告知使用者將以下設定加入 shell profile，重新開啟 terminal 後繼續：
        ```
        export CLICKUP_WORKSPACE_ID=xxxxxxxx   # 填入上方 API 回傳的 teams[0].id
        ```
2. 取得 workspace ID：讀取 `$CLICKUP_WORKSPACE_ID`
3. 建立 Doc：`POST https://api.clickup.com/api/v3/workspaces/{workspaceId}/docs`，body `{"name": "手動測試案例 — {Task 標題}"}`
4. 寫入頁面內容：**禁止用 shell heredoc 或字串展開拼接 JSON**（Markdown 含換行、backtick、引號會導致轉義錯誤）。正確做法是先用 python3 將 payload 序列化後寫入暫存檔，再以 `--data-binary @file` 送出：
   ```bash
   python3 -c "
   import json
   payload = {
       'name': '手動測試案例',
       'content': open('/path/to/test-cases.md').read(),
       'content_format': 'text/md'
   }
   open('/tmp/clickup_page_payload.json', 'w').write(json.dumps(payload))
   "
   curl -s -X POST \
     "https://api.clickup.com/api/v3/workspaces/{workspaceId}/docs/{docId}/pages" \
     -H "Authorization: $CLICKUP_TOKEN" \
     -H "Content-Type: application/json" \
     --data-binary @/tmp/clickup_page_payload.json
   ```
5. **Response 解析**：API response 的 `content` 欄位含整份文件內容（含 literal newline），直接用 `json.load` 可能因 control character 失敗。改用 regex 萃取關鍵欄位，或使用 `jq`：
   ```bash
   # regex 方式（無需 jq）
   echo "$RESPONSE" | python3 -c "
   import sys, re
   raw = sys.stdin.read()
   page_id = re.search(r'\"id\":\"([^\"]+)\"', raw)
   print('page id:', page_id.group(1) if page_id else 'FAILED')
   "
   # jq 方式（若環境有安裝）
   echo "$RESPONSE" | jq -r '.id // "error"'
   ```
6. 在原 Task 留言：`POST https://api.clickup.com/api/v2/task/{taskId}/comment`，body `{"comment_text": "手動測試案例已產出，請見 Doc：https://app.clickup.com/{workspaceId}/docs/{docId}"}`
7. 告知使用者 Doc 連結

**6. 若使用者在 Phase 1 要求同時輸出至本機**，使用 `Write` 將 Markdown 格式文件寫入指定路徑

### 4b. 若來源為直接描述

1. 依 Phase 1b-2 選擇的格式，使用對應範本結構寫入 Phase 1 指定的路徑：
   - 表格式 → 依 `templates/test-case-spec.md` 結構
   - 條列式 → 依 `templates/general-reference.md` 結構
2. 告知使用者檔案已寫入路徑，供後續編輯與上傳

---

## 注意事項

- 案例數量以**涵蓋所有有意義的情境**為準，不追求數量
- 若需求描述不夠具體（例如只說「新增功能」但無細節），Phase 2 結束前必須先補問清楚
- 每個案例的預期結果須具體描述，不能只寫「成功」或「失敗」
