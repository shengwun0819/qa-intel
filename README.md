# qa-intel

個人 QA 智慧工具集——以 AI agent 驅動的測試案例產出、風險評估與 codebase 知識管理。

設計為**可攜式個人工具**：帶著走，每家公司用 `/qa-intel:repo-scout` 建立知識庫，核心方法論不變。

→ 第一次使用？先看 [USAGE.md](USAGE.md)（一頁最小用法），完整情境見 [docs/scenarios.html](docs/scenarios.html)。

---

## 架構概覽

```
qa-intel/
├── skills/
│   ├── repo-scout/       # Skill：掃描 repo → 建立知識庫
│   ├── risk-analyzer/    # Skill：PR / branch 風險評估
│   └── gen-test-cases/   # Skill：產出手動測試案例
├── agents/
│   └── repo-reader.md    # Sub-agent：codebase 深度閱讀（repo-scout 可委派）
├── knowledge/            # 知識庫格式說明（實際資料在 ~/.qa-intel/knowledge/repos/，不在本 repo）
├── USAGE.md              # 一頁最小用法
├── docs/scenarios.html   # 使用情境完整說明
├── scripts/validate.py   # 結構與一致性檢查（CI 也會執行）
└── CLAUDE.md             # 給 Claude Code 的開發指引
```

---

## 可用 Skills

| Skill | 指令 | 說明 |
|-------|------|------|
| repo-scout | `/qa-intel:repo-scout` | 掃描 repo，建立結構化知識庫快照 |
| risk-analyzer | `/qa-intel:risk-analyzer` | 分析 PR / branch 的開發風險，可結合 ClickUp 票卡的 AC |
| gen-test-cases | `/qa-intel:gen-test-cases` | 從 task 或需求描述產出手動測試案例 |

指令名稱帶 plugin 前綴（`/qa-intel:<skill>`）。若同時安裝其他同名 skill（例如 `swiss-knife:gen-test-cases`），請一律使用帶前綴的寫法，以免呼叫到別的 skill。

---

## 安裝

本 repo 同時是一個 plugin marketplace（`.claude-plugin/marketplace.json`），可一行安裝：

```bash
claude plugin install qa-intel --marketplace shengwun0819/qa-intel
```

或分兩步：

```bash
claude plugin marketplace add shengwun0819/qa-intel
claude plugin install qa-intel@qa-intel
```

只想本機試用（不安裝）：

```bash
git clone https://github.com/shengwun0819/qa-intel
claude --plugin-dir ./qa-intel
```

> `claude plugin install` 不接受單純的 repo URL，需透過 marketplace 或 `--plugin-dir`。marketplace 安裝讀取的是 repo 預設分支上的內容。

---

## 快速開始

### Step 1：讓 qa-intel 了解你的 repo

```
/qa-intel:repo-scout
> repo 路徑：/path/to/your/repo
> 模式：comprehensive（初次建議）
```

產出：`~/.qa-intel/knowledge/repos/<repo-name>.md`（本機保存，位於 plugin 目錄之外；可用環境變數 `QA_INTEL_HOME` 改變根目錄）

### Step 2：分析開發風險（merge 前）

```
/qa-intel:risk-analyzer
> PR URL 或 branch：feat/your-feature
> Task ID：abc123（選填，有則分析 AC 覆蓋缺口）
```

### Step 3：產出測試案例

```
/qa-intel:gen-test-cases
> Task ID 或直接描述需求
> 測試階段：Development 或 Verification
```

---

## 典型工作流程

### Sprint 開始
```
/qa-intel:repo-scout（建立或更新知識庫）
```

### Feature 開發中（RD）
```
/qa-intel:risk-analyzer（branch + Task）
→ 確認實作方向是否符合 AC
→ 提早發現遺漏的邊界條件
```

### PR Review 前（QA）
```
/qa-intel:risk-analyzer（PR URL + Task）
→ 確認 AC 全部有對應實作
→ 識別需要重點測試的高風險模組
```

### 測試準備（QA）
```
/qa-intel:gen-test-cases（Task ID）
→ 產出完整 Verification phase 測試案例
→ 確認後寫成 ClickUp Doc 並在 Task 留言（目前僅支援 ClickUp，也可只輸出本機 Markdown）
```

---

## 環境需求

| 工具 | 用途 | 必要性 |
|------|------|--------|
| Claude Code CLI | 執行所有 skill | 必要 |
| `gh` CLI（已登入） | `risk-analyzer` 讀取 private PR diff | PR 分析時需要 |
| ClickUp MCP（或 `CLICKUP_TOKEN` / `CLICKUP_WORKSPACE_ID`） | gen-test-cases、risk-analyzer 讀取票卡；gen-test-cases 寫回 | 使用 ClickUp 票卡時需要；直接描述需求則不需要 |

---

## 知識庫說明

`~/.qa-intel/knowledge/repos/`（可用環境變數 `QA_INTEL_HOME` 改變根目錄）下每個 `.md` 檔案代表一個 repo 的知識快照，包含：

- Repo 概覽與定位、技術棧
- 目錄結構與各目錄職責
- 核心模組說明與 API / 介面清單
- 測試結構與覆蓋狀況
- **已知風險模組**（影響 risk-analyzer 分析重點）

知識庫是時間快照，存放在 plugin 目錄之外，因此不會進入本 repo 的 git，plugin 更新也不會覆蓋。  
repo 有重大架構調整時執行 `/qa-intel:repo-scout` 更新；舊版若把知識庫放在別處，請手動搬到上述路徑。

---

## Token 消耗參考

| 操作 | 預估 token |
|------|-----------|
| `/qa-intel:repo-scout` Comprehensive（中型 repo） | 20k – 80k |
| `/qa-intel:repo-scout` Quick | 3k – 8k |
| `/qa-intel:risk-analyzer`（有知識庫 + PR + Task） | 10k – 30k |
| `/qa-intel:gen-test-cases` Verification phase | 8k – 20k |

---

## 未來規劃

- Phase 1：輸入自動化（自動偵測當前 branch PR、從 branch 名稱萃取 Task ID）
- Phase 2：risk-analyzer → gen-test-cases 直接銜接（風險報告自動轉為測試重點）
- Phase 3：更多 Scrum Tool 支援（Jira、Linear）；目前只實作 ClickUp
- Phase 4：Integration / E2E Test 自動產出
- 可攜性：專案配置（`project.md`：PM 工具、輸出語言、裝置/範圍預設、自訂模板）與每家公司獨立的知識庫目錄，目前尚未實作

細節見 [`skills/gen-test-cases/FUTURE.md`](skills/gen-test-cases/FUTURE.md)。

---

## 開發

本 repo 只有 Markdown prompt，沒有 build 或單元測試。修改後執行：

```bash
python3 -I scripts/validate.py
```

檢查 frontmatter、agent 檔案位置、知識庫路徑一致性、步驟編號重複等；CI 會執行同一支腳本。開發指引見 [CLAUDE.md](CLAUDE.md)。
