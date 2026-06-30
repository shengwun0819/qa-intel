---
name: repo-scout
description: 掃描指定 repository，萃取結構化知識並寫入 ~/self_project/qa-intel/knowledge/repos/<name>.md，供 risk-analyzer、gen-test-cases 等 skill 使用。支援單一與批次掃描。當使用者說「幫我掃描這個 repo」、「建立 repo 知識庫」、「讓你了解這個專案」、「repo-scout」時觸發。
---

# repo-scout

掃描 repository，將 codebase 知識結構化後寫入知識庫，作為 qa-intel 所有 skill 的共同基礎。

知識庫路徑：`~/qa-intel/knowledge/repos/`

---

## Token 預估參考

| 模式 | 適用情境 | 預估 token（單一 repo） |
|------|---------|----------------------|
| **Comprehensive** | 初次建立知識庫、中小型 repo | 20k – 80k |
| **Focused** | 更新特定模組、大型 repo | 5k – 15k |
| **Quick** | 只需架構概覽、不需深入模組 | 3k – 8k |

批次掃描（多個 repo）= 各 repo 個別 token 加總，依序執行，每個完成後才開始下一個。

---

## Phase 1 — 收集輸入

### 1a. Repo 來源（必填，支援多個）

詢問使用者：

> 請提供 repo 來源，可同時列出多個（每行一個）：
> - **Local path**，例如 `/Users/Users_Folder/Project_1/a_project`
> - **GitHub URL**，例如 `github.com/org/repo`（僅 public repo 可直接讀取）

若提供 GitHub URL 且為 private repo，告知使用者改提供 local path。

收到清單後，展示識別名稱確認表：

> 將掃描以下 repo：
> 1. `a_project`（/Users/Users_Folder/Project_1/a_project）
> 2. `b_project`（/Users/Users_Folder/Project_2/b_project
> 識別名稱有誤請告知，確認後繼續。

### 1b. 掃描模式（選填）

**若為單一 repo**，詢問掃描模式（預設 Comprehensive）：
- **Comprehensive**：完整掃描根目錄與所有核心 source 目錄，適合初次建立知識庫
- **Focused**：依 keywords 定向讀取，適合更新特定模組（選此需提供 keywords）
- **Quick**：只讀 README + 套件管理檔 + 根目錄結構，不深入 source，適合快速了解架構

**若為批次（多個 repo）**，展示 token 預估並詢問策略：

> 批次掃描預估 token 消耗較高，建議選擇：
> - **A. 第一個 Comprehensive，其餘 Quick**（推薦，適合「主要工作 repo + 相關 repo 概覽」）
> - **B. 全部 Comprehensive**（最完整，token 消耗最高）
> - **C. 全部 Quick**（最省 token，只建立基礎認識）
> - **D. 自訂**（每個 repo 分別指定模式）

### 1c. 識別名稱（選填）

預設從路徑或 URL 末段萃取（例如 `Project_1/a_project` → `a_project`）。
若使用者有偏好的識別名稱，優先使用。

確認以上資訊後進入 Phase 2。

---

## Phase 2 — 掃描 repo

**若為批次掃描**：依清單順序逐一執行 Phase 2–4，完成一個 repo 後再開始下一個。每個 repo 開始前告知進度：
> 正在掃描（1/3）：`a_project`...

**Quick 模式**：只執行 2a（跳過 2b、2c、2d），直接進入 Phase 3。

### 2a. 基礎結構讀取

1. **README**：嘗試 `README.md`、`README.rst`、`README`，讀取後了解：
   - Repo 用途與定位
   - 技術棧說明
   - 目錄結構說明（若有）
   - Setup / development guide

2. **套件管理檔**（依語言）：
   - Node.js → `package.json`、`package-lock.json`（只看 dependencies 欄位）
   - Python → `pyproject.toml`、`requirements.txt`、`setup.py`
   - Go → `go.mod`
   - Java/Kotlin → `build.gradle`、`pom.xml`
   - 多語言 repo → 全部讀取

3. **根目錄結構**：
   ```bash
   find <path> -maxdepth 1 -not -path '*/\.*' | sort
   ```
   列出所有非隱藏檔案 / 目錄，了解整體佈局。

4. **Config 檔**：尋找並讀取 `.env.example`、`config/`、`src/config.*`、`*.config.ts` 等設定檔，了解環境變數與設定結構。

### 2b. 核心模組深讀

依 2a 發現的目錄結構，讀取以下常見位置：

- `src/` 或 `lib/` 根目錄（了解主要模組分佈）
- `api/` 或 `routes/`（REST endpoints / GraphQL）
- `services/` 或 `controllers/`（業務邏輯層）
- `models/` 或 `schema/` 或 `types/`（資料模型 / 型別定義）
- `plugins/` 或 `extensions/`（若為插件架構）

**Comprehensive 模式**：每個目錄讀取 index / 入口檔與一個代表性檔案
**Focused 模式**：只讀取路徑中含有 keywords 的目錄與檔案

### 2c. 測試結構

1. 找出測試目錄（`test/`、`tests/`、`__tests__/`、`spec/`、`*.test.*`、`*.spec.*`）
2. 讀取一個 unit test 與一個 integration test 範例（若有）
3. 找出測試設定檔（`jest.config.*`、`pytest.ini`、`vitest.config.*`）
4. 估算測試覆蓋範圍（有哪些類型、覆蓋哪些模組）

### 2d. 補充文件（若存在）

依序嘗試讀取，有則讀，無則跳過：

- `CONTRIBUTING.md` / `DEVELOPMENT.md`：開發慣例
- `.github/CODEOWNERS`：模組負責人分佈
- `CHANGELOG.md`：歷史重大變更
- `ai-plans/` 或 `docs/plans/`：最近的設計決策（讀最新 3 個）
- `docs/` 根目錄：架構文件

---

## Phase 3 — 整理知識

依以下結構整理所有讀取到的資訊，產出知識摘要初稿：

```markdown
---
repo: <name>
path: <local-path 或留空>
url: <github-url 或留空>
type: local | github
last-scanned: <YYYY-MM-DD>
keywords: [<掃描用的 keywords，若 Focused 模式>]
---

# <repo-name>

## 概覽
（一到兩段：這個 repo 在做什麼、定位）

## 技術棧
- **語言**：
- **框架**：
- **資料庫 / 儲存**：
- **主要依賴**：

## 目錄結構
（根目錄一層，每行說明職責）

## 核心模組
（3–7 個最重要的模組，說明職責與入口檔路徑）

## API / 介面
（主要 endpoints / MCP tools / CLI 指令；無則說明）

## 測試結構
- **框架**：
- **測試目錄**：
- **覆蓋概況**：

## 關鍵慣例與注意事項
（命名慣例、設計決策、注意事項）

## 已知風險模組
（根據掃描判斷哪些模組邏輯複雜、測試薄弱、或歷史問題多）
```

將初稿展示給使用者，詢問：

> 以上是 `<repo-name>` 的知識摘要，是否需要補充或修正？
> 確認後將寫入知識庫。

- 若使用者確認或無異議 → 進入 Phase 4
- 若使用者提出修正 → 更新後再次確認

---

## Phase 4 — 寫入知識庫

1. 確認 `~/self_project/qa-intel/knowledge/repos/` 目錄存在；若無則建立
2. 若 `<repo-name>.md` 已存在，告知使用者：
   > `<repo-name>.md` 已存在（上次掃描：<date>），將以本次結果覆蓋。
3. 使用 `Write` 將 Phase 3 產出寫入 `~/self_project/qa-intel/knowledge/repos/<repo-name>.md`
4. 告知使用者：
   > ✓ 知識庫已建立：`~/self_project/qa-intel/knowledge/repos/<repo-name>.md`
   >
   > 現在可以使用：
   > - `/risk-analyzer` — 分析 PR 或 branch 的開發風險
   > - `/gen-test-cases` — 產出測試案例時自動讀取此知識庫補充背景

---

## Phase 4 補充 — 批次掃描完成摘要

若為批次掃描，所有 repo 完成後輸出整體摘要：

> ✓ 批次掃描完成，共建立 N 個知識庫：
>
> | Repo | 模式 | 狀態 |
> |------|------|------|
> | a_project | Comprehensive | ✓ 已建立 |
> | b_project | Quick | ✓ 已建立 |
>
> 可執行：
> - `/risk-analyzer` — 分析 PR 風險（會自動選取對應 repo 的知識庫）
> - `/gen-test-cases` — 產出測試案例（自動補充 codebase 背景）

---

## 注意事項

- 若 repo 規模非常大（例如 monorepo 含數十個套件），先讀取頂層結構，詢問使用者要深入哪幾個套件
- 若讀取過程中遭遇權限錯誤，告知使用者並跳過該路徑
- 任何無法確認的欄位，標記為「無法確認」，不自行假設
- 批次掃描建議在 context 相對乾淨時執行（session 剛開始），避免 context 已滿時 token 不足完成全部掃描
