---
name: risk-analyzer
description: 讀取 PR diff 或 branch 變更，對照知識庫（{qa-intel-root}/knowledge/repos/）評估開發風險，產出風險報告與建議測試重點。當使用者說「幫我評估這個 PR 的風險」、「這個改動有什麼風險」、「risk-analyzer」、「分析開發風險」時觸發。需先執行 /repo-scout 建立對應 repo 的知識庫。
---

# risk-analyzer

對照 codebase 知識庫，分析 PR 或 branch 的開發風險，輸出風險評估報告。

知識庫路徑：`{qa-intel-root}/knowledge/repos/`
（`{qa-intel-root}` 為 qa-intel 安裝目錄，含 `plugin.json` 的那個根目錄）

---

## 風險分類定義

| 等級 | 定義 |
|------|------|
| 🔴 High | 可能直接導致功能中斷、資料損壞、或安全問題 |
| 🟡 Medium | 可能影響部分功能或使用流程，但不至於全面中斷 |
| 🟢 Low | 小範圍影響，或已有充足測試覆蓋保護 |

---

## Phase 1 — 收集輸入

### 1a. 變更來源（必填，選其一或多個）

詢問使用者：

> 請提供變更來源（可同時提供多個，分析結果更完整）：
> - **GitHub PR URL**，例如 `github.com/org/repo/pull/123`
> - **Local branch 名稱**，例如 `feat/new-payment-flow`（需同時提供 repo path）
> - **ClickUp Task ID / URL**，例如 `abc123` 或 ClickUp 任務連結
> - **直接描述變更**，貼上 diff 或說明哪些檔案 / 模組被修改

**同時提供 PR + ClickUp Task 是最完整的輸入**：
- PR diff 告訴我們「程式碼做了什麼」
- ClickUp AC 告訴我們「應該要做什麼」
- 兩者交叉分析可找出「做了但不在 AC 裡」或「AC 要求但 diff 看不到實作」的風險

### 1b. 對應 repo（若無法從來源自動推斷）

詢問使用者此變更屬於哪個 repo（知識庫中的識別名稱，例如 `a_project`）。

自動推斷：
- GitHub PR URL → 從 URL 解析 repo 名稱
- Local branch → 請使用者提供 repo path，從 path 末段推斷
- ClickUp Task ID → branch 命名若含 task ID（如 `feat/abc123-feature`），可推斷

### 1c. 輔助背景（選填）

若使用者有額外背景可提供，可選擇：
- **相關 Slack 討論** → 直接貼入，補充設計決策

確認後進入 Phase 2。

---

## Phase 2 — 讀取變更與知識庫

### 2a. 讀取知識庫

1. 定位 qa-intel 根目錄（與 gen-test-cases Phase 0 相同方式：找含 `plugin.json` 且路徑含 `qa-intel` 的目錄）
2. 確認 `{qa-intel-root}/knowledge/repos/<repo-name>.md` 存在
3. 若不存在：告知使用者：
   > 尚未建立 `<repo-name>` 的知識庫，建議先執行 `/repo-scout` 掃描此 repo。
   > 是否仍要繼續？（將以有限資訊進行風險分析）
4. 若存在：讀取完整知識庫，注意「核心模組」與「已知風險模組」欄位

### 2b. 讀取變更 diff

**若提供 GitHub PR URL：**
- 嘗試以 `WebFetch` 讀取 `github.com/{owner}/{repo}/pull/{PR#}/files`
- 若為 private repo 或 WebFetch 失敗：
  - 若使用者也提供了 local repo path，執行 `gh pr diff <PR#>` 取得 diff
  - 否則告知使用者改提供 local repo path 或直接貼入 diff

**若提供 local branch：**
1. 在 repo 路徑下執行：
   ```bash
   git diff main...<branch> --name-only
   ```
   取得 changed files 清單
2. 執行：
   ```bash
   git diff main...<branch> --stat
   ```
   了解變更規模
3. 對高風險模組執行完整 diff：
   ```bash
   git diff main...<branch> -- <high-risk-file>
   ```

**若直接描述變更：**
直接使用使用者提供的資訊。

### 2c. 讀取 ClickUp Task（若有提供）

1. 呼叫 `clickup_get_task` 取得完整資訊，萃取：
   - **Acceptance Criteria**：列出所有明確的 AC 條件
   - **功能摘要**：這個 task 要做什麼
   - **限制條件與業務規則**：有無特定限制、不允許的情境

2. 呼叫 `clickup_get_task_comments` 讀取留言，萃取：
   - 需求補充說明、AC 追加或修改
   - 被討論或排除的情境（「這個先不做」）
   - 設計決策（「改成用 X 方式實作」）

3. 若留言中有 thread，呼叫 `clickup_get_threaded_comments` 讀取完整討論

4. 若任務包含 sub-tasks，逐一讀取各 sub-task 的 AC 與留言，了解完整範圍

**整理 ClickUp 資訊為 AC 清單**，格式如下，供 Phase 3 Dimension 8 使用：

```
AC-1: <條件描述>
AC-2: <條件描述>
...
```

### 2d. 補充讀取（選填，依需要）

若 diff 中出現知識庫未覆蓋的模組，直接讀取對應原始碼補充理解。

---

## Phase 3 — 風險分析

對照知識庫、diff 與 ClickUp AC，依以下八個維度逐一評估：

### 維度 1：API / 介面破壞性變更
- API signature 是否改變（新增必填欄位、移除欄位、改變型別）？
- 是否有 breaking change 影響下游消費者？
- GraphQL schema 是否有 breaking change？

### 維度 2：核心模組影響範圍
- 修改的模組在知識庫中的「已知風險模組」欄位是否有記載？
- 修改的是 shared utility / common module，影響面廣？
- 是否修改了 config 或初始化邏輯，影響所有依賴它的模組？

### 維度 3：測試覆蓋缺口
- 修改的模組是否有對應測試？（對照知識庫「測試結構」欄位）
- 新增的邏輯分支是否有測試覆蓋？
- 若有 regression 風險，是否有對應的 regression test？

### 維度 4：資料層風險
- 是否有 DB schema 變更（migration）？
- Migration 是否可回滾？
- 是否有 data format 或 serialization 變更影響既有資料？

### 維度 5：外部整合與依賴
- 是否修改了與第三方服務的介面（API client、webhook handler）？
- 是否升級了重要 dependency？升級範圍（patch / minor / major）？
- 是否有新增的 environment variable 需要在 deploy 前設定？

### 維度 6：平台 / 環境差異
- 是否有僅在特定平台（iOS / Android / Web）才會觸發的行為？
- 是否有需要特定 env（dev / staging / prod）才能重現的邏輯？

### 維度 7：部署時序與依賴
- 前端與後端是否需要同步部署？有無版本相容窗口？
- 是否需要先執行 migration 再部署？
- 是否需要清除 cache 或通知下游服務？

### 維度 8：AC 覆蓋缺口（僅在有提供 ClickUp Task 時執行）

對照 Phase 2c 整理的 AC 清單與 diff，逐條分析：

**AC → Code 方向（有 AC 但找不到對應實作）**：
- 每條 AC 在 diff 中是否看得到對應的程式碼變更？
- 若某條 AC 完全看不到對應改動，標記為「實作缺口」（風險：上線後該 AC 可能未被滿足）

**Code → AC 方向（有改動但不在任何 AC 裡）**：
- diff 中是否有不屬於任何 AC 的邏輯變更？
- 若有，標記為「範圍外改動」（風險：未預期的行為變更、潛在副作用）

---

## Phase 4 — 輸出風險報告

以以下結構輸出報告：

```markdown
# 風險評估報告

**Repo**：<repo-name>
**變更來源**：<PR URL 或 branch 名稱>
**ClickUp Task**：<Task ID 與標題，若有提供>
**分析日期**：<YYYY-MM-DD>

---

## 摘要

<2–3 句話：整體風險等級、最需要關注的問題>

整體風險等級：🔴 High | 🟡 Medium | 🟢 Low

---

## 風險明細

### 🔴 High 風險
（無則省略此節）

| 風險項目 | 影響範圍 | 建議行動 |
|---------|---------|---------|
| ... | ... | ... |

### 🟡 Medium 風險

| 風險項目 | 影響範圍 | 建議行動 |
|---------|---------|---------|
| ... | ... | ... |

### 🟢 Low 風險

| 風險項目 | 影響範圍 | 建議行動 |
|---------|---------|---------|
| ... | ... | ... |

---

## AC 覆蓋分析（若有提供 ClickUp Task）

| AC | 狀態 | 說明 |
|----|------|------|
| AC-1: <條件> | ✅ 有對應實作 / ⚠️ 找不到實作 | <說明> |
| AC-2: <條件> | ✅ 有對應實作 / ⚠️ 找不到實作 | <說明> |

**範圍外改動**（diff 中有但不在任何 AC 裡）：
- <檔案 / 模組>：<說明改動內容與潛在影響>

---

## 建議測試重點

（根據風險明細與 AC 缺口，列出最需要驗證的測試項目，可直接作為 /gen-test-cases 的輸入）

1. ...
2. ...

---

## 部署注意事項

（若有部署時序、migration、env var 等需要在上線前確認的事項）

- [ ] ...
- [ ] ...
```

展示報告後，詢問：

> 是否需要根據以上風險重點，直接執行 `/gen-test-cases` 產出對應的測試案例？

---

## 注意事項

- 若知識庫不存在，仍可執行分析，但需告知使用者分析品質受限
- 風險等級基於現有資訊判斷，若資訊不足請直接說明不確定性
- 「建議測試重點」應具體到可以直接作為測試案例標題，不寫籠統建議
